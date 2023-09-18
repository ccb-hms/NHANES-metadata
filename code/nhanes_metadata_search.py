import pandas as pd
import sqlite3
import os

__version__ = "0.4.0"

ONTOLOGY_MAPPINGS_TABLE = 'ontology_mappings'


def import_table_to_db(sql_connection, table_file, table_name, table_columns):
    db_cursor = sql_connection.cursor()
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + ''' (''' + table_columns + ''')''')
    data_frame = pd.read_csv(table_file, sep="\t", low_memory=False)
    data_frame.to_sql(table_name, sql_connection, if_exists='replace', index=False)


def resources_annotated_with_term(db_cursor, search_terms, include_subclasses=True, direct_subclasses_only=False):
    if include_subclasses:
        if direct_subclasses_only:
            ontology_table = "ontology_edges"
        else:
            ontology_table = "ontology_entailed_edges"
    else:
        ontology_table = "ontology_edges"

    query = '''SELECT DISTINCT 
                    m.Variable, 
                    m.`Table`, 
                    m.SourceTerm, 
                    m.MappedTermLabel, 
                    m.MappedTermCURIE, 
                    m.MappingScore
                FROM `''' + ONTOLOGY_MAPPINGS_TABLE + '''` m
                LEFT JOIN ''' + ontology_table + ''' ee ON (m.MappedTermCURIE = ee.Subject)'''
    index = 0
    where_clause = "\nWHERE ("
    for term in search_terms:
        if index == 0:
            where_clause += "m.MappedTermCURIE = \'" + term + "\'"
        else:
            where_clause += " OR m.MappedTermCURIE = \'" + term + "\'"
        if include_subclasses:
            where_clause += " OR ee.Object = \'" + term + "\'"
        index += 1
    query += where_clause + ")"

    results = db_cursor.execute(query).fetchall()
    results_columns = [x[0] for x in db_cursor.description]
    results_df = pd.DataFrame(results, columns=results_columns)
    results_df = results_df.sort_values(by=['Variable'])
    return results_df


def do_example_queries(db_cursor, search_terms=('EFO:0009605', 'EFO:0005741')):  # EFO:0009605 'pancreas disease'
    df1 = resources_annotated_with_term(db_cursor, search_terms=search_terms, include_subclasses=False)
    print("Resources annotated with " + str(search_terms) + ": " + ("0" if df1.empty else str(df1.shape[0])))
    if not df1.empty:
        print(df1.head().to_string() + "\n")

    df2 = resources_annotated_with_term(db_cursor, search_terms=search_terms, include_subclasses=True,
                                        direct_subclasses_only=True)
    print("Resources annotated with " + str(search_terms) + " or direct subclasses: " + (
        "0" if df2.empty else str(df2.shape[0])))
    if not df2.empty:
        print(df2.head().to_string() + "\n")

    df3 = resources_annotated_with_term(db_cursor, search_terms=search_terms, include_subclasses=True,
                                        direct_subclasses_only=False)
    print("Resources annotated with " + str(search_terms) + " or indirect (entailed) subclasses: " + (
        "0" if df3.empty else str(df3.shape[0])))
    if not df3.empty:
        print(df3.head().to_string() + "\n")


if __name__ == '__main__':
    connection = sqlite3.connect(os.path.join("..", "nhanes_metadata.db"))
    cursor = connection.cursor()

    do_example_queries(cursor)
    do_example_queries(cursor, search_terms=["EFO:0005741"])       # infectious disease
    do_example_queries(cursor, search_terms=["EFO:0004324"])       # body weights and measures
    do_example_queries(cursor, search_terms=["NCIT:C3303"])        # pain
    do_example_queries(cursor, search_terms=["FOODON:00001248"])   # fish food product

    cursor.close()
    connection.close()
