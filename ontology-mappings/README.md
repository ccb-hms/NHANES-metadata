This folder contains mappings of NHANES variable and table descriptions to controlled terms in the following ontologies:

- Experimental Factor Ontology (EFO)
- National Cancer Institute Thesaurus (NCIT)
- Food Ontology (FOODON)

The mappings are generated via [code/generate_ontology_mappings.py](https://github.com/ccb-hms/NHANES-metadata/blob/master/code/generate_ontology_mappings.py), and use [text2term](https://github.com/ccb-hms/ontology-mapper) configured as follows:

```python
min_score=0.8,          # minimum acceptable mapping score  
mapper=Mapper.TFIDF,    # use the (default) TF-IDF-based mapper to compare strings  
excl_deprecated=True,   # exclude deprecated ontology terms
max_mappings=1,         # maximum number of mappings per input term (per ontology)
```

The outputs are two tables:
- `nhanes_tables_mappings.tsv` contains mappings of the table names that are specified in the `TableName` column of the [metadata/nhanes_tables.tsv](https://github.com/ccb-hms/NHANES-metadata/blob/master/metadata/nhanes_tables.tsv) table.
- `nhanes_variables_mappings.tsv` contains mappings of the variable labels that are specified in the `SASLabel` column of the [metadata/nhanes_variables.tsv](https://github.com/ccb-hms/NHANES-metadata/blob/master/metadata/nhanes_variables.tsv) table.