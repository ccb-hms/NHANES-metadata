import pandas as pd
import text2term

def main():
	df = pd.read_csv("../metadata/nhanes_variables.csv")
	text_to_process = df["SAS Label"].values.tolist()
	processed_text = text2term.preprocess_terms(text_to_process, "templates.txt")
	df["Processed Text"] = processed_text
	df.to_csv("nhanes_variables_processed.csv", index=False)

if __name__ == '__main__':
	main()