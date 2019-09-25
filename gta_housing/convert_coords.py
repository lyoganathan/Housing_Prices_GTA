# Best to use conda to easily install geopandas
import geopandas as gpd

#Shape files can be found here:
#https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-2011-eng.cfm

#Convert NAD83 to WGS84 aka epsg:3347 to epsg:4326

nad83 = gpd.read_file(r"data\lfed000b16a_e.shp",encoding='ansi')
wgs84 = nad83.to_crs({'init': 'epsg:4326'})

wgs84_ont =  wgs84[wgs84.PRNAME == "Ontario"]

wgs84_ont.to_file(r"data\fed_ont_WGS84.shp")

