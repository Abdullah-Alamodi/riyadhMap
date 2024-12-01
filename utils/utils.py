# The haversine function was taken from Geegs4geeks website: 
# https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/ 
import math

# function to calculate distance between two points.
def haversine(loc1:list, loc2:list) -> float:
	# unpacking the list
	lat1, lon1 = loc1
	lat2, lon2 = loc2
	dLat = (lat2 - lat1) * math.pi / 180.0
	dLon = (lon2 - lon1) * math.pi / 180.0

	# convert to radians
	lat1 = (lat1) * math.pi / 180.0
	lat2 = (lat2) * math.pi / 180.0

	# apply formulae
	a = (pow(math.sin(dLat / 2), 2) +
		pow(math.sin(dLon / 2), 2) *
			math.cos(lat1) * math.cos(lat2));
	rad = 6371
	c = 2 * math.asin(math.sqrt(a))
	return rad * c


# This code is contributed 
# by ChitraNayal
