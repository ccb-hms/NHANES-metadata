import pandas as pd
import numpy as np
import text2term
import os

def main(input_file, column_to_process, save_processed_table=False):
	df = pd.read_csv(input_file)
	text_to_process = df[column_to_process].values.tolist()
	with open("temp.txt", 'w') as temp_file:
		temp_file.write('\n'.join(text_to_process))

	processed_text = text2term.preprocess_tagged_terms("temp.txt", "resources/templates.txt", \
                                                       blacklist_path="resources/term_blacklist.txt", blacklist_char="-")
	os.remove("temp.txt")

	df["Processed Text"] = ""
	df["Tags"] = ""
	for term in processed_text:
		df.loc[df[column_to_process] == term.get_original_term(), "Processed Text"] = term.get_term()
		tags = ','.join(term.get_tags())
		df.loc[df[column_to_process] == term.get_original_term(), "Tags"] = tags
	
	bl_df = pd.read_csv("resources/table_blacklist.csv")
	for index, row in bl_df.iterrows():
		df["Processed Text"] = np.where((df["Variable"] == row["names"]) & (df["Table"] == row["tables"]), \
										"-", df["Processed Text"])

	if save_processed_table:
		df.to_csv("nhanes_variables_processed.csv", index=False)
	return df


if __name__ == '__main__':
	main(input_file="../metadata/nhanes_variables.csv", column_to_process="SAS Label", save_processed_table=True)
