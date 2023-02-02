from pathlib import Path
import pandas as pd
import text2term

__version__ = "0.2.0"

MAX_MAPPINGS = 1
MIN_SCORE = 0.5
MAPPINGS_OUTPUT_FOLDER = "ontology-mappings/"
TARGET_ONTOLOGIES = "resources/ontologies.csv"


# Map the values in the specified columns of the source file to the target ontology
def map_to_ontology(target_ontology, source_file, source_file_columns, base_iris=()):
    if not text2term.cache_exists(target_ontology):
        raise FileNotFoundError("Could not find cache file for ontology: " + target_ontology)

    mappings_df = text2term.map_file(
            input_file=source_file,
            target_ontology=target_ontology,
            csv_columns=source_file_columns,
            max_mappings=MAX_MAPPINGS,
            min_score=MIN_SCORE,
            base_iris=base_iris,
            excl_deprecated=True,
            save_mappings=False,
            use_cache=True
    )
    mappings_df["Ontology"] = target_ontology
    return mappings_df


# Map the values in the specified columns of the source file to all ontologies listed in the ontologies table
def map_to_ontologies(ontologies_table, source_file, source_file_columns, save_mappings, output_file_label=""):
    ontologies_table = pd.read_csv(ontologies_table)
    all_mappings = pd.DataFrame()
    for index, row in ontologies_table.iterrows():
        ontology_name = row['acronym']
        limit_to_base_iris = row['iris']
        if not pd.isna(limit_to_base_iris):
            ontology_mappings = map_to_ontology(target_ontology=ontology_name, base_iris=(limit_to_base_iris,),
                                                source_file=source_file, source_file_columns=source_file_columns)
        else:
            ontology_mappings = map_to_ontology(target_ontology=ontology_name,
                                                source_file=source_file, source_file_columns=source_file_columns)
        all_mappings = pd.concat([all_mappings, ontology_mappings])
    all_mappings = all_mappings.drop_duplicates()
    best_mappings = get_best_mappings(all_mappings, source_file, source_file_columns)
    if save_mappings:
        if output_file_label == "":
            output_file_label = Path(source_file).stem
        save_mappings_as_csv(all_mappings, output_file_label, "all")
        save_mappings_as_csv(best_mappings, output_file_label, "best")
    return all_mappings, best_mappings


def map_nhanes_tables(save_mappings, output_file_label=""):
    return map_to_ontologies(source_file="https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/metadata/nhanes_tables.csv",
                             source_file_columns=("Table Name", "Table"),
                             ontologies_table=TARGET_ONTOLOGIES,
                             output_file_label=output_file_label,
                             save_mappings=save_mappings)


def map_nhanes_variables(save_mappings, output_file_label=""):
    return map_to_ontologies(source_file="https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/metadata/nhanes_variables.csv",
                             source_file_columns=("SAS Label", "Variable"),
                             ontologies_table=TARGET_ONTOLOGIES,
                             output_file_label=output_file_label,
                             save_mappings=save_mappings)


def map_preprocessed_nhanes_variables(save_mappings, output_file_label=""):
    return map_to_ontologies(source_file="https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/preprocessing/nhanes_variables_processed.csv",
                             source_file_columns=("Processed Text", "Variable"),
                             ontologies_table=TARGET_ONTOLOGIES,
                             output_file_label=output_file_label,
                             save_mappings=save_mappings)


def map_nhanes_metadata(save_mappings, create_ontology_cache):
    if create_ontology_cache:
        text2term.cache_ontology_set(ontology_registry_path=TARGET_ONTOLOGIES)
    map_nhanes_tables(save_mappings=save_mappings)
    map_nhanes_variables(save_mappings=save_mappings)
    map_preprocessed_nhanes_variables(save_mappings=save_mappings)


# Get a dataframe containing the top-ranked mapping for each input variable
def get_best_mappings(mappings_df, source_file, source_file_columns):
    nhanes_table = pd.read_csv(source_file)
    source_file_label_column = source_file_columns[0]
    best_mappings = pd.DataFrame()
    for index, row in nhanes_table.iterrows():
        variable_label = row[source_file_label_column]
        mappings = mappings_df[mappings_df['Source Term'] == variable_label]
        best_mapping = mappings[mappings['Mapping Score'] == mappings['Mapping Score'].max()]
        best_mappings = pd.concat([best_mappings, best_mapping])
    best_mappings = best_mappings.drop_duplicates()
    return best_mappings


def save_mappings_as_csv(mappings_df, output_file_label, output_file_suffix):
    Path(MAPPINGS_OUTPUT_FOLDER).mkdir(exist_ok=True, parents=True)
    output_file_name = MAPPINGS_OUTPUT_FOLDER + output_file_label + "_mappings_" + output_file_suffix + ".csv"
    mappings_df.to_csv(output_file_name, index=False)


if __name__ == "__main__":
    map_nhanes_metadata(save_mappings=True, create_ontology_cache=False)
