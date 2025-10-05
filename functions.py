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



def fetch_sentry_data_from_url(sentry_url):
    resp = requests.get(sentry_url)
    if resp.status_code != 200:
        raise RuntimeError(f"Sentry API request failed: {resp.status_code} - {resp.text}")
    sentry_response = resp.json()
    return sentry_response

def compute_mass_kg_from_diameter(estimated_diameter_meters, density_g_cm3=2.6):
    # Convert diameter from meters to centimeters
    diameter_cm = estimated_diameter_meters * 100
    radius_cm = diameter_cm / 2
    volume_cm3 = (4/3) * np.pi * (radius_cm ** 3)
    density_kg_m3 = density_g_cm3 * 1000  # Convert g/cm^3 to kg/m^3
    mass_kg = density_kg_m3 * (volume_cm3 / 1e6)  # Convert cm^3 to m^3 for mass calculation
    return mass_kg

def compute_kinetic_energy_Mt_from_mass_and_velocity(mass_kg, velocity_kph):
    velocity_m_s = velocity_kph / 3.6  # Convert km/h to m/s
    kinetic_energy_joules = 0.5 * mass_kg * (velocity_m_s ** 2)
    kinetic_energy_Mt = kinetic_energy_joules / 4.184e15  # Convert joules to megatons of TNT
    return kinetic_energy_Mt


def fetch_sentry_object_details_from_des(sentry_designation):
    # example: "https://ssd-api.jpl.nasa.gov/sentry.api?des=1997 TC25"
    url = "https://ssd-api.jpl.nasa.gov/sentry.api?des=" + sentry_designation
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f"Sentry API request failed: {resp.status_code} - {resp.text}")
    sentry_object_details_json = resp.json()    
    return sentry_object_details_json

    



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

    # hook into SBDB (ssd.jpl.nasa.gov) to get diameter, albedo, absolute magnitude, etc
    nasa_jpl_url = neo_response['nasa_jpl_url']
    absolute_magnitude_h = neo_response['absolute_magnitude_h']

    estimated_diameter_min_meters = neo_response['estimated_diameter']['meters']['estimated_diameter_min']  # in meters
    estimated_diameter_max_meters = neo_response['estimated_diameter']['meters']['estimated_diameter_max']  # in meters
    estimated_diameter_meters = (estimated_diameter_min_meters + estimated_diameter_max_meters) / 2  # average diameter in meters

    dates = []
    velocities_kph = []
    miss_dist_au = []
    miss_dist_km = []

    for event in neo_response['close_approach_data']:
        dates.append(event['close_approach_date'])
        velocities_kph.append(float(event['relative_velocity']['kilometers_per_hour']))
        miss_dist_au.append(float(event['miss_distance']['astronomical']))
        miss_dist_km.append(float(event['miss_distance']['kilometers']))

    # Hook into SENTRY??
    sentry_data_url = None
    sentry_dict = {}
    is_sentry_object = neo_response['is_sentry_object']
    if is_sentry_object:
        sentry_data_url = neo_response['sentry_data']
        sentry_json = fetch_sentry_data_from_url(sentry_data_url)
        print("hooking into sentry data...")
        print("\n")
        sentry_dict['spkId'] = sentry_json['spkId']
        sentry_dict['fullname'] = sentry_json['fullname']
        sentry_dict['designation'] = sentry_json['designation']
        sentry_dict['sentryId'] = sentry_json['sentryId']
        sentry_dict['v_infinity'] = sentry_json['v_infinity']  # in km/s
        sentry_dict['estimated_diameter'] = sentry_json['estimated_diameter']  # in meters
        sentry_dict['absolute_magnitude'] = sentry_json['absolute_magnitude']
        sentry_dict['palermo_scale_ave'] = sentry_json['palermo_scale_ave']
        sentry_dict['impact_probability'] = sentry_json['impact_probability']
        sentry_dict['is_active_sentry_object'] = sentry_json['is_active_sentry_object']
        sentry_dict['url_impact_details'] = sentry_json['url_impact_details']
        print("Sentry data obtained!")
        print("\n")

        # Let's go deeper... a hook within a hook... hookception... 
        # Access the Object Table for ENERGY and MASS directly, instead of computing.
        sentry_object_details_json = fetch_sentry_object_details_from_des(sentry_dict['designation'])
        #        
        print("hooking into sentry OBJECT data...")
        print("\n")            
        sentry_object_details_dict = {}
        if 'data' in sentry_object_details_json and len(sentry_object_details_json['data']) > 0:        
            sentry_object_details_dict['mass'] = sentry_object_details_json['summary']['mass']  # in kg
            sentry_object_details_dict['v_inf'] = sentry_object_details_json['summary']['v_inf']  # in km/s
            sentry_object_details_dict['ip'] = sentry_object_details_json['summary']['ip']  # impact probability
            sentry_object_details_dict['energy'] = sentry_object_details_json['summary']['energy']  # in Mt
            sentry_object_details_dict['diameter'] = sentry_object_details_json['summary']['diameter']  # in km
            print("Sentry OBJECT data obtained!")
            print("\n")

    return {
        'designation': designation,
        'name': name,
        'id': neo_id,
        'neo_reference_id': neo_ref_id,
        'nasa_jpl_url': nasa_jpl_url,
        'absolute_magnitude_h': absolute_magnitude_h,
        'estimated_diameter_meters': estimated_diameter_meters,
        'close_approach_date': dates,
        'relative_velocity_kph': velocities_kph,
        'miss_distance_au': miss_dist_au,
        'miss_distance_km': miss_dist_km,
        'is_sentry_object': is_sentry_object,
        'sentry_data_url': sentry_data_url,
        'sentry_dict': sentry_dict,
        'sentry_object_dict': sentry_object_details_dict if is_sentry_object else {None}
    }

# TEST ASTEROID: 3092161
neo3092161 = fetch_asteroid_dictionary("3092161", api_key)
for key, value in neo3092161.items():
    if key != 'sentry_dict' or 'sentry_object_dict':
        print(f"{key}: {value}")
    elif key == 'sentry_dict':
        print("\nSentry Data:")
        for sentry_key, sentry_value in neo3092161['sentry_dict'].items():
            print(f"{sentry_key}: {sentry_value}")
    elif key == 'sentry_object_dict':
        print("\nSentry Object Data:")
        for sentry_obj_key, sentry_obj_value in neo3092161['sentry_object_dict'].items():
            print(f"{sentry_obj_key}: {sentry_obj_value}")


print(neo3092161)
print(neo3092161['sentry_dict'])

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

... to qualify as potentially hazardous objects with a diameter greater than 140 meters (absolute magnitude brighter than 22).

<https://www.jpl.nasa.gov/keeping-an-eye-on-space-rocks/>
Potentially hazardous asteroids are about 150 meters (almost 500 feet) or larger




<https://ssd-api.jpl.nasa.gov/doc/sentry.html> SENTRY CALCULATIONS:
mass 	    kg 	This estimate assumes a uniform spherical body with the computed diameter and a mass density of 2.6 g/cm3. 
                    The mass estimate is somewhat more rough than the diameter estimate, but generally will be accurate to within a factor of three.

diameter 	km 	This is an estimate based on the absolute magnitude, usually assuming a uniform spherical body 
                    with visual albedo of 0.154 (in accordance with the Palermo Scale) but sometimes using actual measured values if these are available. 
                    Since the albedo is rarely measured, the diameter estimate should be considered only approximate, but in most cases will be accurate 
                    to within a factor of two.

v_imp 	    km/s 	Velocity at atmospheric entry.        

energy 	    Mt 	    The kinetic energy at impact: 0.5 × mass × v_imp2, measured in Megatons of TNT.

h 	  	     .      Absolute Magnitude, a measure of the intrinsic brightness of the object.

ip 	  	    .       The cumulative probability that the tabulated impact will occur. The probability computation is complex and depends on a number 
                    of assumptions that are difficult to verify. For these reasons the stated probability can easily be inaccurate by a factor of a few, 
                    and occasionally by a factor of ten or more.

                    

PLAN:
- 1) add diameter to field from API

    1.5) compute diameter as per SSD using absolute magnitude and albedo (albedo fround from the LINK TO SSD)
        <https://cneos.jpl.nasa.gov/tools/ast_size_est.html>
        "diameter d in km as a function of absolute magnitude H and geometric albedo a is given by the following equation:
        
                d = 10[ 3.1236 - 0.5 log10(a) - 0.2H ]
        "


- 2) assume density to be 2.6 g/cm3, as per SSD dataset
        -- or pull as a field from SSD also..

- 3) calculate mass in kg = Density * Volume = 2.6 g/cm3 * (4/3) * pi * (radius in cm)^3
         ** remember that's RADIUS in CM^3

- 4) calculate kinetic energy = 0.5 * mass * velocity^2
         ** remember velocity here is in M/S **
         "The formula for kinetic energy is: Ek = 1/2 * m * V2 where Ek stands for kinetic energy and is measured in joules, 
            m stands for mass and is measured in kilograms, and V stands for velocity and is measured in m/s."
            <https://www.grc.nasa.gov/www/k-12/BGA/Mike/energy_act.htm>


- 5) ignore IP?

"""

sentry_url = "https://ssd-api.jpl.nasa.gov/sentry.api"
sentry_response = requests.get(sentry_url)
sentry_data = sentry_response.json()


api_key = "EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
neo_url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"
response = requests.get(neo_url)
neo_data = response.json()

print(neo_data)

sentry_objects = []  # Create an empty list to hold sentry objects

neo_objects = neo_data.get('near_earth_objects', [])  # Get all NEOs safely

for neo in neo_objects:
    # Check if the 'is_sentry_object' field exists and is True
    if 'is_sentry_object' in neo:
        if neo['is_sentry_object'] is True:
            sentry_objects.append(neo)  # Add to list if condition satisfied

# Now sentry_objects contains only NEOs flagged as sentry objects

print("Number of sentry objects:", len(sentry_objects))
for obj in sentry_objects[:10]:  # Print first 10 for example
    print(obj.get('designation'), obj.get('name'))


for neo in neo_data['near_earth_objects']:
    designation = neo.get('designation') or neo.get('des') or neo.get('name')
    print("NEO designation:", designation)


all_neos = []
sentry_objects = [] 
page = 0

while True:
    page += 1
    url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?page={page}&size=20&api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"NEO API request failed: {response.status_code} - {response.text}")
    data = response.json()
    neos = data['near_earth_objects']
    print(f"Fetched page {page}, retrieved {len(neos)} NEOs.")
    if not neos:
        print("No more NEOs to fetch.")
        break
    for neo in neos:
        if neo.get('is_sentry_object'):
            print(f"Found sentry object: {neo.get('designation')} - {neo.get('name')}")
            sentry_objects.append(neo)
        all_neos.append(neo)
    print(f"Total NEOs as of page {page}: {len(all_neos)}")
    print(f"Total Sentry Objects as of page {page}: {len(sentry_objects)}")
    time.sleep(.1)  # To respect API rate limits

print(f"Total NEOs retrieved: {len(all_neos)}")
print(f"Total Sentry Objects found: {len(sentry_objects)}")
print("First 5 Sentry Objects:")
for obj in sentry_objects[:5]:
    print(f"Designation: {obj.get('designation')}, Name: {obj.get('name')}, ID: {obj.get('id')}")


"""
Fetched page 150, retrieved 20 NEOs.
Found sentry object: 1997 TC25 - (1997 TC25)

"""

print(sentry_objects[:3])  # Print first 3 sentry objects
"""
>>> print(sentry_objects[:3])  # Print first 3 sentry objects
[{'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/3092161?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, 'id': '3092161', 'neo_reference_id': '3092161', 'name': '(1997 TC25)', 'designation': '1997 TC25', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3092161', 'absolute_magnitude_h': 24.6, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 0.0319561887, 'estimated_diameter_max': 0.0714562102}, 'meters': {'estimated_diameter_min': 31.9561886721, 'estimated_diameter_max': 71.4562101727}, 'miles': {'estimated_diameter_min': 0.0198566489, 'estimated_diameter_max': 0.0444008168}, 'feet': {'estimated_diameter_min': 104.8431420431, 'estimated_diameter_max': 234.436392583}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [{'close_approach_date': '1991-08-09', 'close_approach_date_full': '1991-Aug-09 13:32', 'epoch_date_close_approach': 681744720000, 'relative_velocity': {'kilometers_per_second': '6.1923702086', 'kilometers_per_hour': '22292.5327508979', 'miles_per_hour': '13851.7129195788'}, 'miss_distance': {'astronomical': '1.9421978894', 'lunar': '755.5149789766', 'kilometers': '290548667.372735578', 'miles': '180538570.2206758564'}, 'orbiting_body': 'Juptr'}, {'close_approach_date': '1997-09-28', 'close_approach_date_full': '1997-Sep-28 10:59', 'epoch_date_close_approach': 875444340000, 'relative_velocity': {'kilometers_per_second': '10.2014510592', 'kilometers_per_hour': '36725.2238131337', 'miles_per_hour': '22819.625874333'}, 'miss_distance': {'astronomical': '0.0157100706', 'lunar': '6.1112174634', 'kilometers': '2350193.099309622', 'miles': '1460342.2749399036'}, 'orbiting_body': 'Earth'}], 'orbital_data': {'orbit_id': '14', 'orbit_determination_date': '2021-04-14 20:47:39', 'first_observation_date': '1997-09-30', 'last_observation_date': '1997-10-23', 'data_arc_in_days': 23, 'observations_used': 17, 'orbit_uncertainty': '8', 'minimum_orbit_intersection': '.00125108', 'jupiter_tisserand_invariant': '3.110', 'epoch_osculation': '2450734.5', 'eccentricity': '.6237435118226394', 'semi_major_axis': '2.593161402058156', 'inclination': '.2508939890646966', 'ascending_node_longitude': '17.90811376225372', 'orbital_period': '1525.256027624467', 'perihelion_distance': '.9756938024154823', 'perihelion_argument': '321.5229962507606', 'aphelion_distance': '4.21062900170083', 'perihelion_time': '2450700.019560591526', 'mean_anomaly': '8.138278401943696', 'mean_motion': '.2360259480899658', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'APO', 'orbit_class_description': 'Near-Earth asteroid orbits which cross the Earth’s orbit similar to that of 1862 Apollo', 'orbit_class_range': 'a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU'}}, 'is_sentry_object': True, 'sentry_data': 'http://api.nasa.gov/neo/rest/v1/neo/sentry/3092161?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, {'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/3054334?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, 'id': '3054334', 'neo_reference_id': '3054334', 'name': '(2000 SB45)', 'designation': '2000 SB45', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3054334', 'absolute_magnitude_h': 24.5, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 0.0334622374, 'estimated_diameter_max': 0.0748238376}, 'meters': {'estimated_diameter_min': 33.4622374455, 'estimated_diameter_max': 74.8238376074}, 'miles': {'estimated_diameter_min': 0.0207924639, 'estimated_diameter_max': 0.0464933628}, 'feet': {'estimated_diameter_min': 109.7842471007, 'estimated_diameter_max': 245.4850393757}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [{'close_approach_date': '2000-10-02', 'close_approach_date_full': '2000-Oct-02 16:17', 'epoch_date_close_approach': 970503420000, 'relative_velocity': {'kilometers_per_second': '8.221884036', 'kilometers_per_hour': '29598.7825295964', 'miles_per_hour': '18391.5324001262'}, 'miss_distance': {'astronomical': '0.0237100925', 'lunar': '9.2232259825', 'kilometers': '3546979.335502975', 'miles': '2203990.758672055'}, 'orbiting_body': 'Earth'}], 'orbital_data': {'orbit_id': '12', 'orbit_determination_date': '2021-04-14 20:58:41', 'first_observation_date': '2000-09-27', 'last_observation_date': '2000-09-29', 'data_arc_in_days': 2, 'observations_used': 18, 'orbit_uncertainty': '8', 'minimum_orbit_intersection': '.00131562', 'jupiter_tisserand_invariant': '4.331', 'epoch_osculation': '2451816.5', 'eccentricity': '.3984067237006788', 'semi_major_axis': '1.563631668746629', 'inclination': '3.666634808821013', 'ascending_node_longitude': '195.5839104381994', 'orbital_period': '714.1675507648072', 'perihelion_distance': '.9406702985266594', 'perihelion_argument': '216.1874584454603', 'aphelion_distance': '2.186593038966598', 'perihelion_time': '2451853.738631850092', 'mean_anomaly': '341.2286242189572', 'mean_motion': '.5040833899754664', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'APO', 'orbit_class_description': 'Near-Earth asteroid orbits which cross the Earth’s orbit similar to that of 1862 Apollo', 'orbit_class_range': 'a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU'}}, 'is_sentry_object': True, 'sentry_data': 'http://api.nasa.gov/neo/rest/v1/neo/sentry/3054334?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, {'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/3141528?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, 'id': '3141528', 'neo_reference_id': '3141528', 'name': '(2002 UV36)', 'designation': '2002 UV36', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3141528', 'absolute_magnitude_h': 26.5, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 0.0133215567, 'estimated_diameter_max': 0.0297879063}, 'meters': {'estimated_diameter_min': 13.3215566698, 'estimated_diameter_max': 29.7879062798}, 'miles': {'estimated_diameter_min': 0.008277629, 'estimated_diameter_max': 0.0185093411}, 'feet': {'estimated_diameter_min': 43.7058959846, 'estimated_diameter_max': 97.7293544391}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [{'close_approach_date': '2002-11-01', 'close_approach_date_full': '2002-Nov-01 02:59', 'epoch_date_close_approach': 1036119540000, 'relative_velocity': {'kilometers_per_second': '8.1209772063', 'kilometers_per_hour': '29235.5179427905', 'miles_per_hour': '18165.8139128411'}, 'miss_distance': {'astronomical': '0.0160932202', 'lunar': '6.2602626578', 'kilometers': '2407511.463360974', 'miles': '1495958.2548264812'}, 'orbiting_body': 'Earth'}], 'orbital_data': {'orbit_id': '10', 'orbit_determination_date': '2021-04-14 21:37:10', 'first_observation_date': '2002-10-31', 'last_observation_date': '2002-11-14', 'data_arc_in_days': 14, 'observations_used': 32, 'orbit_uncertainty': '7', 'minimum_orbit_intersection': '.00507937', 'jupiter_tisserand_invariant': '3.218', 'epoch_osculation': '2461000.5', 'eccentricity': '.5985504573548238', 'semi_major_axis': '2.455904533555942', 'inclination': '2.866014970780044', 'ascending_node_longitude': '32.56352393133176', 'orbital_period': '1405.774457608633', 'perihelion_distance': '.9859217517762475', 'perihelion_argument': '356.1504332794245', 'aphelion_distance': '3.925887315335635', 'perihelion_time': '2461014.227536646864', 'mean_anomaly': '356.4845618256019', 'mean_motion': '.256086599135111', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'APO', 'orbit_class_description': 'Near-Earth asteroid orbits which cross the Earth’s orbit similar to that of 1862 Apollo', 'orbit_class_range': 'a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU'}}, 'is_sentry_object': True, 'sentry_data': 'http://api.nasa.gov/neo/rest/v1/neo/sentry/3141528?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}]
>>>


"""

sentry_objects = [{'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/3092161?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, 'id': '3092161', 'neo_reference_id': '3092161', 'name': '(1997 TC25)', 'designation': '1997 TC25', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3092161', 'absolute_magnitude_h': 24.6, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 0.0319561887, 'estimated_diameter_max': 0.0714562102}, 'meters': {'estimated_diameter_min': 31.9561886721, 'estimated_diameter_max': 71.4562101727}, 'miles': {'estimated_diameter_min': 0.0198566489, 'estimated_diameter_max': 0.0444008168}, 'feet': {'estimated_diameter_min': 104.8431420431, 'estimated_diameter_max': 234.436392583}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [{'close_approach_date': '1991-08-09', 'close_approach_date_full': '1991-Aug-09 13:32', 'epoch_date_close_approach': 681744720000, 'relative_velocity': {'kilometers_per_second': '6.1923702086', 'kilometers_per_hour': '22292.5327508979', 'miles_per_hour': '13851.7129195788'}, 'miss_distance': {'astronomical': '1.9421978894', 'lunar': '755.5149789766', 'kilometers': '290548667.372735578', 'miles': '180538570.2206758564'}, 'orbiting_body': 'Juptr'}, {'close_approach_date': '1997-09-28', 'close_approach_date_full': '1997-Sep-28 10:59', 'epoch_date_close_approach': 875444340000, 'relative_velocity': {'kilometers_per_second': '10.2014510592', 'kilometers_per_hour': '36725.2238131337', 'miles_per_hour': '22819.625874333'}, 'miss_distance': {'astronomical': '0.0157100706', 'lunar': '6.1112174634', 'kilometers': '2350193.099309622', 'miles': '1460342.2749399036'}, 'orbiting_body': 'Earth'}], 'orbital_data': {'orbit_id': '14', 'orbit_determination_date': '2021-04-14 20:47:39', 'first_observation_date': '1997-09-30', 'last_observation_date': '1997-10-23', 'data_arc_in_days': 23, 'observations_used': 17, 'orbit_uncertainty': '8', 'minimum_orbit_intersection': '.00125108', 'jupiter_tisserand_invariant': '3.110', 'epoch_osculation': '2450734.5', 'eccentricity': '.6237435118226394', 'semi_major_axis': '2.593161402058156', 'inclination': '.2508939890646966', 'ascending_node_longitude': '17.90811376225372', 'orbital_period': '1525.256027624467', 'perihelion_distance': '.9756938024154823', 'perihelion_argument': '321.5229962507606', 'aphelion_distance': '4.21062900170083', 'perihelion_time': '2450700.019560591526', 'mean_anomaly': '8.138278401943696', 'mean_motion': '.2360259480899658', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'APO', 'orbit_class_description': 'Near-Earth asteroid orbits which cross the Earth’s orbit similar to that of 1862 Apollo', 'orbit_class_range': 'a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU'}}, 'is_sentry_object': True, 'sentry_data': 'http://api.nasa.gov/neo/rest/v1/neo/sentry/3092161?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, {'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/3054334?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, 'id': '3054334', 'neo_reference_id': '3054334', 'name': '(2000 SB45)', 'designation': '2000 SB45', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3054334', 'absolute_magnitude_h': 24.5, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 0.0334622374, 'estimated_diameter_max': 0.0748238376}, 'meters': {'estimated_diameter_min': 33.4622374455, 'estimated_diameter_max': 74.8238376074}, 'miles': {'estimated_diameter_min': 0.0207924639, 'estimated_diameter_max': 0.0464933628}, 'feet': {'estimated_diameter_min': 109.7842471007, 'estimated_diameter_max': 245.4850393757}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [{'close_approach_date': '2000-10-02', 'close_approach_date_full': '2000-Oct-02 16:17', 'epoch_date_close_approach': 970503420000, 'relative_velocity': {'kilometers_per_second': '8.221884036', 'kilometers_per_hour': '29598.7825295964', 'miles_per_hour': '18391.5324001262'}, 'miss_distance': {'astronomical': '0.0237100925', 'lunar': '9.2232259825', 'kilometers': '3546979.335502975', 'miles': '2203990.758672055'}, 'orbiting_body': 'Earth'}], 'orbital_data': {'orbit_id': '12', 'orbit_determination_date': '2021-04-14 20:58:41', 'first_observation_date': '2000-09-27', 'last_observation_date': '2000-09-29', 'data_arc_in_days': 2, 'observations_used': 18, 'orbit_uncertainty': '8', 'minimum_orbit_intersection': '.00131562', 'jupiter_tisserand_invariant': '4.331', 'epoch_osculation': '2451816.5', 'eccentricity': '.3984067237006788', 'semi_major_axis': '1.563631668746629', 'inclination': '3.666634808821013', 'ascending_node_longitude': '195.5839104381994', 'orbital_period': '714.1675507648072', 'perihelion_distance': '.9406702985266594', 'perihelion_argument': '216.1874584454603', 'aphelion_distance': '2.186593038966598', 'perihelion_time': '2451853.738631850092', 'mean_anomaly': '341.2286242189572', 'mean_motion': '.5040833899754664', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'APO', 'orbit_class_description': 'Near-Earth asteroid orbits which cross the Earth’s orbit similar to that of 1862 Apollo', 'orbit_class_range': 'a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU'}}, 'is_sentry_object': True, 'sentry_data': 'http://api.nasa.gov/neo/rest/v1/neo/sentry/3054334?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, {'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/3141528?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}, 'id': '3141528', 'neo_reference_id': '3141528', 'name': '(2002 UV36)', 'designation': '2002 UV36', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=3141528', 'absolute_magnitude_h': 26.5, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 0.0133215567, 'estimated_diameter_max': 0.0297879063}, 'meters': {'estimated_diameter_min': 13.3215566698, 'estimated_diameter_max': 29.7879062798}, 'miles': {'estimated_diameter_min': 0.008277629, 'estimated_diameter_max': 0.0185093411}, 'feet': {'estimated_diameter_min': 43.7058959846, 'estimated_diameter_max': 97.7293544391}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [{'close_approach_date': '2002-11-01', 'close_approach_date_full': '2002-Nov-01 02:59', 'epoch_date_close_approach': 1036119540000, 'relative_velocity': {'kilometers_per_second': '8.1209772063', 'kilometers_per_hour': '29235.5179427905', 'miles_per_hour': '18165.8139128411'}, 'miss_distance': {'astronomical': '0.0160932202', 'lunar': '6.2602626578', 'kilometers': '2407511.463360974', 'miles': '1495958.2548264812'}, 'orbiting_body': 'Earth'}], 'orbital_data': {'orbit_id': '10', 'orbit_determination_date': '2021-04-14 21:37:10', 'first_observation_date': '2002-10-31', 'last_observation_date': '2002-11-14', 'data_arc_in_days': 14, 'observations_used': 32, 'orbit_uncertainty': '7', 'minimum_orbit_intersection': '.00507937', 'jupiter_tisserand_invariant': '3.218', 'epoch_osculation': '2461000.5', 'eccentricity': '.5985504573548238', 'semi_major_axis': '2.455904533555942', 'inclination': '2.866014970780044', 'ascending_node_longitude': '32.56352393133176', 'orbital_period': '1405.774457608633', 'perihelion_distance': '.9859217517762475', 'perihelion_argument': '356.1504332794245', 'aphelion_distance': '3.925887315335635', 'perihelion_time': '2461014.227536646864', 'mean_anomaly': '356.4845618256019', 'mean_motion': '.256086599135111', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'APO', 'orbit_class_description': 'Near-Earth asteroid orbits which cross the Earth’s orbit similar to that of 1862 Apollo', 'orbit_class_range': 'a (semi-major axis) > 1.0 AU; q (perihelion) < 1.017 AU'}}, 'is_sentry_object': True, 'sentry_data': 'http://api.nasa.gov/neo/rest/v1/neo/sentry/3141528?api_key=EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w'}]

for obj in sentry_objects:
    print(obj.keys())
    # print its neo_id, name, designation, absolute_magnitude_h, sentry_data link
    print(f"NEO ID: {obj.get('id')}, Name: {obj.get('name')}, Designation: {obj.get('designation')}, Absolute Magnitude: {obj.get('absolute_magnitude_h')}, Sentry Data Link: {obj.get('sentry_data')}")
    # hook into the sentry_data link
    sentry_link = obj.get('sentry_data')
    if sentry_link:
        sentry_response = requests.get(sentry_link)
        if sentry_response.status_code == 200:
            sentry_info = sentry_response.json()
            print("Sentry Info Keys:", sentry_info.keys())
            print("\n")
            # print from sentry_info: spkId, designation, sentryId, fullname, potential_impacts, impact_probability, v_infinity, absolute_magnitude, estimated_diameter, average_lunar_distance:
            print(f"spkId: {sentry_info.get('spkId')}, designation: {sentry_info.get('designation')}, sentryId: {sentry_info.get('sentryId')}, fullname: {sentry_info.get('fullname')}, potential_impacts: {sentry_info.get('potential_impacts')}, impact_probability: {sentry_info.get('impact_probability')}, v_infinity (km/s): {sentry_info.get('v_infinity')}, absolute_magnitude: {sentry_info.get('absolute_magnitude')}, estimated_diameter (km): {sentry_info.get('estimated_diameter')}, average_lunar_distance: {sentry_info.get('average_lunar_distance')}")
            print("\n")
            # print the link to url_impact_details
            print(f"url_impact_details: {sentry_info.get('url_impact_details')}")
            print("\n")
            # print energy (Mt), diameter (km), mass (kg), v_imp (km/s)
            print(f"energy (Mt): {sentry_info.get('energy')}, diameter (km): {sentry_info.get('diameter')}, mass (kg): {sentry_info.get('mass')}, v_imp (km/s): {sentry_info.get('v_imp')}")
            print("\n")
            # print from url_impact_details:
            impact_details_link = sentry_info.get('url_impact_details')
            if impact_details_link:
                impact_response = requests.get(impact_details_link)
                if impact_response.status_code == 200:
                    impact_info = impact_response.json()
                    print("Impact Info Keys:", impact_info.keys())
                    print("\n")
                    # print out the impact_info keys
                    for key, value in impact_info.items():
                        print(f"{key}: {value}")
                        print("\n")
                else:
                    print(f"Failed to fetch impact details: {impact_response.status_code}")
            # print out the close_approach_data from the sentry_info
            if 'close_approach_data' in sentry_info:
                for cad in sentry_info['close_approach_data']:
                    print("\n")
                    print(f"Close Approach Date: {cad.get('close_approach_date')}, Miss Distance (km): {cad.get('miss_distance', {}).get('kilometers')}, Relative Velocity (km/h): {cad.get('relative_velocity', {}).get('kilometers_per_hour')}")
        else:
            print(f"Failed to fetch sentry data: {sentry_response.status_code}")