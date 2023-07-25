import os
import pandas as pd
from generate_mapping_report import get_mapping_counts_to_ontologies


ONTOLOGY_TABLES_FOLDER = "../ontology-tables/"

if __name__ == "__main__":
    mapping_counts_df = get_mapping_counts_to_ontologies(
        mappings_df=pd.read_csv("../ontology-mappings/nhanes_variables_mappings.tsv", sep="\t"),
        ontologies_df=pd.read_csv("resources/ontologies.csv"),
        save_ontology=True)

    mapping_counts_df = mapping_counts_df.drop(columns=["Ontology"])

    files_in_folder = os.listdir(ONTOLOGY_TABLES_FOLDER)
    labels_files = [file for file in files_in_folder if file.endswith("_labels.tsv")]
    if not labels_files:
        print(f"No files ending with '_labels.tsv' found in {ONTOLOGY_TABLES_FOLDER} folder")

    for labels_file in labels_files:
        labels_file_path = os.path.join(ONTOLOGY_TABLES_FOLDER, labels_file)
        labels_df = pd.read_csv(labels_file_path, sep="\t")

        # Merge the counts table with the labels table on the "IRI" column
        merged_df = pd.merge(labels_df, mapping_counts_df, on="IRI")
        merged_df = merged_df.drop_duplicates()
        merged_df.to_csv(labels_file_path, sep="\t", index=False)
