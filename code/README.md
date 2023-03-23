This folder contains software utilities to perform the tasks below.

### 1. Retrieve NHANES Metadata
`get_nhanes_metadata.Rmd` uses the [nhanesA](https://github.com/cjendres1/nhanes) R package to retrieve the metadata about NHANES survey tables, variables and response codes from all available years (pre-pandemic). The metadata are saved in the [metadata](https://github.com/ccb-hms/NHANES-metadata/tree/master/metadata) folder. 

### 2. Map NHANES Metadata to Ontologies
`generate_ontology_mappings.py` uses the [text2term](https://github.com/ccb-hms/ontology-mapper) Python package to generate ontology mappings for the labels used to describe NHANES tables and variables. The mappings are saved in the [ontology-mappings](https://github.com/ccb-hms/NHANES-metadata/tree/master/ontology-mappings) folder. 

Before mapping, variable labels are preprocessed using the `preprocess_metadata.py` module. As a consequence, the output of the mapping process contains the preprocessed labels rather than the original ones.   

### 3. Generate Ontology Tables to Facilitate Search in Relational DBs
`generate_semsql_ontology_tables.py` retrieves [SemanticSQL](https://github.com/INCATools/semantic-sql)-based SQL builds of ontologies and then extracts tables of interest to support ontology-based search of the mapped metadata. The tables are saved in the [ontology-tables](https://github.com/ccb-hms/NHANES-metadata/tree/master/ontology-tables) folder.

### 4. Perform Ontology-based Search of Mapped Metadata
`ontology_annotated_data_search_py` provides a prototype search interface over the mapped NHANES metadata. It uses the ontology mappings table (generated in **2.**) and the ontology tables (generated in **3.**) to enable searching for NHANES variables that have been annotated with a given search term, or with more specific terms according to the respective ontology's class hierarchy structure. For example, search for variables annotated with _infectious disease_`EFO:0005741` and its subclasses in the EFO ontology. 

### Other Utilities
`run_nhanes_utilities.sh` installs the Python dependencies listed in `requirements.txt`, which are necessary to run the Python utilities described. It then executes both `generate_ontology_mappings.py` and `generate_semsql_ontology_tables.py` to obtain the _ontology-mappings_ and _ontology-tables_ folders, respectively.