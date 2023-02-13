from pathlib import Path
import pandas as pd
import text2term
import preprocess_metadata

__version__ = "0.4.0"

MAX_MAPPINGS_PER_ONTOLOGY = 1
MIN_MAPPING_SCORE = 0.4
MAPPINGS_OUTPUT_FOLDER = "ontology-mappings/"
TARGET_ONTOLOGIES = "resources/ontologies.csv"


# Map the given terms to the target ontology
def map_to_ontology(target_ontology, terms_to_map, term_identifiers, base_iris=()):
    if not text2term.cache_exists(target_ontology):
        raise FileNotFoundError("Could not find cache file for ontology: " + target_ontology)

    mappings_df = text2term.map_terms(
        source_terms=terms_to_map,
        target_ontology=target_ontology,
        source_terms_ids=term_identifiers,
        max_mappings=MAX_MAPPINGS_PER_ONTOLOGY,
        min_score=MIN_MAPPING_SCORE,
        base_iris=base_iris,
        excl_deprecated=True,
        save_mappings=False,
        use_cache=True
    )
    mappings_df["Ontology"] = target_ontology
    return mappings_df


# Map the given terms to all ontologies listed in the ontologies table
def map_to_ontologies(ontologies_table, terms_to_map, term_identifiers):
    ontologies_table = pd.read_csv(ontologies_table)
    all_mappings = pd.DataFrame()
    for index, row in ontologies_table.iterrows():
        ontology_name = row['acronym']
        limit_to_base_iris = row['iris']
        if not pd.isna(limit_to_base_iris):
            ontology_mappings = map_to_ontology(target_ontology=ontology_name, base_iris=(limit_to_base_iris,),
                                                terms_to_map=terms_to_map, term_identifiers=term_identifiers)
        else:
            ontology_mappings = map_to_ontology(target_ontology=ontology_name,
                                                terms_to_map=terms_to_map, term_identifiers=term_identifiers)
        all_mappings = pd.concat([all_mappings, ontology_mappings])
    all_mappings = all_mappings.drop_duplicates()
    return all_mappings


def map_data_with_composite_ids(df, labels_column, variable_id_column, table_id_column):
    sep = ":::"
    combined_id_column = "Variable ID"
    df[combined_id_column] = df[variable_id_column].astype(str) + sep + df[table_id_column]
    mappings_df = map_data(df, labels_column, combined_id_column)
    expanded_df = expand_composite_ids(mappings_df, variable_id_column, table_id_column, "Source Term Id", sep=sep)
    return expanded_df


def map_data(source_df, labels_column, label_ids_column):
    terms, term_ids = get_terms_and_ids(source_df, labels_column, label_ids_column)
    mappings_df = map_to_ontologies(
        terms_to_map=terms,
        term_identifiers=term_ids,
        ontologies_table=TARGET_ONTOLOGIES)
    return mappings_df


def get_terms_and_ids(nhanes_table, label_col, label_id_col):
    terms = nhanes_table[label_col].tolist()
    term_ids = nhanes_table[label_id_col].tolist()
    return terms, term_ids


def expand_composite_ids(df, id_1_col, id_2_col, mappings_df_id_col, sep=":::"):
    df[[id_1_col, id_2_col]] = df[mappings_df_id_col].str.split(sep, expand=True)
    df = df.drop(columns=[mappings_df_id_col])
    cols_to_move = [id_1_col, id_2_col]
    df = df[cols_to_move + [col for col in df.columns if col not in cols_to_move]]
    return df


def save_mappings_as_csv(mappings_df, output_file_label, output_file_suffix=""):
    Path(MAPPINGS_OUTPUT_FOLDER).mkdir(exist_ok=True, parents=True)
    output_file_name = MAPPINGS_OUTPUT_FOLDER + output_file_label + "_mappings"
    if output_file_suffix != "":
        output_file_name += "_" + output_file_suffix
    mappings_df.to_csv(output_file_name + ".csv", index=False)


def save_mappings_subsets(df, table_list):
    for table in table_list:
        subset = df[df["Table"] == table]
        save_mappings_as_csv(subset, output_file_label=table)


def map_nhanes_tables(save_mappings=False):
    source_file = "https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/metadata/nhanes_tables.csv"
    mappings = map_data(source_df=pd.read_csv(source_file), labels_column="Table Name", label_ids_column="Table")
    if save_mappings:
        save_mappings_as_csv(mappings, output_file_label="nhanes_tables", output_file_suffix="all")
    return mappings


def map_nhanes_variables(preprocess=False, save_mappings=False):
    source_file = "https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/metadata/nhanes_variables.csv"
    labels_column = "SAS Label"
    if preprocess:
        input_df = preprocess_metadata.main(input_file=source_file,
                                            column_to_process=labels_column,
                                            save_processed_table=False)
        labels_column = "Processed Text"
        output_file_suffix = "preprocessed"
    else:
        input_df = pd.read_csv(source_file)
        output_file_suffix = "all"
    mappings = map_data_with_composite_ids(df=input_df,
                                           labels_column=labels_column,
                                           variable_id_column="Variable",
                                           table_id_column="Table")
    if save_mappings:
        save_mappings_as_csv(mappings, output_file_label="nhanes_variables", output_file_suffix=output_file_suffix)
    return mappings


def map_nhanes_metadata(create_ontology_cache, preprocess_labels, save_mappings):
    if create_ontology_cache:
        text2term.cache_ontology_set(ontology_registry_path=TARGET_ONTOLOGIES)
    nhanes_table_mappings = map_nhanes_tables(save_mappings=save_mappings)
    nhanes_variable_mappings = map_nhanes_variables(preprocess=preprocess_labels, save_mappings=save_mappings)
    return nhanes_table_mappings, nhanes_variable_mappings


if __name__ == "__main__":
    table_mappings, variable_mappings = map_nhanes_metadata(create_ontology_cache=False,
                                                            preprocess_labels=True,
                                                            save_mappings=True)
    save_mappings_subsets(variable_mappings, ["OHXREF_C", "OHXPRU_C", "OHXPRL_C", "OHXDEN_C"])
