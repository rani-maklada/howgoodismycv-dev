import pandas as pd
from collections import Counter
import os
# import nltk
# from nltk.tokenize import RegexpTokenizer

# # Ensure you have the necessary NLTK package and tokenizer models
# nltk.download('punkt')

def process_and_rank_skills(job_file, directory):
    # Construct the path to the input file
    input_path = os.path.join(directory, job_file)
    # Split the filename to insert '_ranked' before the '.csv'
    base_name, ext = os.path.splitext(job_file)
    ranked_file_name = f"{base_name}_ranked{ext}"
    output_path = os.path.join(directory, ranked_file_name)
    
    if os.path.exists(input_path):
        print(f"Processing skills from {job_file}...")
        # Read the CSV file into a DataFrame
        skills_df = pd.read_csv(input_path)

        # Drop rows with missing values in 'Skills' column
        # skills_df.dropna(subset=['Skills'], inplace=True)
        skills_df['Skills'] = skills_df['Skills'].str.lower()
        
        all_skills_list = skills_df['Skills'].str.split(",").sum()
        # Use Counter to get the most common skills
        skills_counter = Counter(all_skills_list)

        # Convert to a DataFrame for better visualization and sorting
        skills_frequency_df = pd.DataFrame(skills_counter.items(), columns=['Skill', 'Count'])

        # Sort the skills by frequency
        skills_frequency_df = skills_frequency_df.sort_values(by='Count', ascending=False).reset_index(drop=True)

        # Save the ranked skills data to a new CSV file
        skills_frequency_df.to_csv(output_path, index=False)

        print(f"Ranked skills data saved to '{ranked_file_name}'.")
    else:
        print(f"File {job_file} does not exist. Skipping...")

# Specify the directory and job files as before
directory = r'C:\Users\rani\OneDrive\Documents\GitLab\howgoodismycv-dev'
job_files = ['Java_Developer_skills.csv', 'Data_Analyst_skills.csv', 'Python_Developer_skills.csv', 'Automation_Engineer_skills.csv']

# Process each file
for job_file in job_files:
    process_and_rank_skills(job_file, directory)
