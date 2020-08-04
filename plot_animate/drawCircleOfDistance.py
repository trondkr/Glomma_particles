import math
from osgeo import ogr, osr

# https://stochasticcoder.com/2016/04/06/python-custom-distance-radius-with-basemap/

def createCircleAroundWithRadius(lat, lon, radiusKM):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    latArray = []
    lonArray = []
 
    for brng in range(0,360):
        lat2, lon2 = getLocation(lat,lon,brng,radiusKM)
        latArray.append(lat2)
        lonArray.append(lon2)

    return lonArray,latArray


def getLocation(lat1, lon1, brng, radiusKM):
    lat1 = lat1 * math.pi/ 180.0
    lon1 = lon1 * math.pi / 180.0
    #earth radius
    R = 6378.1 #Km
    radiusKM = radiusKM/R

    brng = (brng / 90)* math.pi / 2

    lat2 = math.asin(math.sin(lat1) * math.cos(radiusKM) 
   + math.cos(lat1) * math.sin(radiusKM) * math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(radiusKM)
   * math.cos(lat1),math.cos(radiusKM)-math.sin(lat1)*math.sin(lat2))

    lon2 = 180.0 * lon2/ math.pi
    lat2 = 180.0 * lat2/ math.pi

    return lat2, lon2