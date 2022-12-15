# NHANES-metadata
R code/notebook to retrieve and write out metadata about NHANES survey tables, variables and response codes.

The code uses the [nhanesA](https://github.com/cjendres1/nhanes) package (v0.7.2 - from GitHub) to retrieve the metadata. 

There are three components of the metadata extraction in the `metadata` folder:
* `nhanes_tables.csv` contains metadata about NHANES _tables_: identifiers, descriptions, years,...
* `nhanes_variables.csv` contains metadata about NHANES _variables_: identifiers, labels, full text of questions,...
* `nhanes_variables_codebooks.csv` contains metadata about NHANES _codebooks_, which specify possible responses to the survey questions represented by survey variables. The variable and table identifiers of each codebook are included in the table.
