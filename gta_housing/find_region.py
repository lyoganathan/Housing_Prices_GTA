# Best to use conda to easily install pyproj
import pandas as pd
import shapefile as shp
from shapely.geometry import Point
from shapely.geometry import shape

def find_region(data_path,shapefile_path):
# https://gis.stackexchange.com/questions/250172/finding-out-if-coordinate-is-within-shapefile-shp-using-pyshp/250195

    data_df = pd.read_csv(data_path)

    ontario_map = shp.Reader(shapefile_path,encoding='ansi')

    all_regions = ontario_map.shapes() # get all the polygons
    all_records = ontario_map.records() # get all ridings

    #Create new empty coloumn elec_div
    data_df["ElectoralDiv"] = ""
    # Find if lat,long is within polygon boundry
    for house in range(len(data_df)):
        #Lat,long of each house
        point = (data_df["Longitude"][house],data_df["Latitude"][house])
        for i in range(len(all_regions)):
            boundary = all_regions[i]  # get a boundary polygon
            if Point(point).within(shape(boundary)):  # make a point and see if it's in the polygon
                data_df.loc[house, 'ElectoralDiv'] = all_records[i][1]  # This is electoral riding
                #print(all_records[i][1])
                break

    data_df.to_csv("data/all_houses.csv",index=False)

if __name__ == '__main__':
    find_region(r"data\all_houses.csv",r"data\fed_ont_WGS84.shp")