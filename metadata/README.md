# The NHANES Metadata Set
This folder contains NHANES metadata tables extracted via [code/get_nhanes_metadata.R](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/get_nhanes_metadata.R), using the [nhanesA](https://github.com/cjendres1/nhanes) package.

## Tables Metadata: `nhanes_tables.tsv`

| Table | TableName | BeginYear | EndYear | DataGroup | UseConstraints | DocFile | DataFile | DatePublished |
|-------|-----------|-----------|---------|-----------|----------------|---------|----------|---------------|

- `Table` contains table identifiers, e.g., `BPX_I`.
- `TableName` contains table names, e.g., `Blood Pressure`.
- `BeginYear` and `EndYear` provide the start and end years of the survey/table.
- `DataGroup` provides the data component of the survey, which can be "Demographics", "Dietary", "Examination", "Laboratory", or "Questionnaire".
- `DocFile` and `DataFile` provide the URLs to the documentation .HTML page and the .XPT data file, respectively.
- `DatePublished` provides the date when the table was published or updated. 


## Variables Metadata: `nhanes_variables.tsv`

| Variable | Table | SASLabel | EnglishText | EnglishInstructions | Target | UseConstraints | ProcessedText | Tags | IsPhenotype | OntologyMapped |
|----------|-------|----------|-------------|---------------------|--------|----------------|---------------|------|-------------|----------------|

- `Variable` contains variable identifiers, e.g., "PEASCCT1".
- `Table` contains table identifiers, e.g., "BPX_I".
- `SASLabel` contains variable labels, e.g., "Blood Pressure Comment".
- `EnglishText` contains either the same labels as in `SASLabel` or more detailed descriptions of the variables, e.g., where the `SASLabel` of variable `BPXSY1` is "Systolic: Blood pres (1st rdg) mm Hg", the provided `EnglishText` is "Systolic: Blood pressure (first reading) mm Hg".  
- `EnglishInstructions` contains, for some variables, instructions for answering the question, e.g., "Enter age in years".
- `Target` contains the target demographic of the variable, e.g., "Both males and females 18 YEARS - 59 YEARS".   
- `ProcessedText` contains the processed version of the SASLabel of a variable, e.g., "Blood Pressure" instead of "Blood Pressure Comment" (see [Preprocessing the metadata](#preprocessing-the-metadata)).
- `Tags` contains the tags attached to the variable during preprocessing, e.g., "comment".
- `IsPhenotype` specifies if the variable has been flagged as a non-phenotype during preprocessing.
- `OntologyMapped` specifies if a variable has been mapped to an ontology. 


## Variables Codebooks: `nhanes_variables_codebooks.tsv` 
contains _**variable codebooks**_ which specify possible responses to each variable in each table.

| Variable | Table | CodeOrValue | ValueDescription | Count | Cumulative | SkipToItem |
|----------|-------|-------------|------------------|-------|------------|------------|

Similar to `nhanes_variables.tsv`:
- `Variable` contains variable identifiers.
- `Table` contains table identifiers.
- `CodeOrValue` contains the codes used for in survey question options, observed in the actual data, e.g., 0 or ".".
- `ValueDescription` contains the actual values for the codes in the `CodeOrValue` column, e.g., "No Lab Result" or "Missing".


## Additional files generated during the download process 
- `missing_codebooks.tsv`: contains variables that are listed by `nhanesA::nhanesTableVars()` but that do not have a corresponding codebook obtainable via the `nhanesA::nhanesCodebook()` function.

- `log.txt`: contains the date/time when the metadata was downloaded, along with any errors or warnings that may have occurred.
