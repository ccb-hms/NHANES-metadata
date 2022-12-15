# NHANES-metadata
R code/notebook to retrieve and write out metadata about NHANES survey tables, variables and response codes.

The code uses the [nhanesA](https://github.com/cjendres1/nhanes) package (v0.7.2 - from GitHub) to retrieve the metadata. 

There are three files containing the extracted metadata in the `metadata` folder:
* `nhanes_tables.csv` contains _**table**_ identifiers, descriptions, years,...
* `nhanes_variables.csv` contains _**variable**_ identifiers, labels, full text of questions,...
* `nhanes_variables_codebooks.csv` contains _**codebooks**_, which specify possible responses to survey questions (represented by survey variables).
