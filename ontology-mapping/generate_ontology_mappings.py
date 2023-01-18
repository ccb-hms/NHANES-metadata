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
    return map_to_ontology("ECTO", base_iris=("http://purl.obolibrary.org/obo/ECTO",))


# TODO map to more recent version of SNOMED — conversion script is failing for 2022 releases
def map_to_snomed():
    return map_to_ontology("SNOMED")


def map_to_chebi():
    return map_to_ontology("CHEBI", base_iris=("http://purl.obolibrary.org/obo/CHEBI",))


def map_to_foodon():
    return map_to_ontology("FOODON", base_iris=("http://purl.obolibrary.org/obo/FOODON",))


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


# TODO map to all ontologives given in the .csv file
def map_variables_to_ontologies():
    efo_mappings = map_to_efo()  # Map to Experimental Factor Ontology (EFO)
    hpo_mappings = map_to_hpo()  # Map to Human Phenotype Ontology (HPO)
    mondo_mappings = map_to_mondo()  # Map to Monarch Disease Ontology (MONDO)
    ncit_mappings = map_to_nci_thesaurus()  # Map to NCI Thesaurus (NCIT)
    snomed_mappings = map_to_snomed()  # Map to SNOMED CT
    uberon_mappings = map_to_uberon()  # map to Uber Anatomy ontology (UBERON) to determine anatomical location
    uo_mappings = map_to_uo()  # map to Units of Measurement ontology (UO) to determine unit of measurement
    chebi_mappings = map_to_chebi()
    ecto_mappings = map_to_ecto()
    foodon_mappings = map_to_foodon()

    all_mappings = pd.concat([efo_mappings, hpo_mappings, mondo_mappings, ncit_mappings, snomed_mappings,
                              uberon_mappings, uo_mappings, chebi_mappings, ecto_mappings, foodon_mappings], axis=0)
    all_mappings = all_mappings.drop_duplicates()
    all_mappings.to_csv(get_output_file_name("ALL"), index=False)
    best_mappings = get_best_mappings(all_mappings)
    best_mappings.to_csv(get_output_file_name("BEST"), index=False)


if __name__ == "__main__":
    text2term.cache_ontology_set("ontologies.csv")
    map_variables_to_ontologies()
