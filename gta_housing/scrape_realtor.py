import requests
import pandas as pd

#Scrape realtor.ca for house prices
#https://stackoverflow.com/questions/53140904/cloning-api-call-from-an-existing-website-in-postman
#https://curl.trillworks.com/
#Other examples: https://gist.github.com/DenisCarriere/1a56ac970f91e90e9f46
#https://github.com/bmitch/realtorscraper

def get_from_dict(dataDict, mapList):
    # Function to get value in nested directories using lists:
    # See https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
    for k in mapList: dataDict = dataDict[k]
    return dataDict

def scrape_realtor(city,latmax,longmax,latmin,longmin):

    headers = {
        'Origin': 'https://www.realtor.ca',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
        'Referer': 'https://www.realtor.ca/map',
        'Connection': 'keep-alive',
    }

    # Can find longitude latitude info by searching realtor then copying from url
    # Max is 600 results (50x12), gotta move the screen and zoom to make sure only 600 results
    # Markham: LatitudeMax=43.94939&LongitudeMax=-79.10857&LatitudeMin=43.82938&LongitudeMin=-79.46219
    # 12 is max per page, so gonna have to loop and send some requests

    data = {
        'ZoomLevel': '12',
        'LatitudeMax': latmax,
        'LongitudeMax': longmax,
        'LatitudeMin': latmin,
        'LongitudeMin': longmin,
        'CurrentPage': '1',
        'PropertyTypeGroupID': '1',
        'PropertySearchTypeId': '1',
        'TransactionTypeId': '2',
        'PriceMin': '0',
        'PriceMax': '0',
        'BedRange': '0-0',
        'BathRange': '0-0',
        'RecordsPerPage': '12',
        'ApplicationId': '1',
        'CultureId': '1',
        'Version': '7.0',
        'BuildingTypeId': '1', #This searches for just houses
        'Sort': '6-D' #Rearranges from new to old
    }

    # Optional: use tor. Need Tor expert bundle and start tor.exe for this to work - requires install of requests[socks]
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }

    #This gets the data. Problem is only get's max of 600 results... Need to constrain search area to make sure its less
    #than 600 results. Doing Houses only and sort from newest to oldest
    response = requests.post('https://api2.realtor.ca/Listing.svc/PropertySearch_Post', headers=headers, data=data,
                             proxies=proxies)
    full_data = response.json()

    #Get number of pages
    num_pages = full_data["Paging"]["TotalPages"]
    # Empty pandas dataframe
    col_names = ["MlsNumber","PostalCode","Price","PropertyType","Address","Longitude","Latitude","BuildingType",
                 "Bathrooms","Bedrooms","Stories","Size","RealEstateCompany"]
    n_rows = num_pages*12
    data_df = pd.DataFrame(columns=col_names, index=range(n_rows))

    #Make sure this is same order as col_names
    key_list = [['MlsNumber'],['PostalCode'],['Property','Price'],['Property','Type'],['Property','Address','AddressText'],
                ['Property','Address','Longitude'],['Property','Address','Latitude'],['Building','Type'],
                ['Building','BathroomTotal'],['Building','Bedrooms'],['Building','StoriesTotal'],["Land","SizeTotal"],
                ["Individual",0,"Organization","Name"]]

    # Initialize counter:
    house_idx = 0
    # Initialize errors:
    errors = []

    # Taking fields of interest into dataframe:

    for page in range(num_pages):
        data["CurrentPage"] = page + 1  # Python starts at 0, Mls listings start at 1
        # Get request again (first time it will be redundent)
        response = requests.post('https://api2.realtor.ca/Listing.svc/PropertySearch_Post', headers=headers, data=data,
                                 proxies=proxies)
        full_data = response.json()
        for result in range(len(full_data['Results'])):
            for col_idx in range(len(col_names)):
                try:
                    data_df[col_names[col_idx]][house_idx] = get_from_dict(full_data['Results'][result],key_list[col_idx])
                except KeyError as e:  # Some houses are missing info
                    errors.append("MlsNumber: {0}, Missing {1}".format(data_df['MlsNumber'][house_idx],e))

            house_idx += 1

    data_df.to_csv("{}_Realtor.csv".format(city),index=False)
    errors_df = pd.DataFrame(errors)
    errors_df.to_csv("{}_Realtor_errors.csv".format(city),index=False)


if __name__ == '__main__':
    scrape_realtor('Newmarket','44.08096','-79.37338','44.02113','-79.55019')
    scrape_realtor('Aurora','44.03539','-79.26343','43.91557','-79.61705')
    scrape_realtor('Richmondhill','43.93192','-79.33885','43.87193','-79.51566')
    scrape_realtor('Markham','43.94939','-79.10857','43.82938','-79.46219')
    scrape_realtor('Scarborough','43.83790','-79.11305','43.71768','-79.46668')
    scrape_realtor('Vaughn','43.87710','-79.36083','43.75696','-79.71445')
    scrape_realtor('Mississauga_1','43.56214','-79.58170','43.50178','79.75851')
    scrape_realtor('Mississauga_2','43.61461','-79.57140','43.55431','-79.74821')
    scrape_realtor('Brampton_1','43.71318','-79.68863','43.65297','-79.86544')
    scrape_realtor('Brampton_2', '43.77686', '-79.60907','43.71671','-79.78588')
    scrape_realtor('Toronto_1','43.69914','-79.32921','43.63892','-79.50602')
    scrape_realtor('Toronto_2','43.76536','-79.35623','43.70521','-79.53304')
    scrape_realtor('Oshawa', '43.98303','-78.57739','43.86310','-78.93101')
    scrape_realtor('Pickering','43.93781','-78.87574','43.81778','-79.22936')






# For reference, this was the manual way before get_fromdict, but sometimes some fields will be missing
# Check the DOM to see how this json is organized. A bunch of subfields hidden in there.
# data_df['MlsNumber'][count] = full_data['Results'][house]["MlsNumber"]
# data_df['PostalCode'][count] = full_data['Results'][idx]['PostalCode']
# data_df['Price'][count] = full_data['Results'][idx]['Property']['Price']
# data_df['RealEstateCompany'][count] = full_data['Results'][idx]['Individual'][0]["Organization"]["Name"]