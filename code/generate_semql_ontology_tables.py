import os
import sqlite3
import urllib.request
import pandas as pd


# Overlap between readily available SemanticSQL (https://github.com/INCATools/semantic-sql) databases and the
# ontologies planned for use with NHANES
ontologies = {
    # "HPO": "https://s3.amazonaws.com/bbop-sqlite/hp.db",
    "EFO": "https://s3.amazonaws.com/bbop-sqlite/efo.db",
    "FOODON": "https://s3.amazonaws.com/bbop-sqlite/foodon.db",
    "NCIT": "https://s3.amazonaws.com/bbop-sqlite/ncit.db"
}


def get_semsql_ontology_tables(ontology_url, ontology_name, tables_output_folder='ontology-tables',
                               db_output_folder="ontology-db"):
    db_file = os.path.join(db_output_folder, ontology_name.lower() + ".db")
    if not os.path.isfile(db_file):
        if not os.path.exists(db_output_folder):
            os.makedirs(db_output_folder)
        print("Downloading database file for " + ontology_name + "...")
        urllib.request.urlretrieve(ontology_url, db_file)

    print("Generating tables for " + ontology_name + "...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entailed_edge WHERE predicate='rdfs:subClassOf'")
    edge_columns = [x[0] for x in cursor.description]
    edge_data = cursor.fetchall()
    edges_df = pd.DataFrame(edge_data, columns=edge_columns)
    edges_csv_file = os.path.join(tables_output_folder, ontology_name.lower() + "_edges.csv")
    if not os.path.exists(tables_output_folder):
        os.makedirs(tables_output_folder)
    edges_df.to_csv(edges_csv_file, index=False)

    cursor.execute("SELECT * FROM statements WHERE predicate='rdfs:label'")
    labels_columns = [x[0] for x in cursor.description]
    labels_data = cursor.fetchall()
    labels_df = pd.DataFrame(labels_data, columns=labels_columns)
    labels_df = labels_df.drop(columns=["stanza", "object", "datatype", "language"])
    labels_df = labels_df[labels_df["subject"].str.startswith("_:") == False]  # remove blank nodes
    label_csv_file = os.path.join(tables_output_folder, ontology_name.lower() + "_labels.csv")
    labels_df.to_csv(label_csv_file, index=False)

    cursor.close()
    conn.close()
    return edges_df, labels_df


if __name__ == "__main__":
    for ontology in ontologies:
        get_semsql_ontology_tables(ontology_name=ontology, ontology_url=ontologies[ontology])