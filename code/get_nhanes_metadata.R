install.packages("devtools")
devtools::install_github("cjendres1/nhanes")
library(nhanesA)
library(progress)
library(rvest)
library(dplyr)


nhanes_tables_metadata_column_names <- c("Table", "TableName", "BeginYear", "EndYear", "DataGroup", 
                                         "UseConstraints", "DocFile", "DataFile", "DatePublished")


## NHANES TABLES METADATA ACQUISITION FUNCTIONS ##

# Get metadata about NHANES tables from all survey years and data groups.
get_tables_metadata <- function(use_manifest) {
  print("Extracting tables metadata...")
  data_groups <- c("Demographics", "Dietary", "Examination", "Laboratory", "Questionnaire")
  survey_years <- c(1999, 2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, "P")
  all_tables <- data.frame(matrix(ncol=9, nrow = 0))
  pb <- progress_bar$new(total = length(survey_years))
  for (year in survey_years) {
    pb$tick()
    for (data_group in data_groups) {
      tables_year <- get_tables(data_group=data_group, year=year)
      all_tables <- rbind(all_tables, tables_year)
    }
  }
  colnames(all_tables) <- nhanes_tables_metadata_column_names
  if (use_manifest) {
    all_tables <- add_tables_from_manifest(all_tables)
  }
  all_tables_copy <- all_tables
  all_tables_copy$Table <- toupper(all_tables_copy$Table)  # Ensure Table IDs are capitalized (#20)
  write.table(all_tables_copy, file=paste(output_folder, "nhanes_tables.tsv", sep=""), row.names=FALSE, sep="\t", na="")
  return(all_tables)
}

get_tables <- function(data_group, year) {
  tables <- nhanesTables(data_group=toupper(data_group), year=year, details=TRUE, includerdc=TRUE)
  tables_metadata <- data.frame(matrix(ncol=9, nrow = nrow(tables)))
  colnames(tables_metadata) <- nhanes_tables_metadata_column_names
  for (i in 1:nrow(tables)) {
    # Get the (unique) table identifier
    table_id <- tables$Data.File.Name[i]
    if(year=="P") {
      table_id <- sub(" Doc", "", tables$Doc.File[i])
    }
    tables_metadata$Table[i] <- table_id
    
    # Get the table name (aka description)
    table_name <- ""
    if(year == "P") {
      table_name <- tables$Data.File.Name[i]
    } else {
      table_name <- tables$Data.File.Description[i]
    }
    tables_metadata$TableName[i] <- table_name
    
    # Get the start and end years of the survey
    if(year=="P") {
      survey_years <- strsplit(tables$Years[i], "-")[[1]]
      tables_metadata$BeginYear[i] <- survey_years[1]
      tables_metadata$EndYear[i] <- survey_years[2]
      url_years <- "2017-2018"
    } else {
      tables_metadata$BeginYear[i] <- tables$Begin.Year[i]
      tables_metadata$EndYear[i] <- tables$EndYear[i]
      url_years <- paste0(tables_metadata$BeginYear[i], "-", tables_metadata$EndYear[i])
    }
    tables_metadata$DataGroup[i] <- data_group
    if(year != "P") {
      tables_metadata$UseConstraints[i] <- tables$Use.Constraints[i]
    }
    # TODO: URLs for limited-access tables are currently missing the /limited_access/ bit
    tables_metadata$DocFile[i] <- paste0(nhanesA:::nhanesURL, url_years, "/", sapply(strsplit(table_id, " "), function(x) x[[1]]), ".htm")
    tables_metadata$DataFile[i] <- paste0(nhanesA:::nhanesURL, url_years, "/", sapply(strsplit(table_id, " "), function(x) x[[1]]), ".XPT")
    if(year == "P") {
      tables_metadata$DatePublished[i] <- tables$Date.Published[i]
    }
  }
  return(tables_metadata)
}

# Add tables to the nhanes_tables_metadata data frame that are reported 
# in nhanesA::nhanesManifest() but not obtainable via nhanesA::nhanesTables()
add_tables_from_manifest <- function(nhanes_tables) {
  manifest_variables <- nhanesManifest(which="variables")
  # nhanes_tables$Table <- toupper(nhanes_tables$Table)
  
  manifest_public <- nhanesManifest(which="public")
  nhanes_tables_new <- add_manifest(manifest_public, nhanes_tables, "None", manifest_variables)
  
  manifest_limitedaccess <- nhanesManifest(which="limitedaccess")
  nhanes_tables_newer <- add_manifest(manifest_limitedaccess, nhanes_tables_new, "RDC Only", manifest_variables)
  
  nhanes_tables_newer$UseConstraints[is.na(nhanes_tables_newer$UseConstraints)] <- "None"
  return(nhanes_tables_newer)
}

add_manifest <- function(manifest, nhanes_tables, use_constraints, manifest_variables) {
  colnames(manifest)[colnames(manifest) == "Date.Published"] <- "DatePublished"
  
  # Check if each table in the 'manifest' is in the 'nhanes_tables_metadata' table
  missing_entries <- manifest$Table[!(manifest$Table %in% toupper(nhanes_tables$Table))]
  
  for (missing_table in missing_entries) {
    if(missing_table != "All Years") {
      table_to_add <- manifest[manifest$Table == missing_table, ]
      doc_url <- paste0("https://wwwn.cdc.gov", table_to_add$DocURL)
      data_file_url <- paste0("https://wwwn.cdc.gov", table_to_add$DataURL)
      date_published <- table_to_add$DatePublished
      survey_years <- strsplit(manifest$Years, "-")[[1]]
      begin_year <- survey_years[1]
      end_year <- survey_years[2]
      
      subset <- manifest_variables[manifest_variables$Table == missing_table, ]
      
      # nhanesManifest(which="public" or "limitedaccess") do not include table names or components, 
      # but these details can be obtained from the variables manifest nhanesManifest(which="variables")
      data_group <- subset$Component[1]
      table_name <- subset$TableDesc[1]
      
      if(is.na(table_name)) {
        print(paste("nhanesA::nhanesManifest() does not contain a table name for ", missing_table, ". Scraping from documentation webpage..."))
        webpage <- read_html(doc_url)
        h3_text <- webpage %>% html_nodes("#PageHeader h3") %>% html_text()
        split_string <- strsplit(h3_text, "\\(")
        table_name <- ""
        tryCatch({
          table_name <- split_string[[1]][1]
        },
        error=function(e) {
          print(paste("Error scraping the name of the table: ", missing_table, "(h3text: ", h3_text, ")"))
          print(conditionMessage(e))
        })
      }
      if(is.na(data_group)) {
        print(paste("nhanesA::nhanesManifest() does not contain a data group for ", missing_table))
        if(missing_table %in% c("DOC_2000", "PAX80_G_R", "PAXLUX_G_R", "DRXFMT", "DRXFMT_B", 
                               "FOODLK_C", "FOODLK_D", "VARLK_C", "VARLK_D")) {
          data_group <- "Documentation"
        } 
        else if(missing_table == "DRXFCD_I" || missing_table == "DRXFCD_J") {
          data_group <- "Dietary"
        }
        else if(missing_table %in% c("POOLTF_D", "POOLTF_E", "PFC_POOL")) {
          data_group <- "Laboratory"
        }
        else if(missing_table == "YDQ") {
          data_group <- "Questionnaire"
        }
      }
      new_row <- data.frame(Table=missing_table, TableName=table_name, BeginYear=begin_year, EndYear=end_year, DataGroup=data_group,
                            UseConstraints=use_constraints, DocFile=doc_url, DataFile=data_file_url, DatePublished=date_published)
      nhanes_tables <- rbind(nhanes_tables, new_row)
    }
  }
  merged_nhanes_tables <- merge(nhanes_tables, manifest[, c("Table", "DatePublished")], by = "Table", all.x = TRUE, suffixes = c("", ".manifest"))
  merged_nhanes_tables$DatePublished[is.na(merged_nhanes_tables$DatePublished)] <- merged_nhanes_tables$DatePublished.manifest[is.na(merged_nhanes_tables$DatePublished)]
  merged_nhanes_tables$DatePublished.manifest <- NULL
  return(merged_nhanes_tables)
}


## VARIABLE METADATA ACQUISITION FUNCTIONS ##

# Get metadata about all variables in the given collection of NHANES tables.
get_variables_metadata <- function(tables) {
  print("Extracting variables metadata...")
  # Write a table containing metadata about all variables
  all_variables <- data.frame(matrix(ncol=7, nrow = 0))
  colnames(all_variables) <-c("Variable", "Table", "SASLabel", "EnglishText", "EnglishInstructions", "Target", "UseConstraints")
  variables_metadata_file <- paste(output_folder, "nhanes_variables.tsv", sep="")
  write.table(all_variables, file=variables_metadata_file, row.names=FALSE, sep="\t", na="")
  
  # Write a table containing the codebooks of all variables
  all_codebooks <- data.frame(matrix(ncol=7, nrow = 0))
  variables_codebooks_file <- paste(output_folder, "nhanes_variables_codebooks.tsv", sep="")
  colnames(all_codebooks) <-c("Variable", "Table", "CodeOrValue", "ValueDescription", "Count", "Cumulative", "SkipToItem")
  write.table(all_codebooks, file=variables_codebooks_file, row.names=FALSE, na="", sep="\t")
  pb <- progress_bar$new(total = nrow(tables))
  for (nhanes_table in 1:nrow(tables)) {
    pb$tick()
    table_name <- tables[nhanes_table, "Table"]
    data_group <- tables[nhanes_table, "DataGroup"]
    variable_details <- get_variables_in_table(table_name=table_name, nhanes_data_group=data_group)
    if(length(variable_details) > 0) {
      table_variables <- variable_details[[1]]
      write.table(table_variables, file=variables_metadata_file, sep="\t", na="", append=TRUE, col.names=FALSE, row.names=FALSE)
      table_codebooks <- variable_details[[2]]
      tryCatch({
        write.table(table_codebooks, file=variables_codebooks_file, sep="\t", na="", append=TRUE, col.names=FALSE, row.names=FALSE)
      }, 
      error=function(e) {
        print(paste("Error writing out table: ", table_name, ":", conditionMessage(e)))
      })
    }
    else {
      log_missing_codebook("Warning", "get_nhanes_metadata::get_variables_in_table() returns 0 items", table_name=table_name, variable_name="")
    }
  }
}

# Get metadata about the variables in the given NHANES table (specified by the table name) and data group.
get_variables_in_table <- function(table_name, nhanes_data_group) {
  all_variables <- data.frame(matrix(ncol=7, nrow=0))
  all_variable_codebooks <- data.frame(matrix(ncol=7, nrow=0))
  table_codebooks = {}
  tryCatch({
    table_codebooks <- nhanesCodebook(nh_table=table_name)
  }, error=function(msg) {
    log_missing_codebook("Error in nhanesA::nhanesCodebook()", conditionMessage(msg), table_name=table_name, variable_name="")
  }, warning=function(msg) {
    log_missing_codebook("Warning in nhanesA::nhanesCodebook()", conditionMessage(msg), table_name=table_name, variable_name="")
  })
  
  if(is.null(table_codebooks)) {
    print(paste("nhanesA::nhanesCodebook() returns NULL for table ", table_name))
    return(list())
  } 
  else {
    table_variables <- {}
    # Note: the data groups in the data frame returned by nhanesA::nhanesTables() are in lower case, but 
    # the nhanesA::nhanesTableVars() argument `data_group` only accepts upper-case data group names
    tryCatch({
      table_variables <- nhanesTableVars(data_group=toupper(nhanes_data_group), nh_table=table_name, details=TRUE, nchar=1024, namesonly=FALSE)
      if(length(table_variables) == 0) {
        print(paste("nhanesA::nhanesTableVars() returns 0 variables for table ", table_name))
      } else {
        # Remove duplicate rows for the same variable
        table_variables <- table_variables %>% distinct(Variable.Name, .keep_all = TRUE)
      }
    }, error=function(msg) {
      print(paste("Error in nhanesA::nhanesTableVars() on table", table_name, ":", conditionMessage(msg)))
    }, warning=function(msg) {
      print(paste("Warning in nhanesA::nhanesTableVars() on table", table_name, ":", conditionMessage(msg)))
    })
    
    for (i in 1:length(table_codebooks)) {
      variable <- table_codebooks[[i]]
      variable_name <- variable['Variable Name:'][[1]]
      variable_details <- table_codebooks[variable_name][[1]]
      if (!is.null(variable_details)) {
        label <- clean(variable_details['SAS Label:'][[1]])
        text <- clean(variable_details['English Text:'][[1]])
        instructions <- variable_details['English Instructions:'][[1]]
        if(is.null(instructions) || all(is.na(instructions))) {
          instructions <- ""
        } else {
          instructions <- clean(instructions)
        }
        targets <- ""
        for (i in seq_along(variable_details)) {
          if ('Target:' %in% names(variable_details[i])) {
            target <- clean(variable_details[[i]])
            if (targets == "") {
              targets <- target
            } else {
              targets <- paste(targets, target, sep = " *AND* ")
            }
          }
        }
        use_constraints <- ""
        if(length(table_variables) > 0) {
          use_constraints <- table_variables[variable_name, 'Use.Constraints']
        }
        variable_details_vector <- c(toupper(variable_name), toupper(table_name), label, text, instructions, targets, use_constraints)
        all_variables[nrow(all_variables) + 1, ] <- variable_details_vector
        variable_codebook <- variable_details[variable_name][[1]]
        if (!is.null(variable_codebook)) {
          if (!all(is.na(variable_codebook))) {
            if (variable_name != "SEQN" && variable_name != "SAMPLEID") {
              if (length(variable_codebook) == 0) {
                print(paste("Variable codebook list for variable", variable_name, "in table", table_name, " is empty"))
              }
              if ("Value Description" %in% names(variable_codebook) && !is.null(variable_codebook[["Value Description"]])) {
                variable_codebook[["Value Description"]] <- clean(variable_codebook[["Value Description"]])
              } else {
                variable_codebook[["Value Description"]] <- ""
              }
              names(variable_codebook)[names(variable_codebook) == 'Value Description'] <- 'ValueDescription'
              # Make sure NA values are included in the output table
              variable_codebook$`Code or Value`[is.na(variable_codebook$`Code or Value`)] <- "NA"
              variable_codebook$ValueDescription[is.na(variable_codebook$ValueDescription)] <- "NA"
              variable_codebook <- cbind('Table'=table_name, variable_codebook)
              variable_codebook <- cbind('Variable'=variable_name, variable_codebook)
              variable_codebook$Table <- toupper(variable_codebook$Table)  # Ensure Variable and Table IDs are capitalized (#20)
              variable_codebook$Variable <- toupper(variable_codebook$Variable)
              all_variable_codebooks <- rbind(all_variable_codebooks, variable_codebook)
            }
          }
        } else {
          if (variable_name != "SEQN" && variable_name != "SAMPLEID") {
            log_missing_codebook("Warning", "Null or NA codebook for this variable", table_name = table_name, variable_name = variable_name)
          }
        }
      } else {
        if (!is.null(variable_name) && variable_name != "SEQN" && variable_name != "SAMPLEID") {
          log_missing_codebook("Warning", "nhanesA::nhanesCodebook() does not return a codebook for this variable", 
                               table_name = table_name, variable_name = variable_name)
        }
      }
    }
    return(list(all_variables, all_variable_codebooks))
  }
}


## UTILITY FUNCTIONS ##
log_missing_codebook <- function(exception_type, exception_msg, table_name, variable_name) {
  log_msg <- paste(exception_type, ": ", exception_msg, " (Table-Variable: ", 
                   table_name, "-", variable_name, ")", sep="")
  cat(log_msg, "\n", file=log_file, append=TRUE)
  cat(table_name, "\t", variable_name, "\n", file=missing_codebooks_file, append=TRUE)
  print(log_msg)
}

# Remove carriage return, new line, comma, backslash and quote characters
clean <- function(text) {
  text <- gsub("[\r\n,\\\"]", "", text)
  return(text)
}


## GET TABLE METADATA ##

# Get the metadata about the tables and the variables in NHANES surveys 1999-2017.
output_folder <- "../metadata/"
dir.create(file.path(".", output_folder), showWarnings=FALSE, recursive=TRUE)
log_file <- paste(output_folder, "log.txt", sep="")
missing_codebooks_file <- paste(output_folder, "missing_codebooks.tsv", sep="")

# Get the metadata about all NHANES tables.
start_tbls = proc.time()
all_tables <- get_tables_metadata(use_manifest=TRUE)
diff_tbls <- proc.time() - start_tbls
print(paste("Tables metadata acquired in ", diff_tbls[3][["elapsed"]], " seconds"))


## GET VARIABLE METADATA ##

# Get metadata about all variables in all NHANES tables collected above.
start_vars = proc.time()
get_variables_metadata(all_tables)
diff <- proc.time() - start_vars
print(paste("Variables metadata acquired in ", diff[3][["elapsed"]], " seconds"))

# Write out to log file the date when metadata finished downloading
cat(paste("Downloaded on:", format(Sys.time(), format="%m-%d-%YT%H:%M:%S")), file=log_file, append=TRUE)
print("finished")
