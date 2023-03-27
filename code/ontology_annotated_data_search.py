from pathlib import Path
import pandas as pd
import sqlite3

__version__ = "0.1.2"

ONTOLOGIES = {'efo', 'ncit', 'foodon'}
ONTOLOGY_MAPPINGS_TABLE = 'ontology_mappings'


def setup_database():
    db_name = 'example_database.db'
    Path(db_name).touch()
    db_connection = sqlite3.connect(db_name)
    ontology_tables_folder = 'https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/ontology-tables/'

    # Import the edges and labels tables for each ontology
    for ontology_name in ONTOLOGIES:
        ontology_edges_table_name = ontology_name + "_edges"
        ontology_entailed_edges_table_name = ontology_name + "_entailed_edges"
        ontology_term_labels_table_name = ontology_name + "_labels"
        semsql_table_columns = "subject,predicate,object"

        import_csv_to_db(sql_connection=db_connection,
                         csv_file=ontology_tables_folder + ontology_edges_table_name + '.csv',
                         table_name=ontology_edges_table_name, table_columns=semsql_table_columns)

        import_csv_to_db(sql_connection=db_connection,
                         csv_file=ontology_tables_folder + ontology_entailed_edges_table_name + '.csv',
                         table_name=ontology_entailed_edges_table_name, table_columns=semsql_table_columns)

        import_csv_to_db(sql_connection=db_connection,
                         csv_file=ontology_tables_folder + ontology_term_labels_table_name + '.csv',
                         table_name=ontology_term_labels_table_name, table_columns=semsql_table_columns)

    # Import the ontology mappings table
    import_csv_to_db(sql_connection=db_connection,
                     csv_file='https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/ontology-mappings/nhanes_variables_mappings.csv',
                     table_name=ONTOLOGY_MAPPINGS_TABLE,
                     table_columns="'Variable','Table','Source Term','Mapped Term Label','Mapped Term CURIE',"
                                   "'Mapped Term IRI','Mapping Score','Tags','Ontology'")
    return db_connection


def import_csv_to_db(sql_connection, csv_file, table_name, table_columns):
    cursor = sql_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + ''' (''' + table_columns + ''')''')
    data_frame = pd.read_csv(csv_file)
    data_frame.to_sql(table_name, sql_connection, if_exists='replace', index=False)


def resources_annotated_with_term(cursor, search_term, include_subclasses=True, direct_subclasses_only=False):
    result_df = pd.DataFrame()
    for ontology in ONTOLOGIES:
        df = resources_annotated_with_term_in_ontology(cursor=cursor, search_term=search_term, ontology_name=ontology,
                                                       include_subclasses=include_subclasses,
                                                       direct_subclasses_only=direct_subclasses_only)
        result_df = pd.concat([result_df, df])
    return result_df


def resources_annotated_with_term_in_ontology(cursor, search_term, ontology_name, include_subclasses=True,
                                              direct_subclasses_only=False):
    if include_subclasses:
        if direct_subclasses_only:
            ontology_table = ontology_name + "_edges"
        else:
            ontology_table = ontology_name + "_entailed_edges"
    else:
        ontology_table = ontology_name + "_edges"
    results = cursor.execute('''
                 SELECT DISTINCT m.`Variable` AS "Variable ID", m.`Table` AS "Table ID", 
                    m.`Source Term` AS "Variable Label (preprocessed)",
                    m.`Mapped Term Label` AS "Ontology Term", m.`Mapped Term CURIE` AS "Ontology Term ID",
                    m.`Mapping Score` AS "Mapping Confidence"
                 FROM `''' + ONTOLOGY_MAPPINGS_TABLE + '''` m
                 LEFT JOIN ''' + ontology_table + ''' ee ON (m.`Mapped Term CURIE` = ee.subject)
                 WHERE (m.`Mapped Term CURIE` = \'''' + search_term + '''\'''' +
                             (''' OR ee.object = \'''' + search_term + '''\'''' if include_subclasses else '''''')
                             + ''') AND ee.predicate = 'rdfs:subClassOf'
                 ''').fetchall()
    results_columns = [x[0] for x in cursor.description]
    results_df = pd.DataFrame(results, columns=results_columns)
    results_df = results_df.sort_values(by=['Variable ID'])
    return results_df


def do_example_queries(db_cursor, search_term='EFO:0009605'):  # EFO:0009605 'pancreas disease'
    df1 = resources_annotated_with_term(db_cursor, search_term=search_term, include_subclasses=False)
    print("Resources annotated with " + search_term + ": " + ("0" if df1.empty else str(df1.shape[0])))
    if not df1.empty:
        print(df1.head().to_string() + "\n")

    df2 = resources_annotated_with_term(db_cursor, search_term=search_term, include_subclasses=True, direct_subclasses_only=True)
    print("Resources annotated with " + search_term + " or its direct (asserted) subclasses: " + ("0" if df2.empty else str(df2.shape[0])))
    if not df2.empty:
        print(df2.head().to_string() + "\n")

    df3 = resources_annotated_with_term(db_cursor, search_term=search_term, include_subclasses=True, direct_subclasses_only=False)
    print("Resources annotated with " + search_term + " or its indirect (inferred) subclasses: " + ("0" if df3.empty else str(df3.shape[0])))
    if not df3.empty:
        print(df3.head().to_string() + "\n")


if __name__ == '__main__':
    connection = setup_database()
    cursor = connection.cursor()

    do_example_queries(cursor)
    do_example_queries(cursor, search_term="EFO:0005741")    # infectious disease
    do_example_queries(cursor, search_term="EFO:0004324")    # body weights and measures
    do_example_queries(cursor, search_term="NCIT:C3303")     # pain

    cursor.close()
    connection.close()
