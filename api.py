"""A note on security: were I putting users' actual billing addresses in this app, I'd absolutely 
require OAuth2. Since I could see an OAuth2 implentation taking up half of the time I have to complete
this excercise, I'm making the call to use http only to get geocoords. Since the app theoretically deals 
with users' financial and physical location info, it would be **very important** to use a secured 
connection, IMO.

Please see https://developers.google.com/maps/documentation/geocoding/ for more info."""

import os
import requests
import json
from urllib import quote_plus

API_KEY = os.environ['GEOCODING_API_KEY']

BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?'

def get_geocoords(address):
	"""Function should take an address object and return a tuple 
	with the latitude and longitude of that address. If none is found,
	the coordinates of the city and state should be returned."""
	# Could potentially implement this recursively?
	# Am implementing with a quick if/else check to get it working,
	# because "premature optimization is the root of all evil"

	print "this was passed to get_geocoords(): ", address
	# import pdb; pdb.set_trace()

	# extract the parameter values from the address obj since they are stored as unicode:
	address_str = str(address.name)
	city_str = str(address.city_name.city_name)
	state_str = str(address.state_abbreviation.state_abbreviation)

	dict_response = call_api(address=address_str, city=city_str, state=state_str)

	# Check that we have results before extracting coords:
	if dict_response['status'] == 'OK':
		return extract_coords(dict_response)

	# If no results, call API again for just city and state
	elif dict_response['status'] == 'ZERO_RESULTS':
		dict_response = call_api(city=address.city_name, state=address.state_abbreviation)
			# Still need to make sure that second attempt worked:
		if dict_response['status'] == 'OK':
			return extract_coords(dict_response)
	
	else:
		# In the unlikely event there aren't geocoords for the state, return hardcoded coords
		# for USA. In production, I might instrument this to notify someone that the
		# geocoord API might be down or have another issue requiring an engineer's attention.
		#
		# Alternatively, I could keep geocoords for each state in the DB, and return 
		# the stored state coordinates instead of making repeated API calls. This would also be a 
		# better implementation because I could then easily put address.name 
		# and its corresponding geocoords in its own table in the event that, say, 
		# there are many different users living in the same apartment building. 
		# This would avoid the repetition of querying geocoords for the same street address each time.

		return (37.6,-95.665)


def call_api(**kwargs):
	"""Function to fetch geocoordinates for any combination of parameters accepted
	by the Google Geocoding API."""

	# Put args in the right order for the API:
	parameters = kwargs['address'] + kwargs['city'] + kwargs['state']

	encoded_parameters = quote_plus(parameters)
	api_request = BASE_URL + "address=" + encoded_parameters + "&key=" + API_KEY

	response = requests.get(api_request)
	# response_string = str(response.content)
	dict_response = json.loads(response.content)
	print dict_response

	return dict_response


def extract_coords(json_as_dict):
	"""Nice little helper function to pull the geocoords out of a 
	Google Geolocation API json response."""
	lat = json_as_dict['results'][0]['geometry']['location']['lat']
	lon = json_as_dict['results'][0]['geometry']['location']['lng']
	coords = (lat, lon)
	return coords


def main():
	pass


if __name__ == '__main__':
	main()
