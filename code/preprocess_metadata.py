import pandas as pd
import numpy as np
import text2term
import os

PROCESSED_TEXT_COL = "ProcessedText"
PHENOTYPE_COL = "IsPhenotype"

# The "blocklist_table" file contains non-phenotype variables specified by their precise identifiers
BLOCKLIST_TABLE = "resources/blocklist_table.csv"

# The "blocklist_regexps" file contains a list of regular expressions that are applied to the labels of variables, and
# where matches occur, the corresponding variables are marked as non-phenotypes
BLOCKLIST_REGEXPS = "resources/blocklist_regexps.txt"


def preprocess(input_file, column_to_process, save_processed_table=False, input_file_col_separator=","):
    print("Preprocessing metadata table...")
    df = pd.read_csv(input_file, sep=input_file_col_separator, lineterminator="\n")
    text_to_process = df[column_to_process].values.tolist()
    with open("temp.txt", 'w') as temp_file:
        temp_file.write('\n'.join(str(item) for item in text_to_process))

    processed_text = text2term.preprocess_tagged_terms(file_path="temp.txt", template_path="resources/templates.txt",
                                                       blocklist_path=BLOCKLIST_REGEXPS,
                                                       blocklist_char="-")
    os.remove("temp.txt")
    df[PROCESSED_TEXT_COL] = ""
    df["Tags"] = ""
    for term in processed_text:
        df.loc[df[column_to_process] == term.get_original_term(), PROCESSED_TEXT_COL] = term.get_term()
        tags = ','.join(term.get_tags())
        df.loc[df[column_to_process] == term.get_original_term(), "Tags"] = tags

    bl_df = pd.read_csv(BLOCKLIST_TABLE)
    for index, row in bl_df.iterrows():
        df[PROCESSED_TEXT_COL] = np.where((df["Variable"] == row["names"]) & (df["Table"] == row["tables"]),
                                          "-", df[PROCESSED_TEXT_COL])
    df = mark_phenotpyes(df)
    if save_processed_table:
        df.to_csv(input_file, sep="\t", index=False, mode="w")
    print("...done")
    return df

def mark_phenotpyes(df):
    df[PHENOTYPE_COL] = np.where(df[PROCESSED_TEXT_COL] == "-", "FALSE", "TRUE")
    return df

if __name__ == '__main__':
    preprocess(input_file="../metadata/nhanes_variables.tsv", column_to_process="SASLabel", save_processed_table=True,
               input_file_col_separator="\t")

