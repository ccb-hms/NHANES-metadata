library(nhanesA)
library(progress)

# Get metadata about NHANES tables from all survey years and data groups.
get_tables_metadata <- function() {
  data_groups <- c("DEMOGRAPHICS", "DIETARY", "EXAMINATION", "LABORATORY", "QUESTIONNAIRE")
  survey_years <- c(1999, 2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017)
  all_tables <- data.frame(matrix(ncol=6, nrow = 0))
  for (year in survey_years) {
    for (data_group in data_groups) {
      tables_year <- get_tables(data_group=data_group, year=year)
      all_tables <- rbind(all_tables, tables_year)
    }
  }
  colnames(all_tables) <-c("Table", "TableName", "BeginYear", "EndYear", "DataGroup", "UseConstraints", "DocFile", "DataFile", "DatePublished")
  return(all_tables)
}

get_tables <- function(data_group, year) {
  tables <- nhanesTables(data_group=data_group, year=year, details=TRUE, includerdc=TRUE)
  if(year=='P') {
    # Pre-pandemic (2019-) tables have different header names that need renaming
    colnames(tables)[colnames(tables)=="Data.File.Name"] = "Data.File.Description"
    colnames(tables)[colnames(tables)=="Doc.File"] = "Data.File.Name"
  }
  tables$DocFile <- ""
  tables$DataFile <- ""
  tables$DatePublished <- ""
  for (i in 1:nrow(tables)) {
    table_name <- tables$Data.File.Name[i]
    search_pattern <- paste("\\b", table_name, "\\b", sep="")
    table_details <- nhanesSearchTableNames(search_pattern, includerdc=TRUE, details=TRUE)
    if(!is.null(table_details)) {
      tables$DocFile[i] <- paste0(nhanesA:::nhanesURL, table_details$Years, "/", 
                                  sapply(strsplit(table_name, " "), function(x) x[[1]]), ".htm")
      tables$DataFile[i] <- paste0(nhanesA:::nhanesURL, table_details$Years, "/", 
                                   sapply(strsplit(table_name, " "), function(x) x[[1]]), ".XPT")
      tables$DatePublished[i] <- table_details[["Date.Published"]]
    }
  }
  return(tables)
}

# Get metadata about all variables in the given collection of NHANES tables.
get_variables_metadata <- function(tables) {
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
  
  # Get all variables in the specified table
  # Note: the data groups in the data frame returned by nhanesTables() function
  #   are in lower case, but the nhanesTableVars() function argument `data_group`
  #   is case-sensitive and only accepts upper-case data group names
  table_variables <- nhanesTableVars(data_group=toupper(nhanes_data_group), 
                                     nh_table=table_name, details=TRUE, 
                                     nchar=1024, namesonly=FALSE)
  
  # For each variable in this table get its details
  if(length(table_variables) > 0) {
    for (variable in 1:nrow(table_variables)) {
      variable_name <- table_variables[variable, 'Variable.Name']
      use_constraints <- table_variables[variable, 'Use.Constraints']
      if(variable_name != "SEQN") {
        tryCatch({
          variable_details <- nhanesCodebook(nh_table=table_name, colname=variable_name)
          if(!is.null(variable_details)) {
            label <- clean(variable_details['SAS Label:'][[1]])
            text <- clean(variable_details['English Text:'][[1]])
            targets <- ""
            for (i in seq_along(variable_details)) {
              if (names(variable_details[i])=='Target:') {
                target <- clean(variable_details[[i]])
                if(targets == "") {
                  targets <- target
                }
                else {
                  targets <- paste(targets, target, sep = " *AND* ")
                }
              }
            }
            variable_details_vector <- c(variable_name, table_name, label, text, targets, use_constraints)
            all_variables[nrow(all_variables) + 1, ] <- variable_details_vector
            variable_codebook <- variable_details[variable_name][[1]]
            variable_codebook[["Value Description"]] <- clean(variable_codebook[["Value Description"]])
            names(variable_codebook)[names(variable_codebook) == 'Value Description'] <- 'ValueDescription'
            variable_codebook <- cbind('Table'=table_name, variable_codebook)
            variable_codebook <- cbind('Variable'=variable_name, variable_codebook)
            all_variable_codebooks <- rbind(all_variable_codebooks, variable_codebook)
          }
          else {
            log_missing_codebook("Warning", "Codebook does not exist for this variable", table_name=table_name, variable_name=variable_name)
          }
        }, error=function(e) {
          log_missing_codebook("ERROR", conditionMessage(e), table_name=table_name, variable_name=variable_name)
        }, warning=function(w) {
          log_missing_codebook("WARNING", conditionMessage(w), table_name=table_name, variable_name=variable_name)
        })
      }
    }
  } else {
    print(paste("Warning: nhanesA::nhanesTableVars() returns 0 variables in table ", table_name))
  } 
  return(list(all_variables, all_variable_codebooks))
}

log_missing_codebook <- function(exception_type, exception_msg, table_name, variable_name) {
  log_msg <- paste(exception_type, ": ", exception_msg, " (Table-Variable: ", 
                   table_name, "-", variable_name, ")", sep="")
  cat(log_msg, "\n", file=log_file, append=TRUE)
  cat(table_name, "\t", variable_name, "\n", 
      file=missing_codebooks_file, append=TRUE)
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
write.table(all_tables, file=paste(output_folder, "nhanes_tables.tsv", sep=""), 
            row.names=FALSE, sep="\t", na="")

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
