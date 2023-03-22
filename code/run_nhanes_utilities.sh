alias pip=pip3.9
alias python=python3.9

pip install -r requirements.txt
python generate_semsql_ontology_tables.py
python generate_ontology_mappings.py