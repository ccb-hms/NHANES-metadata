# NHANES-metadata
This repository contains code and (meta)data components to be included in the [NHANES database and tools](https://github.com/ccb-hms/NHANES).  

## Code
The [code](https://github.com/ccb-hms/NHANES-metadata/tree/master/code) folder contains the programs that generate the metadata components described in the next subsections. 
* `get_nhanes_metadata.Rmd` extracts and saves NHANES metadata for inclusion in the NHANES database distribution.
* `generate_ontology_mappings.py` generates mappings of the metadata to a select set of ontologies.
* `generate_semsql_ontology_tables.py` downloads [SemanticSQL](https://github.com/INCATools/semantic-sql) ontology databases and exports tables needed to support ontology-based querying.

## Metadata
The [metadata](https://github.com/ccb-hms/NHANES-metadata/tree/master/metadata) folder contains three files with the extracted metadata:
* `nhanes_tables.csv` contains _**table**_ identifiers, descriptions, years,...
* `nhanes_variables.csv` contains _**variable**_ identifiers, labels, full text of questions,...
* `nhanes_variables_codebooks.csv` contains _**codebooks**_, which specify possible responses to survey questions (represented by survey variables).

## Ontology Mappings
The [ontology-mappings](https://github.com/ccb-hms/NHANES-metadata/tree/master/ontology-mappings) folder contains the output of running the [text2term](https://github.com/ccb-hms/ontology-mapper) ontology mapping tool on the labels used to describe NHANES tables and variables. 
* `nhanes_tables_mappings.csv` contains mappings of the table names that are specified in the `Table Name` column of the `nhanes_tables.csv` table.
* `nhanes_variables_mappings.csv` contains mappings of the variable labels that are specified in the `SAS Label` column of the `nhanes_variables.csv` table.

## Ontology Tables
The [ontology-tables](https://github.com/ccb-hms/NHANES-metadata/tree/master/ontology-tables) folder contains tabular representations of the class hierarchies of select ontologies. Here we are leveraging the [SemanticSQL](https://github.com/INCATools/semantic-sql) readily available SQL builds of popular biomedical ontologies. For each ontology, the following tables are exported:
* `ontology_labels.csv` contains the labels of all ontology terms.
* `ontology_edges.csv` contains the asserted relationships between ontology terms.
* `ontology_entailed_edges.csv` contains the inferred relationships between ontology terms (including asserted ones).

These tables can be combined with the ontology-mapping tables to enable ontology-based search of mapped data points. 