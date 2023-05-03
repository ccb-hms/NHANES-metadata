from pathlib import Path
import pandas as pd
import sqlite3

__version__ = "0.2.0"

ONTOLOGY_MAPPINGS_TABLE = 'ontology_mappings'


def setup_database():
    db_name = 'example_database.db'
    Path(db_name).touch()
    db_connection = sqlite3.connect(db_name)
    ontology_tables_folder = '../ontology-tables/'
    semsql_table_columns = "subject,object,ontology"

    # Import the edges and labels tables
    ontology_edges_table_name = "ontology_edges"
    ontology_entailed_edges_table_name = "ontology_entailed_edges"
    ontology_term_labels_table_name = "ontology_labels"

    import_table_to_db(sql_connection=db_connection,
                       table_file=ontology_tables_folder + ontology_edges_table_name + '.tsv',
                       table_name=ontology_edges_table_name, table_columns=semsql_table_columns)

    import_table_to_db(sql_connection=db_connection,
                       table_file=ontology_tables_folder + ontology_entailed_edges_table_name + '.tsv',
                       table_name=ontology_entailed_edges_table_name, table_columns=semsql_table_columns)

    import_table_to_db(sql_connection=db_connection,
                       table_file=ontology_tables_folder + ontology_term_labels_table_name + '.tsv',
                       table_name=ontology_term_labels_table_name, table_columns=semsql_table_columns)

    # Import the ontology mappings table
    import_table_to_db(sql_connection=db_connection,
                       table_file="../ontology-mappings/nhanes_variables_mappings.tsv",
                       table_name=ONTOLOGY_MAPPINGS_TABLE,
                       table_columns="'Variable','Table','SourceTerm','MappedTermLabel','MappedTermCURIE',"
                                     "'MappedTermIRI','MappingScore','Tags','Ontology'")
    return db_connection


def import_table_to_db(sql_connection, table_file, table_name, table_columns):
    db_cursor = sql_connection.cursor()
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + ''' (''' + table_columns + ''')''')
    data_frame = pd.read_csv(table_file, sep="\t")
    data_frame.to_sql(table_name, sql_connection, if_exists='replace', index=False)


def resources_annotated_with_term(db_cursor, search_term, include_subclasses=True, direct_subclasses_only=False):
    if include_subclasses:
        if direct_subclasses_only:
            ontology_table = "ontology_edges"
        else:
            ontology_table = "ontology_entailed_edges"
    else:
        ontology_table = "ontology_edges"

    query = '''SELECT DISTINCT m.`Variable`, m.`Table`, m.`SourceTerm`, 
                    m.`MappedTermLabel`, m.`MappedTermCURIE`, m.`MappingScore`
                 FROM `''' + ONTOLOGY_MAPPINGS_TABLE + '''` m
                 LEFT JOIN ''' + ontology_table + ''' ee ON (m.`MappedTermCURIE` = ee.Subject)
                 WHERE (m.`MappedTermCURIE` = \'''' + search_term + '''\'''' +\
            (''' OR ee.Object = \'''' + search_term + '''\'''' if include_subclasses else '''''') + ''')'''
    results = db_cursor.execute(query).fetchall()
    results_columns = [x[0] for x in db_cursor.description]
    results_df = pd.DataFrame(results, columns=results_columns)
    results_df = results_df.sort_values(by=['Variable'])
    return results_df


def do_example_queries(db_cursor, search_term='EFO:0009605'):  # EFO:0009605 'pancreas disease'
    df1 = resources_annotated_with_term(db_cursor, search_term=search_term, include_subclasses=False)
    print("Resources annotated with " + search_term + ": " + ("0" if df1.empty else str(df1.shape[0])))
    if not df1.empty:
        print(df1.head().to_string() + "\n")

    df2 = resources_annotated_with_term(db_cursor, search_term=search_term, include_subclasses=True,
                                        direct_subclasses_only=True)
    print("Resources annotated with " + search_term + " or its direct (asserted) subclasses: " + (
        "0" if df2.empty else str(df2.shape[0])))
    if not df2.empty:
        print(df2.head().to_string() + "\n")

    df3 = resources_annotated_with_term(db_cursor, search_term=search_term, include_subclasses=True,
                                        direct_subclasses_only=False)
    print("Resources annotated with " + search_term + " or its indirect (inferred) subclasses: " + (
        "0" if df3.empty else str(df3.shape[0])))
    if not df3.empty:
        print(df3.head().to_string() + "\n")


if __name__ == '__main__':
    connection = setup_database()
    cursor = connection.cursor()

    do_example_queries(cursor)
    do_example_queries(cursor, search_term="EFO:0005741")       # infectious disease
    do_example_queries(cursor, search_term="EFO:0004324")       # body weights and measures
    do_example_queries(cursor, search_term="NCIT:C3303")        # pain
    do_example_queries(cursor, search_term="FOODON:00001248")   # fish food product

    cursor.close()
    connection.close()
