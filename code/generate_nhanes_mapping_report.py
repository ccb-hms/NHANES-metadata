import pandas as pd
from generate_mapping_report import get_mapping_counts_to_ontologies


if __name__ == "__main__":
    mapping_counts_df = get_mapping_counts_to_ontologies(
        mappings_df=pd.read_csv("../ontology-mappings/nhanes_variables_mappings.tsv", sep="\t"),
        ontologies_df=pd.read_csv("resources/ontologies.csv"),
        save_ontology=True)

    mapping_counts_df = mapping_counts_df.drop(columns=["Ontology"])

    labels_file = "../ontology-tables/ontology_labels.tsv"
    labels_df = pd.read_csv(labels_file, sep="\t")

    # Merge the counts table with the labels table on the "IRI" column
    merged_df = pd.merge(labels_df, mapping_counts_df, on="IRI")
    merged_df = merged_df.drop_duplicates()
    merged_df.to_csv(labels_file, sep="\t", index=False)
