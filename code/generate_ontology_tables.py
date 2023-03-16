import os
import owlready2
import pandas as pd
from ontoutils.onto2table import Onto2Table

owlready2.reasoning.JAVA_MEMORY = 16000
OUTPUT_FOLDER = "ontology-tables/"


def generate_tables(output_folder=OUTPUT_FOLDER):
    os.makedirs(output_folder, exist_ok=True)
    ontology_set = pd.read_csv("resources/ontologies.csv")
    for index, row in ontology_set.iterrows():
        Onto2Table.generate_table_from_file(ontology_file=row.url,
                                            output_file=output_folder + row.acronym + ".csv",
                                            use_reasoning=False)


if __name__ == '__main__':
    generate_tables()
