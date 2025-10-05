import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import time
import requests
import pandas as pd
import os, io
import sys
api_key = "EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"

neo_url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"






# -- LARGER MORE FULL FUNCTION -- #
def fetch_asteroid_dictionary(neo_id, api_key):
    resp = requests.get(f"https://api.nasa.gov/neo/rest/v1/neo/{neo_id}?api_key={api_key}")
    if resp.status_code != 200:
        raise RuntimeError(f"NEO API request failed: {resp.status_code} - {resp.text}")
    neo_response = resp.json()
    
    designation = neo_response['designation']
    name = neo_response['name']
    neo_id = neo_response['id']
    neo_ref_id = neo_response['neo_reference_id']

    dates = []
    velocities_kph = []
    miss_dist_au = []
    miss_dist_km = []

    for event in neo_response['close_approach_data']:
        dates.append(event['close_approach_date'])
        velocities_kph.append(float(event['relative_velocity']['kilometers_per_hour']))
        miss_dist_au.append(float(event['miss_distance']['astronomical']))
        miss_dist_km.append(float(event['miss_distance']['kilometers']))

    return {
        'designation': designation,
        'name': name,
        'id': neo_id,
        'neo_reference_id': neo_ref_id,
        'close_approach_date': dates,
        'relative_velocity_kph': velocities_kph,
        'miss_distance_au': miss_dist_au,
        'miss_distance_km': miss_dist_km
    }

# -- plot the RETURNED DICTIONARY from 'fetch_asteroid_dictionary(neo_id, api_key)' -- #
def plot_asteroid_dictionary(asteroid_dict):
    plt.figure(figsize=(10, 5))
    plt.plot(asteroid_dict['close_approach_date'], asteroid_dict['miss_distance_km'], marker='o')
    plt.xlabel('Close Approach Date')
    plt.ylabel('Miss Distance (km)')
    plt.title(f'Asteroid {asteroid_dict["name"]} Miss Distance Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# -- EXAMPLE USAGE -- #
plot_asteroid_dictionary(fetch_asteroid_dictionary("2001566", api_key))







# ------------------------------------------------------------ #
# ------------------------------------------------------------ #

# -- FETCH / FIND ASTEROIDS BASED ON DIFFERENT CRITERIA -- #
# ------------------------------------------------------------ #


# Find potentially hazardous asteroids from the key 'is_potentially_hazardous_asteroid'
def fetch_hazardous_asteroids(api_key, limit=20):
    neo_url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"
    response = requests.get(neo_url)
    if response.status_code != 200:
        raise RuntimeError(f"NEO API request failed: {response.status_code} - {response.text}")
    data = response.json()
    
    hazardous_asteroids = []
    for obj in data['near_earth_objects']:
        if obj['is_potentially_hazardous_asteroid']:
            hazardous_asteroids.append(obj)
        if len(hazardous_asteroids) == limit:
            break
    
    return hazardous_asteroids

hazardous_asteroids = fetch_hazardous_asteroids(api_key, limit=5)
for asteroid in hazardous_asteroids:
    print(f"Designation: {asteroid['designation']}, Name: {asteroid['name']}, ID: {asteroid['id']}")
# -- this only seems to return 3 (THREE) 'hazardous' asteroids in the entire dataset... -- #


# -- Fetch asteroids that have 'approached Earth' (according to the API data) in the last 'n' days -- #
def fetch_nearby_asteroids(api_key, days=7):
    end_date = pd.Timestamp.today()
    start_date = end_date - pd.Timedelta(days=days)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    feed_url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_str}&end_date={end_str}&api_key={api_key}"
    response = requests.get(feed_url)
    if response.status_code != 200:
        raise RuntimeError(f"NEO Feed API request failed: {response.status_code} - {response.text}")
    data = response.json()
    
    nearby_asteroids = []
    for date in data['near_earth_objects']:
        for obj in data['near_earth_objects'][date]:
            nearby_asteroids.append(obj)
    
    return nearby_asteroids

# -- EXAMPLE USAGE -- #
nearby_asteroids = fetch_nearby_asteroids(api_key, days=7)
print(f"Found {len(nearby_asteroids)} asteroids approaching Earth in the last 7 days.")

for asteroid in nearby_asteroids[:15]:  # Print first 15
    asteroid_dict = fetch_asteroid_dictionary(asteroid['id'], api_key)
    print(f"Asteroid {asteroid_dict['name']} (neo_id: {asteroid_dict['neo_reference_id']}) approached on {asteroid_dict['close_approach_date'][0]} with miss distance {asteroid_dict['miss_distance_km'][0]} km.")
# That just prints the asteroid identifiers to the console:
"""
Asteroid (2008 SS) approached on 1906-10-02 with miss distance 24264564.149475206 km.
Asteroid (2015 HN9) approached on 1902-09-30 with miss distance 23160725.07452431 km.
Asteroid (2015 KT120) approached on 1935-05-11 with miss distance 64538544.87798536 km.
Asteroid (2021 SY3) approached on 1901-10-06 with miss distance 6508610.150578066 km.
Asteroid (2021 UJ1) approached on 1923-09-19 with miss distance 55059459.86577525 km.
Asteroid (2022 FL1) approached on 1949-05-17 with miss distance 63720865.629522026 km.
Asteroid (2022 QG41) approached on 1954-11-29 with miss distance 11782157.071317146 km.
Asteroid (2022 SK21) approached on 1901-12-23 with miss distance 38646978.185169995 km.
Asteroid (2022 VV) approached on 1904-09-13 with miss distance 13691349.622307826 km.
Asteroid (2023 RV12) approached on 1920-09-26 with miss distance 1581140.653449575 km.
Asteroid (2023 SV1) approached on 1936-10-01 with miss distance 58298111.214424714 km.
Asteroid (2023 XJ16) approached on 1918-12-30 with miss distance 71709225.57956995 km.
Asteroid (2024 TW) approached on 1915-10-06 with miss distance 10655639.437987436 km.
Asteroid (2025 QK10) approached on 2025-10-03 with miss distance 12572284.43126897 km.
Asteroid (2025 RH2) approached on 2025-10-03 with miss distance 7514832.23213637 km.
"""


# ---- WHAT I CONSIDER 'HAZARDOUS' == CLOSE ------ #

def fetch_asteroids_by_distance(api_key, max_distance_km=7500000):
    neo_url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"
    response = requests.get(neo_url)
    if response.status_code != 200:
        raise RuntimeError(f"NEO API request failed: {response.status_code} - {response.text}")
    data = response.json()
    
    close_asteroids = []
    for obj in data['near_earth_objects']:
        for event in obj['close_approach_data']:
            miss_distance_km = float(event['miss_distance']['kilometers'])
            if miss_distance_km <= max_distance_km:
                close_asteroids.append(obj)
                break  # No need to check further events for this asteroid
    
    return close_asteroids

# -- EXAMPLE USAGE -- #
close_asteroids = fetch_asteroids_by_distance(api_key, max_distance_km=7500000)
print(f"Found {len(close_asteroids)} asteroids within 7,500,000 km of Earth.")

# DISPLAY THE FIRST 5 ASTEROIDS AND PLOT THEIR DISTANCE DATA
for asteroid in close_asteroids[:5]:  # Print first 5
    print(f"Designation: {asteroid['designation']}, Name: {asteroid['name']}, ID: {asteroid['id']}")
    asteroid_dict = fetch_asteroid_dictionary(asteroid['id'], api_key)
    plot_asteroid_dictionary(asteroid_dict)
    print(f"Plotted asteroid {asteroid_dict['name']} with miss distance data.")
    

"""

NOTES ON KINETIC ENERGY CALCULATIONS:
---------------------------------------

<https://cneos.jpl.nasa.gov/sentry/vi.html>
Impact Energy (Mt)
    Kinetic energy at impact, based upon the computed absolute magnitude and impact velocity for the particular case, 
    and computed in accordance with the guidelines stated for the Palermo Technical Scale. Uncertainty in this value 
    is dominated by mass uncertainty and the stated value will generally be good to within a factor of three.


to qualify as potentially hazardous objects with a diameter greater than 140 meters (absolute magnitude brighter than 22).



"""