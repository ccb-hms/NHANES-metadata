# NHANES-metadata
R code/notebook to retrieve and write out metadata about NHANES survey tables, variables and response codes.

The code uses the [nhanesA](https://github.com/cjendres1/nhanes) package (v0.7.2 - from GitHub) to retrieve the metadata. 

There are three components of the metadata extraction in the `metadata` folder:
* `nhanes_tables.csv` contains metadata about NHANES tables: names, descriptions, years,...
* `nhanes_variables.csv` contains metadata about NHANES variables: names, labels, source tables,...
* `variable_codebooks` folder contains .csv files each containing the codebook for a variable—table pair. The variable and table names are encoded in the file name. For example, for a variable `var1` in a table `table1`, the codebook is saved as `table1_var1.csv`.
