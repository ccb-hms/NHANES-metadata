import pandas as pd
import text2term

MAX_MAPPINGS = 1
MIN_SCORE = 0.5
EXCLUDE_DEPRECATED = True
SAVE_MAPPINGS = True
MAPPINGS_OUTPUT_FOLDER = "ontology-mappings/"
NHANES_TABLE = "https://raw.githubusercontent.com/ccb-hms/NHANES-metadata/master/metadata/nhanes_variables.csv"
NHANES_TABLE_COLUMNS = ("SAS Label", "Variable")


# Maps the given table to the specified ontology
def map_to_ontology(ontology_name, csv_file=NHANES_TABLE, csv_file_columns=NHANES_TABLE_COLUMNS, base_iris=()):
    mappings_df = text2term.map_file(
        input_file=csv_file,
        target_ontology=ontology_name,
        output_file=get_output_file_name(ontology_name),
        csv_columns=csv_file_columns,
        max_mappings=MAX_MAPPINGS,
        min_score=MIN_SCORE,
        base_iris=base_iris,
        excl_deprecated=EXCLUDE_DEPRECATED,
        save_mappings=SAVE_MAPPINGS,
        use_cache=True
    )
    return add_ontology_source(mappings_df, ontology_name)


def map_to_hpo():
    return map_to_ontology('HPO', base_iris=("http://purl.obolibrary.org/obo/HP",))


def map_to_efo():
    return map_to_ontology('EFO', base_iris=("http://www.ebi.ac.uk/efo/EFO",))


def map_to_mondo():
    return map_to_ontology("MONDO", base_iris=("http://purl.obolibrary.org/obo/MONDO",))


def map_to_uberon():
    return map_to_ontology("UBERON", base_iris=("http://purl.obolibrary.org/obo/UBERON",))


def map_to_nci_thesaurus():
    return map_to_ontology("NCIT")


def map_to_uo():
    return map_to_ontology("UO", base_iris=("http://purl.obolibrary.org/obo/UO",))


def map_to_ecto():
    """
    2 errors come up upon loading ECTO (http://purl.obolibrary.org/obo/ecto/releases/2022-12-12/ecto.owl):
    - Cannot read literal of datatype xml:string
        obo.CDNO_0000003, CHEBI_16646, CDNO_0000004, CHEBI_17996, ...
    - _pickle.PicklingError: Can't pickle obo.IAO_0000078: attribute lookup IAO_0000078 on owlready2.entity failed
    """
    return map_to_ontology("ECTO", base_iris=("http://purl.obolibrary.org/obo/ECTO",))


# TODO map to more recent version of SNOMED — conversion script is failing for 2022 releases
def map_to_snomed():
    return map_to_ontology("SNOMED")


def map_to_chebi():
    return map_to_ontology("CHEBI", base_iris=("http://purl.obolibrary.org/obo/CHEBI",))


def map_to_foodon():
    # TODO implement
    pass


def get_output_file_name(ontology_name):
    return MAPPINGS_OUTPUT_FOLDER + "mappings_" + ontology_name + ".csv"


def add_ontology_source(data_frame, ontology_name):
    data_frame["Ontology"] = ontology_name
    return data_frame


def get_best_mappings(mappings_df):
    nhanes_table = pd.read_csv(NHANES_TABLE)
    best_mappings = pd.DataFrame()
    for index, row in nhanes_table.iterrows():
        variable_label = row['SAS Label']
        mappings = mappings_df[mappings_df['Source Term'] == variable_label]
        best_mapping = mappings[mappings['Mapping Score'] == mappings['Mapping Score'].max()]
        best_mappings = pd.concat([best_mappings, best_mapping])
    best_mappings = best_mappings.drop_duplicates()
    return best_mappings


def map_variables_to_ontologies():
    efo_mappings = map_to_efo()
    hpo_mappings = map_to_hpo()
    mondo_mappings = map_to_mondo()
    ncit_mappings = map_to_nci_thesaurus()
    snomed_mappings = map_to_snomed()
    uberon_mappings = map_to_uberon()
    uo_mappings = map_to_uo()
    chebi_mappings = map_to_chebi()
    # ecto_mappings = map_to_ecto()

    all_mappings = pd.concat([efo_mappings, hpo_mappings, mondo_mappings, ncit_mappings, snomed_mappings,
                              uberon_mappings, uo_mappings, chebi_mappings], axis=0)
    all_mappings = all_mappings.drop_duplicates()
    all_mappings.to_csv(get_output_file_name("ALL"), index=False)
    best_mappings = get_best_mappings(all_mappings)
    best_mappings.to_csv(get_output_file_name("BEST"), index=False)


if __name__ == "__main__":
    text2term.cache_ontology_set("ontologies.csv")
    map_variables_to_ontologies()
