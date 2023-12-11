import pandas as pd
import numpy as np
import text2term
import os

BLOCKLIST_LOC = "resources/table_blocklist.csv"

def preprocess(input_file, column_to_process, save_processed_table=False, input_file_col_separator=","):
	print("Preprocessing metadata table...")
	df = pd.read_csv(input_file, sep=input_file_col_separator)
	text_to_process = df[column_to_process].values.tolist()
	with open("temp.txt", 'w') as temp_file:
		temp_file.write('\n'.join(text_to_process))

	processed_text = text2term.preprocess_tagged_terms("temp.txt", "resources/templates.txt", \
                                                       blocklist_path="resources/term_blocklist.txt", blocklist_char="-")
	os.remove("temp.txt")
	processed_text_col = "ProcessedText"
	df[processed_text_col] = ""
	df["Tags"] = ""
	for term in processed_text:
		df.loc[df[column_to_process] == term.get_original_term(), processed_text_col] = term.get_term()
		tags = ','.join(term.get_tags())
		df.loc[df[column_to_process] == term.get_original_term(), "Tags"] = tags

	bl_df = pd.read_csv(BLOCKLIST_LOC)
	for index, row in bl_df.iterrows():
		df[processed_text_col] = np.where((df["Variable"] == row["names"]) & (df["Table"] == row["tables"]), \
										"-", df[processed_text_col])

	if save_processed_table:
		df.to_csv(input_file, sep="\t", index=False, mode="w")
	print("...done")
	return df


if __name__ == '__main__':
	preprocess(input_file="../metadata/nhanes_variables.tsv", column_to_process="SASLabel", save_processed_table=True,
			   input_file_col_separator="\t")
