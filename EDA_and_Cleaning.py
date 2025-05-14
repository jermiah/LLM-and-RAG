from IPython.display import display
import pandas as pd
def get_most_frequent_rows(df, column_name):
    """
    Prints the most frequent value(s) in a column and all rows that contain it.
    
    Args:
        df (pd.DataFrame): The DataFrame to analyze.
        column_name (str): The name of the column to check.
    """
    if column_name not in df.columns:
        print(f"Column '{column_name}' does not exist in the DataFrame.")
        return
    
    top_value = df[column_name].mode()[0]
    rows = df[df[column_name] == top_value]
    freq = len(rows)

    print(f"\nMost frequent value in column '{column_name}' (appears {freq} times):\n")
    print("--------------------------------------------------------------")
    display(top_value)
    print("--------------------------------------------------------------")
    print("\nCorresponding rows:\n")
    display(rows)

import re

def clean_question_text(text):
    if not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub(r'\\n|\n', ' ', text)  # remove newlines
    text = re.sub(r'\\+', '', text)      # remove escape slashes
    text = re.sub(r'\s+', ' ', text)     # normalize whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove non-ASCII

    # Remove prefixed question numbers: "10.14 " or "6.2.1 " or "Q1. "
    text = re.sub(r'^\d+(\.\d+)*\s+', '', text)
    text = re.sub(r'^Q\d+\.\s*', '', text, flags=re.IGNORECASE)

    # Remove survey-specific instructions: (Single selection allowed), [5.2], etc.
    text = re.sub(r'\(.*?selection allowed.*?\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\d+(\.\d+)?\]', '', text)

    # Remove trailing "copy" or other export artifacts
    text = re.sub(r'\s+copy$', '', text, flags=re.IGNORECASE)

    return text.strip()