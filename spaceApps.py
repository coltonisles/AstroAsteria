import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
# from IPython.display import clear_output
import time
import requests
import pandas as pd


api_key = "EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"

image_folder = "C:\\Users\\Batman\\NASA-Space-Apps"


# This is the NASA NEO (Near Earth Object) API endpoint for browsing asteroids:
# https://api.nasa.gov/neo/rest/v1/neo/browse?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w

url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"
response = requests.get(url)
data = response.json()
# print(data)   # Outputs the 40,000 object data from that API NEO dataset

"""
This is 1 single NEO:

links	
next	"http://api.nasa.gov/neo/rest/v1/neo/browse?page=1&size=20&api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
self	"http://api.nasa.gov/neo/rest/v1/neo/browse?page=0&size=20&api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
page	
size	20
total_elements	40680
total_pages	2034
number	0
near_earth_objects	
0	
links	
self	"http://api.nasa.gov/neo/rest/v1/neo/2000433?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
id	"2000433"
neo_reference_id	"2000433"
name	"433 Eros (A898 PA)"
name_limited	"Eros"
designation	"433"
nasa_jpl_url	"https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=2000433"
absolute_magnitude_h	10.39
estimated_diameter	
kilometers	
estimated_diameter_min	22.2103282246
estimated_diameter_max	49.6638037128
meters	{ estimated_diameter_min: 22210.3282245866, estimated_diameter_max: 49663.8037127578 }
miles	{ estimated_diameter_min: 13.8008538592, estimated_diameter_max: 30.8596473768 }
feet	{ estimated_diameter_min: 72868.5332523526, estimated_diameter_max: 162938.9937729642 }
is_potentially_hazardous_asteroid	false
close_approach_data	
0	
close_approach_date	"1900-12-27"
close_approach_date_full	"1900-Dec-27 01:30"
epoch_date_close_approach	-2177879400000
relative_velocity	
kilometers_per_second	"5.5786191875"
kilometers_per_hour	"20083.0290749201"
miles_per_hour	"12478.8132604691"
miss_distance	
astronomical	"0.3149291693"
lunar	"122.5074468577"
kilometers	"47112732.928149391"
miles	"29274494.7651919558"
orbiting_body	"Earth"
1	{ close_approach_date: "1907-11-05", close_approach_date_full: "1907-Nov-05 03:31", epoch_date_close_approach: -1961526540000, … }
2	{ close_approach_date: "1917-04-20", close_approach_date_full: "1917-Apr-20 21:19", epoch_date_close_approach: -1663036860000, … }
3	{ close_approach_date: "1924-03-05", close_approach_date_full: "1924-Mar-05 22:13", epoch_date_close_approach: -1446083220000, … }
4	{ close_approach_date: "1931-01-30", close_approach_date_full: "1931-Jan-30 04:07", epoch_date_close_approach: -1228247580000, … }
5	{ close_approach_date: "1938-01-13", close_approach_date_full: "1938-Jan-13 22:04", epoch_date_close_approach: -1008726960000, … }
6	{ close_approach_date: "1944-11-27", close_approach_date_full: "1944-Nov-27 01:41", epoch_date_close_approach: -791936340000, … }
7	{ close_approach_date: "1961-04-04", close_approach_date_full: "1961-Apr-04 09:08", epoch_date_close_approach: -275928720000, … }
8	{ close_approach_date: "1968-02-11", close_approach_date_full: "1968-Feb-11 13:46", epoch_date_close_approach: -59566440000, … }
9	{ close_approach_date: "1975-01-23", close_approach_date_full: "1975-Jan-23 07:39", epoch_date_close_approach: 159694740000, … }
10	{ close_approach_date: "1981-12-29", close_approach_date_full: "1981-Dec-29 08:05", epoch_date_close_approach: 378461100000, … }
11	{ close_approach_date: "1988-11-06", close_approach_date_full: "1988-Nov-06 14:56", epoch_date_close_approach: 594831360000, … }
12	{ close_approach_date: "2005-03-08", close_approach_date_full: "2005-Mar-08 22:07", epoch_date_close_approach: 1110319620000, … }
13	{ close_approach_date: "2012-01-31", close_approach_date_full: "2012-Jan-31 11:01", epoch_date_close_approach: 1328007660000, … }
14	{ close_approach_date: "2019-01-15", close_approach_date_full: "2019-Jan-15 06:01", epoch_date_close_approach: 1547532060000, … }
15	{ close_approach_date: "2025-11-30", close_approach_date_full: "2025-Nov-30 02:18", epoch_date_close_approach: 1764469080000, … }
16	{ close_approach_date: "2042-04-06", close_approach_date_full: "2042-Apr-06 19:02", epoch_date_close_approach: 2280423720000, … }
17	{ close_approach_date: "2049-02-12", close_approach_date_full: "2049-Feb-12 05:38", epoch_date_close_approach: 2496721080000, … }
18	{ close_approach_date: "2056-01-24", close_approach_date_full: "2056-Jan-24 11:03", epoch_date_close_approach: 2715937380000, … }
19	{ close_approach_date: "2062-12-31", close_approach_date_full: "2062-Dec-31 08:25", epoch_date_close_approach: 2934779100000, … }
20	{ close_approach_date: "2069-11-08", close_approach_date_full: "2069-Nov-08 21:29", epoch_date_close_approach: 3151171740000, … }
21	{ close_approach_date: "2086-03-11", close_approach_date_full: "2086-Mar-11 22:55", epoch_date_close_approach: 3666725700000, … }
22	{ close_approach_date: "2093-01-31", close_approach_date_full: "2093-Jan-31 15:47", epoch_date_close_approach: 3884255220000, … }
23	{ close_approach_date: "2100-01-16", close_approach_date_full: "2100-Jan-16 11:39", epoch_date_close_approach: 4103782740000, … }
24	{ close_approach_date: "2106-12-04", close_approach_date_full: "2106-Dec-04 02:22", epoch_date_close_approach: 4320872520000, … }
25	{ close_approach_date: "2123-04-10", close_approach_date_full: "2123-Apr-10 05:51", epoch_date_close_approach: 4836779460000, … }
26	{ close_approach_date: "2130-02-14", close_approach_date_full: "2130-Feb-14 22:11", epoch_date_close_approach: 5053011060000, … }
27	{ close_approach_date: "2137-01-25", close_approach_date_full: "2137-Jan-25 14:12", epoch_date_close_approach: 5272179120000, … }
28	{ close_approach_date: "2144-01-03", close_approach_date_full: "2144-Jan-03 10:26", epoch_date_close_approach: 5491103160000, … }
29	{ close_approach_date: "2150-11-12", close_approach_date_full: "2150-Nov-12 07:12", epoch_date_close_approach: 5707523520000, … }
30	{ close_approach_date: "2167-03-16", close_approach_date_full: "2167-Mar-16 05:30", epoch_date_close_approach: 6223152600000, … }
31	{ close_approach_date: "2174-02-03", close_approach_date_full: "2174-Feb-03 01:30", epoch_date_close_approach: 6440520600000, … }
32	{ close_approach_date: "2181-01-17", close_approach_date_full: "2181-Jan-17 20:55", epoch_date_close_approach: 6660046500000, … }
33	{ close_approach_date: "2187-12-06", close_approach_date_full: "2187-Dec-06 23:28", epoch_date_close_approach: 6877265280000, … }
orbital_data	
orbit_id	"659"
orbit_determination_date	"2021-05-24 17:55:05"
first_observation_date	"1893-10-29"
last_observation_date	"2021-05-13"
data_arc_in_days	46582
observations_used	9130
orbit_uncertainty	"0"
minimum_orbit_intersection	".148353"
jupiter_tisserand_invariant	"4.582"
epoch_osculation	"2461000.5"
eccentricity	".2228359407071628"
semi_major_axis	"1.458120998474684"
inclination	"10.82846651399785"
ascending_node_longitude	"304.2701025753316"
orbital_period	"643.1151986547006"
perihelion_distance	"1.13319923411471"
perihelion_argument	"178.9297536744151"
aphelion_distance	"1.783042762834657"
perihelion_time	"2461088.831287055474"
mean_anomaly	"310.5543277370992"
mean_motion	".5597752949285997"
equinox	"J2000"
orbit_class	
orbit_class_type	"AMO"
orbit_class_description	"Near-Earth asteroid orbits similar to that of 1221 Amor"
orbit_class_range	"1.017 AU < q (perihelion) < 1.3 AU"
is_sentry_object	false
"""

# Find potentially hazardous asteroids from the key 'is_potentially_hazardous_asteroid'
hazardous_asteroids = []
for obj in data['near_earth_objects']:
    if obj['is_potentially_hazardous_asteroid']:
        hazardous_asteroids.append(obj)
    if len(hazardous_asteroids) == 5:
        break

# Print their names and IDs
for asteroid in hazardous_asteroids:
    print(f"Name: {asteroid['name']}, ID: {asteroid['id']}")

# # OUTPUTS:
# Name: 1566 Icarus (1949 MA), ID: 2001566
# Name: 1620 Geographos (1951 RA), ID: 2001620
# Name: 1862 Apollo (1932 HA), ID: 2001862


# -------------------------------------------------------------------- #
# -------------------------------------------------------------------- #
# Now, we could access those specific objects by ID for futher details

# TODO: -- COULD SYNC THIS WITH THE ABOVE TASK, i.e. store the output from hazardous_asteroids and loop through them.

# TRY TO ISOLATE DATA FOR ICARUS
asteroid_id = "2001566"
url = f"https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={api_key}"

response = requests.get(url)
icarus_data = response.json()

# Print all data (or access specific fields)
print(icarus_data)


# Output of data for ICARUS (2001566)
"""
links	
self	"http://api.nasa.gov/neo/rest/v1/neo/2001566?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
id	"2001566"
neo_reference_id	"2001566"
name	"1566 Icarus (1949 MA)"
name_limited	"Icarus"
designation	"1566"
nasa_jpl_url	"https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=2001566"
absolute_magnitude_h	16.53
estimated_diameter	
kilometers	
estimated_diameter_min	1.313877806
estimated_diameter_max	2.9379200884
meters	
estimated_diameter_min	1313.877806011
estimated_diameter_max	2937.9200883689
miles	
estimated_diameter_min	0.8164055662
estimated_diameter_max	1.8255383432
feet	
estimated_diameter_min	4310.6228610732
estimated_diameter_max	9638.8457427242
is_potentially_hazardous_asteroid	true
close_approach_data	
0	
close_approach_date	"1902-06-11"
close_approach_date_full	"1902-Jun-11 20:20"
epoch_date_close_approach	-2131933200000
relative_velocity	
kilometers_per_second	"27.0080561011"
kilometers_per_hour	"97229.0019638462"
miles_per_hour	"60414.3206924799"
miss_distance	
astronomical	"0.0844842162"
lunar	"32.8643601018"
kilometers	"12638658.792139494"
miles	"7853298.4111492572"
orbiting_body	"Earth"
1	
close_approach_date	"1914-08-09"
close_approach_date_full	"1914-Aug-09 15:15"
epoch_date_close_approach	-1748162700000
relative_velocity	
kilometers_per_second	"42.8976350142"
kilometers_per_hour	"154431.4860509623"
miles_per_hour	"95957.719763166"
miss_distance	
astronomical	"0.0993900417"
lunar	"38.6627262213"
kilometers	"14868538.537531179"
miles	"9238881.4345971102"
orbiting_body	"Merc"
"""

# -- PLOT DISTANCE FROM EARTH OVER TIME -- #

# -- TODO: -- put this in a function
approaches = [entry for entry in icarus_data['close_approach_data'] if entry['orbiting_body'] == 'Earth']

dates = [entry['close_approach_date'] for entry in approaches]
distances = [float(entry['miss_distance']['kilometers']) for entry in approaches]

df = pd.DataFrame({'date': pd.to_datetime(dates), 'distance_km': distances})
df = df.sort_values('date')

plt.figure(figsize=(10, 5))
plt.plot(df['date'], df['distance_km'], marker='o')
plt.xlabel('Date')
plt.ylabel('Distance from Earth (km)')
plt.title('1566 Icarus: Proximity to Earth Over Time')
plt.grid(True)

# SAVE IMAGE OF PLOT TO LOCAL STORAGE
# TODO: change this location to work with WEB-APP
plt.savefig(f"{image_folder}/icarus_proximity.png")
plt.show()

# -- That was PLOT DISTANCE FROM EARTH OVER TIME -- #




