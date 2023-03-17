This folder contains all the code necessary to retrieve NHANES metadata, to perform ontology mapping, and to generate ontology tables.

### Metadata Retrieval
The code in `get_nhanes_metadata.Rmd` uses the [nhanesA](https://github.com/cjendres1/nhanes) package to retrieve the metadata about NHANES survey tables, variables and response codes, and then writes out the metadata to table files. 

### Ontology Mapping
The code in `generate_ontology_mappings.py` uses [text2term](https://github.com/ccb-hms/ontology-mapper) to generate ontology mappings for the labels used to describe NHANES tables and variables.

### Ontology Tables
The code in `generate_semsql_ontology_tables.py` retrieves [SemanticSQL](https://github.com/INCATools/semantic-sql)-based SQL builds of ontologies and then extracts tables of interest to support ontology-based search of the mapped data points.