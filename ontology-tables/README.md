This folder contains table representations of ontology class hierarchies, generated via [code/generate_semql_ontology_tables.py](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/generate_semql_ontology_tables.py). 

We use readily available [SemanticSQL](https://github.com/INCATools/semantic-sql)-based SQL builds of the Experimental Factor Ontology (EFO), the NCI Thesaurus (NCIT) and the Food Ontology (FoodOn). For each ontology, e.g., EFO, the following tables are exported:

* `efo_labels.csv` contains the labels of all EFO terms (specified via _rdfs:label_).
* `efo_edges.csv` contains the asserted _rdfs:subClassOf_ relationships between EFO terms.   
* `efo_entailed_edges.csv` contains the inferred _rdfs:subClassOf_ relationships between EFO terms—i.e., the relationships obtained after reasoning over the ontology—this includes asserted relationships.