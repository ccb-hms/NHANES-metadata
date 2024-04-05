# The NHANES Metadata Set
This folder contains NHANES metadata tables extracted via [code/get_nhanes_metadata.R](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/get_nhanes_metadata.R), using the [nhanesA](https://github.com/cjendres1/nhanes) package.

## Tables Metadata: `nhanes_tables.tsv`
The headers of the table containing metadata about NHANES tables are depicted and described below.

| Table | TableName | BeginYear | EndYear | DataGroup | UseConstraints | DocFile | DataFile | DatePublished |
|-------|-----------|-----------|---------|-----------|----------------|---------|----------|---------------|

- `Table` contains table identifiers, e.g., `BPX_I`.
- `TableName` contains table names, e.g., `Blood Pressure`.
- `BeginYear` and `EndYear` provide the start and end years of the survey/table.
- `DataGroup` provides the data component of the survey, which can be "Demographics", "Dietary", "Examination", "Laboratory", or "Questionnaire".
- `DocFile` and `DataFile` provide the URLs to the documentation .HTML page and the .XPT data file, respectively.
- `DatePublished` provides the date when the table was published or updated. 


## Variables Metadata: `nhanes_variables.tsv`
The headers of the table containing metadata about NHANES variables are depicted and described below. 

| Variable | Table | SASLabel | EnglishText | EnglishInstructions | Target | UseConstraints | IsPhenotype | OntologyMapped |
|----------|-------|----------|-------------|---------------------|--------|----------------|-------------|----------------|

- `Variable` contains variable identifiers, e.g., "PEASCCT1".
- `Table` contains table identifiers, e.g., "BPX_I".
- `SASLabel` contains variable labels, e.g., "Blood Pressure Comment".
- `EnglishText` contains either the same labels as in `SASLabel` or more detailed descriptions of the variables, e.g., where the `SASLabel` of variable `BPXSY1` is "Systolic: Blood pres (1st rdg) mm Hg", the provided `EnglishText` is "Systolic: Blood pressure (first reading) mm Hg".  
- `EnglishInstructions` contains, for some variables, instructions for answering the question, e.g., "Enter age in years".
- `Target` contains the target demographic of the variable, e.g., "Both males and females 18 YEARS - 59 YEARS". If there are multiple target values for a given variable, the multiple targets get concatenated into one string while separated by the token `*AND*`.
- `IsPhenotype` specifies if the variable has been flagged as a non-phenotype during preprocessing.
- `OntologyMapped` specifies if a variable has been mapped to an ontology. 

## Processed Variables Metadata: `nhanes_variables_processed.tsv`
A copy of the `nhanes_variables.tsv` table with the additional columns listed below, which are used for ontology mapping. 
- `ProcessedText` contains the processed version of the SASLabel of a variable, e.g., "Blood Pressure" instead of "Blood Pressure Comment" (see [Preprocessing Metadata](#preprocessing-metadata)).
- `Tags` contains the tags attached to the variable during preprocessing, e.g., "comment".

## Variables Codebooks: `nhanes_variables_codebooks.tsv` 
The headers of the table containing the codebooks of NHANES variables are depicted and described below. Variable codebooks specify possible responses to each variable in each table, and how the coded values in the XPT data tables should be translated— since the coded values are often numbers that stand for strings, for example, in some variables a response of 0 means "No Lab Result" or "Yes" or "Good" or "No problem". For appropriate data analysis, the data tables need to be translated using the variable codebooks that we extract here.

| Variable | Table | CodeOrValue | ValueDescription | Count | Cumulative | SkipToItem |
|----------|-------|-------------|------------------|-------|------------|------------|

Similar to `nhanes_variables.tsv`:
- `Variable` contains variable identifiers.
- `Table` contains table identifiers.
- `CodeOrValue` contains the codes used for in survey question options, observed in the actual data, e.g., 0 or ".".
- `ValueDescription` contains the actual values for the codes in the `CodeOrValue` column, e.g., "No Lab Result" or "Missing".


## Additional files generated during the download process 
- `missing_codebooks.tsv`: contains names of tables that do not have a codebook obtainable via the `nhanesA::nhanesCodebook()` function.

- `log.txt`: contains the date/time when the metadata was downloaded, along with any errors or warnings that may have occurred.

---

# Metadata Acquisition Process
In this section we describe the methods and tools used to extract the NHANES metadata assets described above. 

## Downloading Metadata
The R script [`code/get_nhanes_metadata.R`](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/get_nhanes_metadata.R) is used to fetch the NHANES metadata, primarily relying on the [nhanesA](https://github.com/cjendres1/nhanes) R package.

Metadata about NHANES tables are obtained using the `nhanesA::nhanesTables()` and `nhanes::nhanesManifest()` functions. We originally used only `nhanesA::nhanesTables()` but then found that it returns an incomplete set of NHANES tables. We now use the more recently implemented `nhanesA::nhanesManifest()` function, which returns a complete set of tables.

Metadata about variables are obtained primarily using the `nhanesA::nhanesCodebook()` function, which returns variable and table identifiers, variable label, English text, English instructions, and variable targets. To obtain the UseConstraints detail associated with each variable we use `nhanesA::nhanesTableVars()`.

The codebook of each variable is obtained using the `nhanesA::nhanesCodebook()` function.

## Preprocessing Metadata
Some variable labels contain wording that makes it more challenging to identify the underlying phenotype, e.g., "Age when heart disease first diagnosed". For such cases, we developed a [preprocessing module](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/preprocess_metadata.py) that applies "cleanup" regular expressions—provided in the file [`templates.txt`](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/resources/templates.txt)—to the SASLabel of variables. The cleaned-up version of the label text is represented in the `ProcessedText` column of [`nhanes_variables.tsv`](#variables-metadata-nhanes_variablestsv). For example, applying the regular expression `Age when (.*) first diagnosed` to the previous example gives rise to the processed text `heart disease`.

### Adding Tags to Variables
In addition to cleaning up the labels of variables, we developed a mechanism to add tags to variables whose `SASLabel` labels match the regular expressions in [`templates.txt`](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/resources/templates.txt). To tag a variable we use a custom separator `;:;` between the regular expression (that matches the variable label) and the desired tag(s). For example: `Age when (.*) first diagnosed;:;age` adds the tag `age` to all variables whose labels match the regex. Tags are represented in the column `Tags` of [`nhanes_variables.tsv`](#variables-metadata-nhanes_variablestsv).

## Flagging Non-Phenotypes
Certain variables do not represent or relate to a phenotype, for example the variables `DR1EXMER`: "Interviewer ID code" or `PSQ300`: "Language Used". In such cases it is desirable to have a way to flag those variables as non-phenotypes. We implemented two mechanisms to specify non-phenotype variables—one based on specific table-variable identifiers and another based on regular expressions:
- A table [`blocklist_table.csv`](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/resources/blocklist_table.csv) that contains specific variable and table identifiers, which have been manually identified as non-phenotype variables.  
- A file [`blocklist_regexps.txt`](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/resources/blocklist_regexps.txt) that contains a list of regular expressions that are applied to the `SASLabel` of variables—if a label of a variable matches a regular expression, that variable is declared as a non-phenotype variable.  

Variables flagged as non-phenotypes have a value of `False` in the column `IsPhenotype` of [`nhanes_variables.tsv`](#variables-metadata-nhanes_variablestsv), or `True` otherwise.