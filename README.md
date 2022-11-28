# NHANES-metadata
R code/notebook to retrieve and write out metadata about NHANES survey tables, variables and response codes.

The code uses the [nhanesA](https://github.com/cjendres1/nhanes) package (v0.7.2 - from GitHub) to retrieve the metadata. 

There are three components of the metadata extraction in the `metadata` folder:
* `nhanes_tables.csv` contains metadata about all NHANES tables: names, descriptions, years,...
* `nhanes_variables.csv` contains metadata about all NHANES variables: names, labels, descriptions, source tables,...
* `variable_codebooks` folder contains .csv files each containing the codebook for a variable—table pair. The names of the variable and table are encoded in the file name. For example, for a given variable `var1` in a given table `table1`, the response metadata are saved as a .csv file named `table1_var1.csv`.
