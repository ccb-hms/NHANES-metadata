# NHANES-metadata
This repository contains code and (meta)data components included in the [NHANES database and tools](https://github.com/ccb-hms/NHANES).  

## Code
The [code](https://github.com/ccb-hms/NHANES-metadata/tree/master/code) folder contains the programs that generate the metadata components described in the next subsections. 
* `get_nhanes_metadata.R` extracts and saves NHANES metadata from CDC using [nhanesA](https://github.com/cjendres1/nhanes).
* `generate_ontology_mappings.py` generates mappings of the metadata to a select set of ontologies.
* `generate_ontology_tables.py` downloads [SemanticSQL](https://github.com/INCATools/semantic-sql) ontology databases and exports tables needed to support ontology-based querying.
* `generate_nhanes_mapping_report.py` uses the generic module `generate_mapping_report.py` to compute counts of direct and inherited mappings and add them to the ontology labels table. 

## Metadata
The [metadata](https://github.com/ccb-hms/NHANES-metadata/tree/master/metadata) folder contains three files with the extracted metadata:
* `nhanes_tables.tsv` contains _**table**_ identifiers, descriptions, years,...
* `nhanes_variables.tsv` contains _**variable**_ identifiers, labels, full text of questions,...
* `nhanes_variables_codebooks.tsv` contains _**codebooks**_, which specify possible responses to survey questions (represented by survey variables).

## Ontology Mappings
The [ontology-mappings](https://github.com/ccb-hms/NHANES-metadata/tree/master/ontology-mappings) folder contains the output of running the [text2term](https://github.com/ccb-hms/ontology-mapper) ontology mapping tool on the labels used to describe NHANES tables and variables. 
* `nhanes_tables_mappings.tsv` contains mappings of the table names that are specified in the `TableName` column of the `nhanes_tables.tsv` table.
* `nhanes_variables_mappings.tsv` contains mappings of the variable labels that are specified in the `SASLabel` column of the `nhanes_variables.tsv` table.

## Ontology Tables
The [ontology-tables](https://github.com/ccb-hms/NHANES-metadata/tree/master/ontology-tables) folder contains table representations of ontology class hierarchies. We use readily available [SemanticSQL](https://github.com/INCATools/semantic-sql)-based SQL builds of ontologies from which we extract the tables:
* `ontology_labels.tsv` contains the labels of all ontology terms.
* `ontology_edges.tsv` contains the asserted relationships between ontology terms.
* `ontology_entailed_edges.tsv` contains the inferred relationships between ontology terms (including asserted ones).
* `ontology_synonyms.tsv` contains the (exact) synonyms of all ontology terms.
* `ontology_dbxrefs.tsv` contains database cross-references that relate ontology terms to other ontologies or databases.

These tables are combined with the ontology mappings to enable ontology-based search of mapped data points. 
