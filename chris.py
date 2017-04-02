#!/usr/bin/env python3

from flask import Flask
from flask import request
import urllib.request
import json
from math import radians, cos, sin, asin, sqrt

map_range = 100
global dist
#uses haversine formula to calculate distance between points, returns true if within min distance
def calc(lat, long, ulat, ulong, mass): #returns true if within set distance
	if lat and long and lat != "0.000000" and long != "0.000000" and mass:
		lat, long, ulat, ulong = map(radians, [float(lat), float(long), float(ulat),float(ulong)])
		dlon = ulong - long
		dlat = ulat - lat
		a = sin(dlat/2)**2 + cos(lat) * cos(ulat) * sin(dlon/2)**2
		c = 2 * asin(sqrt(a))
		r = 3956
		dist = c*r
		return dist<map_range
	else:
		return 0

def convert_direction(degree):
	degree = str(degree)
	
	converted_degree = degree[:-1]

app = Flask(__name__)

@app.route("/search")
def search():
	user_latitude = request.args.get('lat')
	user_longitude = request.args.get('long')
	#meteors
	#user_latitude = 34.068921
	#user_longitude = -118.445181
	url = 'https://data.nasa.gov/api/views/gh4g-9sfh/rows.json?accessType=DOWNLOAD'
	response = urllib.request.urlopen(url)
	data = response.read()
	jdata = json.loads(data)
	n = len(jdata['data'])
	counter_radius = 0
	to_delete = []
	to_keep =[]
	kept_latlong = []
	for i in range(0, n):
		templat = jdata['data'][i][15]
		templong = jdata['data'][i][16]
		tempyear = jdata['data'][i][14]
		tempname = str(jdata['data'][i][8])
		tempname = str(tempname)
		tempmass = jdata['data'][i][12]
		smallest_mass = 10000000000
		index = 0
		for element in to_keep:
			if tempmass:
				if float(element[4]) < smallest_mass:
					smallest_mass = float(element[4])
					small_mass_index = int(index)
			index = index + 1
		latlongstring = str(templat) + str(templong)
		if calc(templat, templong, user_latitude, user_longitude, tempmass): 
			counter_radius = counter_radius + 1
			print (tempname, " ")
			if kept_latlong.count(latlongstring) < 1 and len(to_keep) > 10 and float(tempmass) >= smallest_mass:
				del to_keep[small_mass_index]
				to_keep.append(jdata['data'][i])
				kept_latlong.append(latlongstring)
			elif len(to_keep)<10:
				to_keep.append(jdata['data'][i])
				kept_latlong.append(latlongstring)
			#TODO keep or put in database?
		else:
			to_delete.append(tempname)
	print (len(to_keep),"whats to keep",  " ")
	#TODO Format and return values mattie needs
	json_strings = []
	for i in range(0, len(to_keep)):
		json_strings.append("{{ 'name': '{}', 'lat': '{}', 'lon': '{}', 'year': '{}', 'mass': '{}'}}".format(to_keep[i][8].replace("'", "\\'"), to_keep[i][15], to_keep[i][16], to_keep[i][14], to_keep[i][12]))
	json_array_contents = ",".join(json_strings)
	real_string = "[" + json_array_contents + "]"
	print (real_string, "real!", " ")

	#Shooting Stars
	url_shoot = 'https://data.nasa.gov/api/views/mc52-syum/rows.json?accessType=DOWNLOAD'
	response_shoot = urllib.request.urlopen(url)
	data_shoot = response_shoot.read()
	jdata_shoot = json.loads(data_shoot)
	n = len(jdata_shoot['data'])
	counter_keep_shoot = 0
	to_delete_shoot = []
	to_keep_shoot = []
	#for i in range(0,n):
	#	templat = jdata_shoot['data'][i][1]
	#	templong = jdata_shoot['data'][i][2]
	#	tempdate = jdata_shoot['data'][i][0]
	#	if calc(templat, templong, user_latitude, user_longitude):
	#		counter_keep_shoot = counter_keep_shoot + 1
	#		to_keep_shoot.append(tempdate)
	#	else:
	#		to_delete_shoot.append(tempdate)
	return real_string

#search()
@app.route("/")
def hello():
	return "Hello World"

@app.route("/sample")
def sample():
	return "[ { 'latitude': 124.121, 'longitude': 1231.121, 'event': 'meteorite', 'test': 'Chris is awesome' } ]"



if __name__ == "__main__":
	app.run(host='0.0.0.0')
