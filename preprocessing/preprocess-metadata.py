import pandas as pd
import text2term

def main():
	df = pd.read_csv("../metadata/nhanes_variables.csv")
	text_to_process = df["SAS Label"].values.tolist()

	processed_text = text2term.preprocess_terms(text_to_process, "templates.txt", \
								blacklist_path="term_blacklist.txt", blacklist_char="-")
	df["Processed Text"] = processed_text

	bl_df = pd.read_csv("table_blacklist.csv")
	for index, row in bl_df.iterrows():
		df.loc[df['Table'] == row['tables'], "Processed Text"] = "-"

	df.to_csv("nhanes_variables_processed.csv", index=False)

if __name__ == '__main__':
	main()