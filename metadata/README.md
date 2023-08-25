This folder contains NHANES metadata tables extracted via [code/get_nhanes_metadata.Rmd](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/get_nhanes_metadata.Rmd), using the [nhanesA](https://github.com/cjendres1/nhanes) package.

## nhanes_tables.tsv

| Table | TableName | BeginYear | EndYear | DataGroup | UseConstraints | DocFile | DataFile | DatePublished |
|-------|-----------|-----------|---------|-----------|----------------|---------|----------|---------------|

- `Table` contains table identifiers, e.g., `BPX_I`.
- `TableName` contains table names, e.g., `Blood Pressure`.
- `BeginYear` and `EndYear` provide the start and end years of the survey/table.
- `DocFile` and `DataFile` provide the URLs to the documentation webpage and the data file, respectively.
- `DatePublished` provides the date of update or publishing of the table. 


## nhanes_variables.tsv

| Variable | Table | SASLabel | EnglishText | Target | UseConstraints | ProcessedText | Tags | VariableID | OntologyMapped |
|----------|-------|----------|-------------|--------|----------------|---------------|------|------------|----------------|

- `Variable` contains variable identifiers, e.g., `PEASCCT1`.
- `Table` contains table identifiers, e.g., `BPX_I`.
- `SASLabel` contains variable labels, e.g., `Blood Pressure Comment`.
- `ProcessedText` contains the processed label, e.g., `Blood Pressure`.
- `Tags` contains the tags attached to the variable during preprocessing, e.g., `comment`.
- `VariableID` contains unique identifiers formed by combining variable and table IDs separated by `-` e.g. `PEASCCT1-BPX_I`.  
- `OntologyMapped` specifies if a variable has been mapped to an ontology. 


## nhanes_variables_codebooks.tsv 
contains _**variable codebooks**_ which specify possible responses to questions (represented by the variables).

| Variable | Table | CodeOrValue | ValueDescription | Count | Cumulative | SkipToItem |
|----------|-------|-------------|------------------|-------|------------|------------|

Similar to `nhanes_variables.tsv`:
- `Variable` contains variable identifiers.
- `Table` contains table identifiers.


## missing_codebooks.tsv
contains variables that are listed by `nhanesTableVars()` but that do not have a corresponding codebook obtainable via the `nhanesCodebook()` function in nhanesA.


## log.txt
contains the date/time when the metadata was downloaded, along with any errors or warnings that may have occurred.