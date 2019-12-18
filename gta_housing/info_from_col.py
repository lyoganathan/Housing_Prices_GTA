# Converts some string columns to just numbers using regex
import pandas as pd
import re
from fractions import Fraction

# Function to sum digits to single number
# https://www.geeksforgeeks.org/finding-sum-of-digits-of-a-number-until-sum-becomes-single-digit/
def digsum(n):
    if n == 0:
        return 0
    if n % 9 == 0:
        return 9
    else:
        return n % 9

def new_cols(data_path):
    data_df = pd.read_csv(data_path)

    # Remove $ and , from price
    data_df['Price'] = data_df['Price'].str.replace(r'[$,]', '')

    # Bedrooms are often listed in format like 3+1
    # Split bedroom column into full bedrooms and other rooms
    data_df['FullBedrooms'] = data_df['Bedrooms'].str.extract('(\d)+')
    data_df['OtherRooms'] = data_df['Bedrooms'].str.extract('(\d) \+ (\d)')[1]
    # Change NA to 0, if bedrooms was just one number, then we say 0 other rooms
    data_df.loc[data_df['OtherRooms'].isna(),'OtherRooms'] = 0

    # Get House Number (112 would be 5, 45 would be 9)
    data_df['HouseNumber'] = data_df['Address'].str.extract('(\d*)')
    data_df['HouseNumber'] = pd.to_numeric(data_df['HouseNumber'], downcast='integer')

    data_df['NumSum'] = data_df['HouseNumber'].apply(digsum)

    # Calculate Lot Area
    ## Convert metres to square feet
    ## Convert acres to square feet

    data_df["LotArea"] = ""

    #Regex for feet
    p1 = re.compile('([0-9.]+ x [0-9.]+ FT)')
    p1a = re.compile('([0-9.]+) x')
    p1b = re.compile('([0-9.]+) FT')
    #Regex for meters
    p2 = re.compile('([0-9.]+ x [0-9.]+ M)')
    p2a = re.compile('([0-9.]+) x')
    p2b = re.compile('([0-9.]+) M')
    #Regex for acres:
    p3 = re.compile('([0-9./]+) ac',re.IGNORECASE)

    # Search for measurment in feet, meters then acres
    for i in range(0,len(data_df["Size"])):
        # f = lambda x: bool(p.search(x))
        if pd.isna(data_df["Size"][i]):
            pass
        elif bool(p1.search(data_df["Size"][i])):
            data_df.loc[i,"LotArea"] = \
                float(p1a.search(data_df["Size"][i]).group(1)) * \
                float(p1b.search(data_df["Size"][i]).group(1))
        elif bool(p2.search(data_df["Size"][i])):
            data_df.loc[i,"LotArea"] = \
                float(p2a.search(data_df["Size"][i]).group(1)) * \
                float(p2b.search(data_df["Size"][i]).group(1))
        elif bool(p3.search(data_df["Size"][i])):
            data_df.loc[i,"LotArea"] = float(Fraction(p3.search(data_df["Size"][i]).group(1))) * 43560
        else:
            pass
            # Skipping other weird conventions for now...
            # About 100 get skipped
            # print("Skipping {}".format(data_df["Size"][i]))

    data_df.to_csv("data/all_houses.csv",index=False)


if __name__ == '__main__':
    new_cols(r"C:\Users\Laagi\Documents\projects\realtor-app\all_houses.csv")