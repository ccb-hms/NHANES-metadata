alias pip=pip3.9
alias python=python3.9

[ ! -d "ontology-utilities" ] && git clone 'https://github.com/ccb-hms/ontology-utilities.git'
(cd "ontology-utilities" || return
pip install . )
pip install -r requirements.txt
python generate_ontology_tables.py
python generate_ontology_mappings.py