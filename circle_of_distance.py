import math


# https://stochasticcoder.com/2016/04/06/python-custom-distance-radius-with-basemap/

class Circle_of_distance():

    def create_circle_with_radius(self, lat, lon, radius_in_km):
        lon_array = []
        lat_array = []
        for brng in range(0, 360):
            lat2, lon2 = self.getLocation(lat, lon, brng, radius_in_km)
            lat_array.append(lat2)
            lon_array.append(lon2)

        return lon_array, lat_array

    def getLocation(self, lat1, lon1, brng, radius_in_km):
        lat1 = lat1 * math.pi / 180.0
        lon1 = lon1 * math.pi / 180.0
        # earth radius
        R = 6378.1  # Km
        radius_in_km = radius_in_km / R

        brng = (brng / 90) * math.pi / 2

        lat2 = math.asin(math.sin(lat1) * math.cos(radius_in_km)
                         + math.cos(lat1) * math.sin(radius_in_km) * math.cos(brng))

        lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(radius_in_km)
                                 * math.cos(lat1), math.cos(radius_in_km) - math.sin(lat1) * math.sin(lat2))

        lon2 = 180.0 * lon2 / math.pi
        lat2 = 180.0 * lat2 / math.pi

        return lat2, lon2
