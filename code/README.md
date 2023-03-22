This folder contains code to (1) retrieve NHANES metadata, (2) map metadata elements to ontologies, (3) generate ontology tables that can be used for search in a relational database, and (4) perform ontology-based search of annotated metadata.

### (1) Metadata Retrieval
The code in `get_nhanes_metadata.Rmd` uses the [nhanesA](https://github.com/cjendres1/nhanes) package to retrieve the metadata about NHANES survey tables, variables and response codes, and then writes out the metadata to table files. 

### (2) Ontology Mapping
The code in `generate_ontology_mappings.py` uses [text2term](https://github.com/ccb-hms/ontology-mapper) to generate ontology mappings for the labels used to describe NHANES tables and variables.

### (3) Ontology Tables
The code in `generate_semsql_ontology_tables.py` retrieves [SemanticSQL](https://github.com/INCATools/semantic-sql)-based SQL builds of ontologies and then extracts tables of interest to support ontology-based search of the mapped data points.

### (4) Ontology-based Search
The code in `ontology_annotated_data_search_py` is a prototype search interface over the annotated/mapped NHANES metadata. It uses the ontology mappings generated in (2) and the ontology tables generated in (3) to enable searching for NHANES variables that have been annotated with a given search term or with more specific terms (e.g., variables annotated with `EFO:0005741` ('infectious disease') and subclasses). 