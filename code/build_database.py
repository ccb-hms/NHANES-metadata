import os.path
from pathlib import Path
import pandas as pd
import tarfile
import sqlite3

__version__ = "0.2.0"

ONTOLOGY_MAPPINGS_TABLE = 'ontology_mappings'


def build_database(database_name):
    Path(database_name).touch()
    db_connection = sqlite3.connect(database_name)
    ontology_tables_folder = os.path.join("..", "ontology-tables")

    # Import the edges and database cross-references tables
    ontology_edges_table = "ontology_edges"
    ontology_entailed_edges_table = "ontology_entailed_edges"
    ontology_dbxrefs_table = "ontology_dbxrefs"
    ontology_synonyms_table = "ontology_synonyms"
    ontology_tables_columns = "Subject TEXT,Object TEXT,Ontology TEXT"

    import_table_to_db(db_connection, table_file=os.path.join(ontology_tables_folder, ontology_edges_table + '.tsv'),
                       table_name=ontology_edges_table, table_columns=ontology_tables_columns)

    import_table_to_db(db_connection,
                       table_file=os.path.join(ontology_tables_folder, ontology_entailed_edges_table + '.tsv'),
                       table_name=ontology_entailed_edges_table, table_columns=ontology_tables_columns)

    import_table_to_db(db_connection, table_file=os.path.join(ontology_tables_folder, ontology_dbxrefs_table + '.tsv'),
                       table_name=ontology_dbxrefs_table, table_columns=ontology_tables_columns)

    import_table_to_db(db_connection, table_file=os.path.join(ontology_tables_folder, ontology_synonyms_table + '.tsv'),
                       table_name=ontology_synonyms_table, table_columns=ontology_tables_columns)

    # Import the labels table
    term_labels_table_name = "ontology_labels"
    term_labels_table_columns = "Subject TEXT,Object TEXT,IRI TEXT,DiseaseLocation TEXT,Ontology TEXT," \
                                "Direct INT,Inherited INT"
    import_table_to_db(db_connection, table_file=os.path.join(ontology_tables_folder, term_labels_table_name + '.tsv'),
                       table_name=term_labels_table_name, table_columns=term_labels_table_columns)

    # Import the ontology mappings table
    mappings_table_columns = "Variable TEXT,`Table` TEXT,SourceTermID TEXT,SourceTerm TEXT,MappedTermLabel TEXT," \
                             "MappedTermCURIE TEXT,MappedTermIRI TEXT,MappingScore REAL,Tags TEXT,Ontology TEXT"
    import_table_to_db(db_connection,
                       table_file=os.path.join("..", "ontology-mappings", "nhanes_variables_mappings.tsv"),
                       table_name=ONTOLOGY_MAPPINGS_TABLE, table_columns=mappings_table_columns)

    # Import the NHANES variables metadata table
    metadata_columns = "Variable TEXT,`Table` TEXT,SASLabel TEXT,EnglishText TEXT,EnglishInstructions TEXT,Target TEXT," \
                       "UseConstraints TEXT,ProcessedText TEXT,Tags TEXT,IsPhenotype BOOLEAN,OntologyMapped BOOLEAN"
    import_table_to_db(db_connection, table_file=os.path.join("..", "metadata", "nhanes_variables.tsv"),
                       table_name="nhanes_variables_metadata", table_columns=metadata_columns)

    # Import the NHANES tables metadata table
    table_metadata_columns = "`Table` TEXT,TableName TEXT,BeginYear INT,EndYear INT,DataGroup TEXT,UseConstraints TEXT," \
                             "DocFile TEXT,DataFile TEXT,DatePublished TEXT"
    import_table_to_db(db_connection, table_file=os.path.join("..", "metadata", "nhanes_tables.tsv"),
                       table_name="nhanes_tables_metadata", table_columns=table_metadata_columns)

    # Import the table of expert-verified oral health phenotype mappings
    manual_mappings_table_columns = "Variable TEXT,`Table` TEXT,SourceTermID TEXT,SourceTerm TEXT,MappedTermLabel TEXT," \
                                    "MappedTermIRI TEXT,MappingScore REAL,Ontology TEXT,Comments TEXT"
    import_table_to_db(db_connection,
                       table_file=os.path.join("..", "ontology-mappings", "nhanes_oral_health_mappings.tsv"),
                       table_name="ontology_mappings_confirmed", table_columns=manual_mappings_table_columns)

    # Import the table of expert-contributed synonyms of variable labels
    synonyms_table_columns = "Variable TEXT,`Table` TEXT,Synonym TEXT"
    import_table_to_db(db_connection, table_file=os.path.join("..", "metadata", "synonym_table.tsv"),
                       table_name="nhanes_variables_synonyms", table_columns=synonyms_table_columns)

    return db_connection


def import_table_to_db(sql_connection, table_file, table_name, table_columns):
    db_cursor = sql_connection.cursor()
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + ''' (''' + table_columns + ''')''')
    data_frame = pd.read_csv(table_file, sep="\t", low_memory=False)
    data_frame.to_sql(table_name, sql_connection, if_exists='replace', index=False)


if __name__ == '__main__':
    db_name = "nhanes_metadata.db"
    db_filepath = os.path.join('..', db_name)
    build_database(db_filepath)
    with tarfile.open(db_filepath + ".tar.xz", "w:xz") as tar:
        tar.add(db_filepath, arcname=db_name)
