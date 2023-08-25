This folder contains table representations of ontology class hierarchies, generated via [code/generate_semql_ontology_tables.py](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/generate_semql_ontology_tables.py). 

We use readily available [SemanticSQL](https://github.com/INCATools/semantic-sql)-based SQL builds of the Experimental Factor Ontology (EFO), the NCI Thesaurus (NCIT) and the Food Ontology (FoodOn), to generate the following tables:

* `ontology_labels.tsv` contains the labels of all ontology terms (specified via _rdfs:label_).
* `ontology_edges.tsv` contains the asserted _rdfs:subClassOf_ relationships between ontology terms.   
* `ontology_entailed_edges.tsv` contains the inferred _rdfs:subClassOf_ relationships between ontology terms—i.e., the relationships obtained after reasoning over the ontology—this includes asserted relationships.
* `ontology_dbxrefs.tsv` contains the multiple database/ontology cross-references associated with each ontology term.
* `ontology_synonyms.tsv` contains the multiple synonyms associated with each ontology term.

Each file contains all the relationships of that type in all the ontologies—for example, all term labels (from EFO, NCIt, etc.) can be found in the `ontology_labels.tsv` table.