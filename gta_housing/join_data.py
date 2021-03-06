import pandas as pd
import os


# https://www.freecodecamp.org/news/how-to-combine-multiple-csv-files-with-8-lines-of-code-265183e0854/
# Loop through and get all house data
def join_data(path):
    # List comprehension to get all file names and combine into pandas dataframe
    filepaths = [os.path.join(path, file) for file in os.listdir(path) if file.endswith("Realtor.csv")]
    combined_data = pd.concat([pd.read_csv(file) for file in filepaths])

    # Drop duplicates
    combined_data.drop_duplicates(subset='MlsNumber', inplace=True)
    # Save to csv
    combined_data.to_csv(os.path.join(path, 'all_houses.csv'), index=False)

if __name__ == '__main__':
    join_data(r'data')