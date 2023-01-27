import pandas as pd
import text2term

MAX_MAPPINGS = 1
MIN_SCORE = 0.5
EXCLUDE_DEPRECATED = True
MAPPINGS_OUTPUT_FOLDER = "ontology-mappings/"
NHANES_TABLE = "https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/preprocessing/nhanes_variables_processed.csv"
NHANES_VARIABLE_LABEL_COLUMN = "Processed Text"
NHANES_VARIABLE_ID_COLUMN = "Variable"
NHANES_TABLE_COLUMNS = (NHANES_VARIABLE_LABEL_COLUMN, NHANES_VARIABLE_ID_COLUMN)


# Maps the given table to the specified ontology
def map_to_ontology(ontology_name, csv_file=NHANES_TABLE, csv_file_columns=NHANES_TABLE_COLUMNS, base_iris=()):
    if not text2term.cache_exists(ontology_name):
        raise FileNotFoundError("Could not find cache file for ontology: " + ontology_name)
    mappings_df = text2term.map_file(
            input_file=csv_file,
            target_ontology=ontology_name,
            output_file=get_output_file_name(ontology_name),
            csv_columns=csv_file_columns,
            max_mappings=MAX_MAPPINGS,
            min_score=MIN_SCORE,
            base_iris=base_iris,
            excl_deprecated=EXCLUDE_DEPRECATED,
            save_mappings=False,
            use_cache=True
    )
    mappings_df["Ontology"] = ontology_name
    return mappings_df


def get_output_file_name(ontology_name):
    return MAPPINGS_OUTPUT_FOLDER + "mappings_" + ontology_name + ".csv"


# Get a dataframe containing the top-ranked mapping for each input variable
def get_best_mappings(mappings_df):
    nhanes_table = pd.read_csv(NHANES_TABLE)
    best_mappings = pd.DataFrame()
    for index, row in nhanes_table.iterrows():
        variable_label = row[NHANES_VARIABLE_LABEL_COLUMN]
        mappings = mappings_df[mappings_df['Source Term'] == variable_label]
        best_mapping = mappings[mappings['Mapping Score'] == mappings['Mapping Score'].max()]
        best_mappings = pd.concat([best_mappings, best_mapping])
    best_mappings = best_mappings.drop_duplicates()
    return best_mappings


# Map to all ontologies specified in the given table file
def map_variables_to_ontologies(ontologies_table):
    ontologies_table = pd.read_csv(ontologies_table)
    all_mappings = pd.DataFrame()
    for index, row in ontologies_table.iterrows():
        name = row['acronym']
        iris = row['iris']
        if not pd.isna(iris):
            ontology_mappings = map_to_ontology(ontology_name=name, base_iris=(iris,))
        else:
            ontology_mappings = map_to_ontology(ontology_name=name)
        all_mappings = pd.concat([all_mappings, ontology_mappings])
    all_mappings = all_mappings.drop_duplicates()
    all_mappings.to_csv(get_output_file_name("ALL"), index=False)
    best_mappings = get_best_mappings(all_mappings)
    best_mappings.to_csv(get_output_file_name("BEST"), index=False)
    return all_mappings


if __name__ == "__main__":
    ontologies = "resources/ontologies.csv"
    text2term.cache_ontology_set(ontologies)
    map_variables_to_ontologies(ontologies_table=ontologies)
