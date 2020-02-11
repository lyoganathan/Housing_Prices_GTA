import requests
import pandas as pd
import os

#Scrape realtor.ca for house prices
#https://stackoverflow.com/questions/53140904/cloning-api-call-from-an-existing-website-in-postman
#https://curl.trillworks.com/
#Other examples: https://gist.github.com/DenisCarriere/1a56ac970f91e90e9f46
#https://github.com/bmitch/realtorscraper

def get_from_dict(dataDict, mapList):
    # Function to get value in nested dictionaries using lists:
    # See https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
    for k in mapList: dataDict = dataDict[k]
    return dataDict

def get_minmax_latlong(zoom,center):
    # Trying to get latitude max/min and longitude max/min just using zoom and center
    # Fit an exponential decay curve to how latitude/longitude vary with zoom (a * 0.5 **zoom + b)
    # Got parameters with curve_fit from scipy.optimize
    zoom = int(zoom)
    lat_len = 497.617 * 0.5**zoom - 0.00013
    long_len = 1448.433 * 0.5**zoom + 0.000005
    center_lat, center_long = [float(x) for x in center.split(',')]
    # Find min and max and save as five decimal point string
    latmin = "{0:.5f}".format(center_lat - lat_len/2)
    latmax = "{0:.5f}".format(center_lat + lat_len/2)
    longmin = "{0:.5f}".format(center_long - long_len/2)
    longmax = "{0:.5f}".format(center_long + long_len/2)
    return latmax, longmax, latmin, longmin


def scrape_realtor(city,zoom,center,path):

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
    # 12 is max per page, so gonna have to loop and send some requests

    latmax, longmax, latmin, longmin = get_minmax_latlong(zoom,center)

    data = {
        'ZoomLevel': zoom,
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
    # into environment
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

    data_df.to_csv(os.path.join(path,'{}_Realtor.csv'.format(city)),index=False)
    errors_df = pd.DataFrame(errors)
    errors_df.to_csv(os.path.join(path,'{}_Realtor_errors.csv'.format(city)),index=False)


if __name__ == '__main__':
    scrape_realtor('HamiltonEast','12','43.182935,-79.698982','data')
    scrape_realtor('HamiltonWest','13','43.269680,-79.911580','data')
    scrape_realtor('HamiltonSouth','12','43.178655,-80.052600','data')
    scrape_realtor('Brantford','11','43.178625,-80.583035','data')
    scrape_realtor('Cambridge','11','43.421220,-80.520550','data')
    scrape_realtor('Waterdown','12','43.360685,-79.990120','data')
    scrape_realtor('Milton','12','43.481128,-79.990120','data')
    scrape_realtor('Burlington','12','43.360900,-79.637533','data')
    scrape_realtor('Oakville','12','43.481100,-79.636500','data')
    scrape_realtor('MissisaugaEast', '13', '43.571212,-79.584143','data')
    scrape_realtor('MissisaugaWest','13','43.571212,-79.760783','data')
    scrape_realtor('Georgetown','12','43.602077,-79.990120','data')
    scrape_realtor('MissisaugaNorth', '12','43.661467,-79.642334','data')
    scrape_realtor('Brampton','12','43.781062,-79.666023','data')
    scrape_realtor('Toronto', '13', '43.658907,-79.387145','data')
    scrape_realtor('York', '13', '43.718613,-79.387145','data')
    scrape_realtor('NorthYork', '13', '43.778507,-79.402251','data')
    scrape_realtor('Vaughn', '12', '43.844237,-79.666023','data')
    scrape_realtor('MarkhamWest', '13', '43.838341,-79.402251','data')
    scrape_realtor('KingCity', '12', '43.962973,-79.666023','data')
    scrape_realtor('RichmondHill', '13', '43.897745,-79.402251','data')
    scrape_realtor('Aurora', '12', '43.962973,-79.303817','data')
    scrape_realtor('Newmarket', '12', '44.065686,-79.460372','data')
    scrape_realtor('Scarborough', '11', '43.704964,-78.985457','data')
    scrape_realtor('MarkhamEast', '12', '43.879187,-79.150252','data')
    scrape_realtor('Oshawa', '12', '43.906155,-78.798003','data')


# For reference, this was the manual way before get_fromdict, but sometimes some fields will be missing
# Check the DOM to see how this json is organized. A bunch of subfields hidden in there.
# data_df['MlsNumber'][count] = full_data['Results'][house]["MlsNumber"]
# data_df['PostalCode'][count] = full_data['Results'][idx]['PostalCode']
# data_df['Price'][count] = full_data['Results'][idx]['Property']['Price']
# data_df['RealEstateCompany'][count] = full_data['Results'][idx]['Individual'][0]["Organization"]["Name"]
