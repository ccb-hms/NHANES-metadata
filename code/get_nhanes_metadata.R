install.packages("devtools")
devtools::install_github("cjendres1/nhanes")
library(nhanesA)
library(progress)

nhanes_tables_metadata_column_names <- c("Table", "TableName", "BeginYear", "EndYear", "DataGroup", 
                                         "UseConstraints", "DocFile", "DataFile", "DatePublished")

# Get metadata about NHANES tables from all survey years and data groups.
get_tables_metadata <- function() {
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
  write.table(all_tables, file=paste(output_folder, "nhanes_tables.tsv", sep=""),
              row.names=FALSE, sep="\t", na="")
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
    tables_metadata$DocFile[i] <- paste0(nhanesA:::nhanesURL, url_years, "/", 
                                         sapply(strsplit(table_id, " "), function(x) x[[1]]), ".htm")
    tables_metadata$DataFile[i] <- paste0(nhanesA:::nhanesURL, url_years, "/", 
                                          sapply(strsplit(table_id, " "), function(x) x[[1]]), ".XPT")
    if(year == "P") {
      tables_metadata$DatePublished[i] <- tables$Date.Published[i]
    } else {
      search_pattern <- paste0("\\b", table_id, "\\b")
      table_details <- nhanesSearchTableNames(search_pattern, includerdc=TRUE, details=TRUE, includewithdrawn=TRUE)
      if(!is.null(table_details)) {
        tables_metadata$DatePublished[i] <- table_details[["Date.Published"]]
      }
    }
  }
  return(tables_metadata)
}

# Get metadata about all variables in the given collection of NHANES tables.
get_variables_metadata <- function(tables) {
  print("Extracting variables metadata...")
  # Write a table containing metadata about all variables
  all_variables <- data.frame(matrix(ncol=6, nrow = 0))
  colnames(all_variables) <-c("Variable", "Table", "SASLabel", "EnglishText", "Target", "UseConstraints")
  variables_metadata_file <- paste(output_folder, "nhanes_variables.tsv", sep="")
  write.table(all_variables, file=variables_metadata_file, row.names=FALSE, sep="\t", na="")
  
  # Write a table containing the codebooks of all variables
  all_codebooks <- data.frame(matrix(ncol=7, nrow = 0))
  variables_codebooks_file <- paste(output_folder, "nhanes_variables_codebooks.tsv", sep="")
  colnames(all_codebooks) <-c("Variable", "Table", "CodeOrValue", "ValueDescription", 
                              "Count", "Cumulative", "SkipToItem")
  write.table(all_codebooks, file=variables_codebooks_file, row.names=FALSE, na="", sep="\t")
  pb <- progress_bar$new(total = nrow(tables))
  for (nhanes_table in 1:nrow(tables)) {
    pb$tick()
    table_name <- tables[nhanes_table, "Table"]
    data_group <- tables[nhanes_table, "DataGroup"]
    variable_details <- get_variables_in_table(table_name=table_name, 
                                               nhanes_data_group=data_group)
    if(length(variable_details) > 0) {
      table_variables <- variable_details[[1]]
      write.table(table_variables, file=variables_metadata_file, sep="\t", na="",
                  append=TRUE, col.names=FALSE, row.names=FALSE)
      table_codebooks <- variable_details[[2]]
      tryCatch({
        write.table(table_codebooks, file=variables_codebooks_file, sep="\t", na="",
                    append=TRUE, col.names=FALSE, row.names=FALSE)
      }, 
      error=function(e) {
        print(paste("Error writing out table: ", table_name))
        print(conditionMessage(e))
      })
    }
    else {
      log_missing_codebook("Warning", "get_nhanes_metadata::get_variables_in_table() returns 0 items", 
                           table_name=table_name, variable_name="")
    }
  }
}

# Get metadata about the variables in the given NHANES table (specified by the table name) and data group.
get_variables_in_table <- function(table_name, nhanes_data_group) {
  all_variables <- data.frame(matrix(ncol=6, nrow=0))
  all_variable_codebooks <- data.frame(matrix(ncol=7, nrow=0))
  table_codebooks = {}
  tryCatch({
    table_codebooks <- nhanesCodebook(nh_table=table_name)
  },
  error=function(msg) {
    log_missing_codebook("Error in nhanesA::nhanesCodebook()", conditionMessage(msg), table_name=table_name, variable_name="")
  }, warning=function(msg) {
    log_missing_codebook("Warning in nhanesA::nhanesCodebook()", conditionMessage(msg), table_name=table_name, variable_name="")
  })

  # Get all variables in the specified table
  # Note: the data groups in the data frame returned by nhanesTables() function
  #   are in lower case, but the nhanesTableVars() function argument `data_group`
  #   is case-sensitive and only accepts upper-case data group names
  tryCatch({
    table_variables <- nhanesTableVars(data_group=toupper(nhanes_data_group), 
                                       nh_table=table_name, details=TRUE, 
                                       nchar=1024, namesonly=FALSE)
    # For each variable in this table get its details
    if(length(table_variables) > 0) {
      for (variable in 1:nrow(table_variables)) {
        variable_name <- table_variables[variable, 'Variable.Name']
        use_constraints <- table_variables[variable, 'Use.Constraints']
        tryCatch({
          variable_details <- table_codebooks[variable_name][[1]]
          if (!is.null(variable_details)) {
            label <- clean(variable_details['SAS Label:'][[1]])
            text <- clean(variable_details['English Text:'][[1]])
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
            variable_details_vector <- c(variable_name, table_name, label, text, targets, use_constraints)
            all_variables[nrow(all_variables) + 1, ] <- variable_details_vector
            variable_codebook <- variable_details[variable_name][[1]]
            if (!is.null(variable_codebook)) {
              if (variable_name != "SEQN" && variable_name != "SAMPLEID") {
                if(length(variable_codebook) == 0) {
                  print(paste("Variable codebook list for variable", variable_name, "in table", table_name, " is empty"))
                }
                if ("Value Description" %in% names(variable_codebook) && !is.null(variable_codebook[["Value Description"]])) {
                  variable_codebook[["Value Description"]] <- clean(variable_codebook[["Value Description"]])
                } else {
                  variable_codebook[["Value Description"]] <- ""
                }
                names(variable_codebook)[names(variable_codebook) == 'Value Description'] <- 'ValueDescription'
                variable_codebook <- cbind('Table'=table_name, variable_codebook)
                variable_codebook <- cbind('Variable'=variable_name, variable_codebook)
                all_variable_codebooks <- rbind(all_variable_codebooks, variable_codebook)
              }
            } else {
              log_missing_codebook("Warning", "Null codebook for this variable", table_name = table_name, variable_name = variable_name)
            }
          } else {
            if (variable_name != "SEQN" && variable_name != "SAMPLEID") {
              log_missing_codebook("Warning", "nhanesA::nhanesCodebook() does not return a codebook for this variable", table_name = table_name, variable_name = variable_name)
            }
          }
        }, error=function(e) {
          log_missing_codebook("ERROR", conditionMessage(e), table_name=table_name, variable_name=variable_name)
        }, warning=function(w) {
          log_missing_codebook("WARNING", conditionMessage(w), table_name=table_name, variable_name=variable_name)
        })
      }
    } else {
      print(paste("Warning: nhanesA::nhanesTableVars() returns 0 variables in table ", table_name))
    }
  }, error=function(msg) {
    print(paste("Error in nhanesA::nhanesTableVars():", conditionMessage(msg)))
  }, warning=function(msg) {
    print(paste("Warning in nhanesA::nhanesTableVars():", conditionMessage(msg)))
  })
  return(list(all_variables, all_variable_codebooks))
}

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

# Get the metadata about the tables and the variables in NHANES surveys 1999-2017.
output_folder <- "../metadata/"
dir.create(file.path(".", output_folder), showWarnings=FALSE, recursive=TRUE)
log_file <- paste(output_folder, "log.txt", sep="")
missing_codebooks_file <- paste(output_folder, "missing_codebooks.tsv", sep="")

# Get the metadata about all NHANES tables.
start_tbls = proc.time()
all_tables <- get_tables_metadata()
diff_tbls <- proc.time() - start_tbls
print(paste("Tables metadata acquired in ", diff_tbls[3][["elapsed"]], " seconds"))

# Get metadata about all variables in all NHANES tables collected above.
start_vars = proc.time()
get_variables_metadata(all_tables)
diff <- proc.time() - start_vars
print(paste("Variables metadata acquired in ", diff[3][["elapsed"]], " seconds"))

# Write out to log file the date when metadata finished downloading
cat(paste("Downloaded on:", format(Sys.time(), format="%m-%d-%YT%H:%M:%S")), file=log_file, append=TRUE)
print("finished")
