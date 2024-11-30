# The haversine function was taken from Geegs4geeks website: 
# https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/ 
import math

# function to calculate distance between two points.
def haversine(loc1:tuple, loc2:tuple) -> float:
	# unpacking the tuple
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

# Driver code
if __name__ == "__main__":
	loc1 = (24.87425068007454, 46.82029724121094)
	loc2 = (24.90755801, 46.78645960)

	
	print(haversine(loc1, loc2), "K.M.")

# This code is contributed 
# by ChitraNayal
