#TODO: Make the output graph better i.e. axis
#TODO: Make the get_damage() output string better ('.2f')
#TODO: Clean this code to make it NASA-worthy (https://www.cs.otago.ac.nz/cosc345/resources/nasa-10-rules.htm)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import time
import requests
import pandas as pd
import os, io
import sys
from datetime import datetime
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

api_key = "EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"
neo_url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"


# --------------------------------- #
# -- (useful) CALLABLE FUNCTIONS -- #
"""
#
# -- FETCHING FUNCTIONS -- #
#
multipage_fetch_NEOs(limit=100)
    - Populates the global list of NEOs found in the dataset
    - INPUT: (optional: 
                limit: int = maximum size of the list of NEOs)
#
fetch_asteroid_dictionary(neo_id, api_key)
    - get the USEFUL data from the NASA dataset
        - will automatically fetch additional data from SENTRY if it is a SENTRY object
    - INPUT: 'id' value from a neo object (from the "neo_url" dataset)
    - RETURNS:
        void    
        Outputs a MatPlotLib plot
#
#
# All other FETCH functions are called from the above FETCHers, where applicable
#
#
# -- DATA PRESENTATION -- #
#
print_all_data_for_asteroid_dict(asteroid_dict)
    == toString()
    - INPUT: dict == the return of:
            fetch_asteroid_dictionary(neo_id, api_key)
    - OUTPUT:
        str:    Formatted string of the useful data
#
get_next_approach_date_by_neoID(neo_id)
    Get the next upcoming 'close approach' according to the NASA API NEO dataset.
    Return the most recent approach if no predicted future approach.

        Input:
            str[] -> The 'neo_id' of a NEO from the NASA NEO API
        
        Return:
            datetime -> The next (or most recent) 'close-approach'
#
get_impactEnergy_Mt_from_neoID(neo_id) -> float:
        - INPUT: 'id' value from a neo object (from the "neo_url" dataset)
        - RETURNS: 
            float: Kinetic Energy on impact, in Megatons 
#
get_damageString_from_neoID(neo_ID)
        - INPUT: 'id' value from a neo object (from the "neo_url" dataset)
        - RETURNS: 
            str: A string blurb describing damage
#
get_damageData_from_neoID(neo_id)
        - INPUT: 'id' value from a neo object (from the "neo_url" dataset)
        - RETURNS:
            dict: 
                'name': name,
                'diameter': diameter_m,
                'mass': mass_kg,
                'velocity': velocity_infinity_kps,
                'energy': kinetic_Energy_Mt,
                'isPredicted': isPredicted,
                'ip': impact_probability
#
#
# -- PLOTTING -- #
#
plot_asteroid_dictionary(asteroid_dict)
#
#
# -- MATH -- #
#
compute_kinetic_energy_Mt_from_massKG_and_velocityKPH(mass_kg, velocity_kph, *, return_unit='Mt')
        - INPUT: mass (kilograms); velocity (km/h); [optional: Return Unit (options = "{'tons', 'joules', 'megatons'(default})]
        - RETURNS: 
            float: Energy, in Megatons (unless 'return_unit' has been specified)
#
compute_average_velocity(velocities_list)
        - INPUT: list (from the neo_object['close_approach_data'] velocities)
        - OUTPUT:
            float: averaged velocity (same units as input)
#
compute_mass_kg_from_diameter(estimated_diameter_meters, density_g_cm3=2.6)
        - INPUT: float -> diameter (meters); [optional: float -> density (g/cm^3)]
        - OUTPUT: 
            float: Mass (kilograms)
"""

# ----------------------------- #
# -- GLOBAL VARIABLE STORAGE -- #
# Preparing lists to store NEOs. Including separate lists for their IDs 
global_list_of_saved_NEO_IDs = []
global_list_of_saved_NEO_IDs_in_Sentry = []
global_neo_multipage_dataset = {}
global_page_to_browse = 0
"""
The main FETCH functions only pull 1 PAGE at a time, out of who knows how many pages...
So this below function browses all the pages, until a defined limit is reached. 
"""
def multipage_fetch_NEO_IDs(limit=5000):
    """
    This function browses *all* of the pages of the NASA NEO api dataset, and adds each NEO to 
    'list_of_saved_neos' until a defined limit (default = 100)

    If a NEO is ALSO in the NASA SENTRY API, it will be added to 'list_of_saved_neos_in_Sentry' for easy reference
    for simulations that would benefit from the Sentry data.

    Params:
    limit: int  = a max size for the list_of_neos[]

    Returns:
    N/A -> fills the gloabal lists
    """
    # Use the GLOBAL keyword to treat a variable as 'static', meaning data will persist instead of resetting each time this function runs
    global global_page_to_browse
    global global_list_of_saved_NEO_IDs
    global global_list_of_saved_NEO_IDs_in_Sentry 
    global global_neo_multipage_dataset

    while (len(global_list_of_saved_NEO_IDs) < limit):

        # Cycle through each page of the dataset
        global_page_to_browse += 1
        neo_api_url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?page={global_page_to_browse}&size=20&api_key={api_key}"
        r = requests.get(neo_api_url)
        if r.status_code != 200:
            raise RuntimeError(f"Sentry API request failed: {r.status_code} - {r.text}")
        page_of_NEOs_json = r.json()

        # Update GLOBAL DICT of multi-paged dataset to include this page
        # global_neo_multipage_dataset.update(page_of_NEOs_json)

        # Update GLOBAL lists of NEO 'id' values saved from the API dataset
        neo_asteroids = page_of_NEOs_json['near_earth_objects']
        for neo in neo_asteroids:
            global_list_of_saved_NEO_IDs.append(neo['id'])
            if neo['is_sentry_object']:
                global_list_of_saved_NEO_IDs_in_Sentry.append(neo['id'])
            if len(global_list_of_saved_NEO_IDs) >= limit:
                print("\n Declared size limit of global_list_of_saved_NEOs[] has been reached.")
                break
        
        # Avoid crashing NASA's server
        time.sleep(0.1)
        if len(global_list_of_saved_NEO_IDs) >= limit:
                print("\n Declared size limit of global_list_of_saved_NEOs[] has been reached.")
                break

# multipage_fetch_NEO_IDs(50)
# print(len(global_list_of_saved_NEO_IDs))
# print("\n")
# list_of_approach_dates





# TEST CODE
# print(len(global_list_of_saved_NEOs))
# print(global_list_of_saved_NEOs)

# print(len(global_list_of_saved_NEOs_in_Sentry))

# print(global_page_to_browse)

# print(len(global_list_of_saved_NEOs))
# print(len(global_list_of_saved_NEOs_in_Sentry))

# for entry in global_list_of_saved_NEOs_in_Sentry: 
#     print(global_list_of_saved_NEOs_in_Sentry['id'])
# # / test code


# -------------------------------------------------------- #
# ----- NEO DATA FETCH AND PLOT ------- #
# -------------------------------------------------------- #
# -- FULL ASTEROID DATA FETCH -- #
def fetch_asteroid_dictionary(neo_id) -> dict:
    """
    This has been expanded to include the link to the SBDB details.
    If the asteroid IS a Sentry object, it will also fetch the Sentry data by following the breadcrumbs
    to the url that is appended to any Sentry objects in this dataset ('is_sentry_object' has always been
    a field, and if 'true', an additional url is provided to link to THAT asteroid's SENTRY data).

    1. neo_id: str - The NEO ID of the asteroid to fetch.
    2. api_key: str - Your NASA API key.

    Returns:
    dict - A dictionary containing the asteroid's details, including close approach data and Sentry data where available
    {} FIELDS:
        'designation': str
        'name': str
        'id': str
        'neo_reference_id': str
        'nasa_jpl_url': str
        'absolute_magnitude_h': float 
        'estimated_diameter_meters': float
        'close_approach_date': str[]
        'relative_velocity_kph': float (km/h)
        'miss_distance_au': NOT USED - COULD ADD A CONVERSION FACTOR IF WE WANT
        'miss_distance_km': float (proximity to Earth during 'close approach' events)
        'is_sentry_object': bool (does it have Sentry data?)
        'sentry_data_url': str (if it does, where is it?)
        'sentry_dict': dict (here it is)
        'sentry_object_dict': dict (more data that includes ENERGY(Mt))
        'v_inf_kps': float (Velocity_infinity (km/s))
        'energy_Mt': float (impact Kinetic Energy (Megatons))
        'mass_kg': float (mass (kg))
        'ip':  float (impact probability)
        'diameter_m': (SENTRY diameter (m))
    """
    # First, fetch the NEO data
    resp = requests.get(f"https://api.nasa.gov/neo/rest/v1/neo/{neo_id}?api_key={api_key}")
    if resp.status_code != 200:
        raise RuntimeError(f"NEO API request failed: {resp.status_code} - {resp.text}")
    neo_response = resp.json()
    
    # Now, harvest the original NEO fields
    designation = neo_response['designation']
    name = neo_response['name']
    neo_id = neo_response['id']
    neo_ref_id = neo_response['neo_reference_id']
    absolute_magnitude_h = neo_response['absolute_magnitude_h']

    # Compute estimated diameter in meters (average of min and max)
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
    
    # hook into SBDB (ssd.jpl.nasa.gov) to get diameter, albedo, absolute magnitude, etc
    nasa_jpl_url = neo_response['nasa_jpl_url']

    # Hook into SENTRY (if available)
    sentry_data_url = None
    sentry_dict = {}
    is_sentry_object = neo_response['is_sentry_object']
    if is_sentry_object:
        # This field does not exist if 'is_sentry_object' is false
        sentry_data_url = neo_response['sentry_data']
        sentry_json = fetch_sentry_data_from_url(sentry_data_url)   # returns the fetched request.get().json()
        print("...\n")

        # Now, harvest the Sentry fields
        sentry_dict['spkId'] = sentry_json['spkId']
        sentry_dict['fullname'] = sentry_json['fullname']
        sentry_dict['designation'] = sentry_json['designation']
        sentry_dict['sentryId'] = sentry_json['sentryId']
        sentry_dict['v_infinity'] = float(sentry_json['v_infinity'])  # in km/s
        sentry_dict['estimated_diameter'] = float(sentry_json['estimated_diameter'])  # in meters
        sentry_dict['absolute_magnitude'] = float(sentry_json['absolute_magnitude'])
        sentry_dict['palermo_scale_ave'] = float(sentry_json['palermo_scale_ave'])
        sentry_dict['impact_probability'] = float(sentry_json['impact_probability'])
        sentry_dict['is_active_sentry_object'] = sentry_json['is_active_sentry_object']
        sentry_dict['url_impact_details'] = sentry_json['url_impact_details']
    
        # Let's go deeper... a hook within a hook... hookception... 
        # Access the Object Table for ENERGY and MASS directly, instead of computing.
        sentry_object_details_json = fetch_sentry_object_details_from_des(sentry_dict['designation'])
        #        
        print("....")    
        sentry_object_details_dict = {}
        if 'data' in sentry_object_details_json and len(sentry_object_details_json['data']) > 0:        
            sentry_object_details_dict['mass'] = float(sentry_object_details_json['summary']['mass'])  # in kg
            sentry_object_details_dict['v_inf'] = float(sentry_object_details_json['summary'].get('v_inf', None))  # in km/s
            sentry_object_details_dict['ip'] = float(sentry_object_details_json['summary']['ip'])  # impact probability
            sentry_object_details_dict['energy'] = float(sentry_object_details_json['summary'].get('energy', None))  # in Mt
            sentry_object_details_dict['diameter'] = float(sentry_object_details_json['summary']['diameter'])  / 1000 # in m
        
    # compute numeric fallbacks (used when Sentry data not present)
    avg_velocity_kph = compute_average_velocity(velocities_kph) if velocities_kph else None    
    fallback_mass_kg = compute_mass_kg_from_diameter(estimated_diameter_meters)
    fallback_v_inf_kps = (avg_velocity_kph / 3600.0) if avg_velocity_kph is not None else None
    fallback_energy_Mt = (compute_kinetic_energy_Mt_from_massKG_and_velocityKPH(fallback_mass_kg, avg_velocity_kph)
                            if avg_velocity_kph is not None else None)
    fallback_ip = None
    fallback_diameter_m = estimated_diameter_meters


    # Patch to fix the NESTED IF problem of a dict not being created, leading to too many 'None' values instead of the above fallbacks:
    if 'sentry_object_details_dict' not in locals():
        sentry_object_details_dict = {}
    # choose numeric values from Sentry if present, otherwise use computed fallbacks
    v_inf_val = sentry_object_details_dict.get('v_inf') if sentry_object_details_dict.get('v_inf') is not None else fallback_v_inf_kps
    energy_val = sentry_object_details_dict.get('energy') if sentry_object_details_dict.get('energy') is not None else fallback_energy_Mt
    mass_val = sentry_object_details_dict.get('mass') if sentry_object_details_dict.get('mass') is not None else fallback_mass_kg
    ip_val = sentry_object_details_dict.get('ip') if sentry_object_details_dict.get('ip') is not None else fallback_ip
    diameter_val = sentry_object_details_dict.get('diameter') if sentry_object_details_dict.get('diameter') is not None else fallback_diameter_m
        
    return {        
        # WHEN ACCESSING DIAMETER:
        # TRY GETTING 'diameter_m' if 'diameter_m' is not None else {'estimated_diameter_meters'}
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
        'sentry_object_dict': sentry_object_details_dict if is_sentry_object else {},
        #
        #
        'v_inf_kps': v_inf_val,
        'energy_Mt': energy_val,
        'mass_kg': mass_val,
        'ip':  ip_val,
        'diameter_m': diameter_val
    }

# -- plot the RETURNED DICTIONARY from 'fetch_asteroid_dictionary(neo_id, api_key)' -- #
def plot_asteroid_dictionary(asteroid_dict):
    dates_to_plot = convert_approach_dates_to_DateTypeList(asteroid_dict['close_approach_date'])
    plt.figure(figsize=(10, 5))
    plt.plot(dates_to_plot, asteroid_dict['miss_distance_km'], marker='o')
    plt.xlabel('Close Approach Date')
    plt.ylabel('Miss Distance (tens of millions of kilometers from Earth)')
    plt.title(f'Asteroid {asteroid_dict["name"]} Proximity to Earth Distance Over Time')
    plt.xticks(rotation=45)
    # Format the x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Change format to just Year
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())  # Automatically determine good intervals
    plt.gcf().autofmt_xdate()  # Automatically format the x-axis labels
    plt.axvline(datetime.now(), color='red', linestyle='--', label='Today')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

# -------------------------------------------------------- #
# ----- toString() ------- #
def print_all_data_for_asteroid_dict(asteroid_dict):
    """
    INPUT:
        asteroid_dict: dict.json() 

    An organized, neater way to see the data pulled from the API for a particular asteroid
    """
    for key, value in asteroid_dict.items():
        print(f"\n{key}: {value}")


# -------------------------------------------------------- #
# ----- SENTRY DATA WHERE AVAILABLE ------- #
# -------------------------------------------------------- #
def fetch_sentry_data_from_url(sentry_url):
    """
    One field in the original NEO data is 'is_sentry_object'. If true, an additional field is present called 'sentry_data_url', linking
    to the Sentry API. This function fetches the Sentry data from that URL.
    1. sentry_url: str - The URL to fetch Sentry data from.

    Returns:
    dict - The JSON response from the Sentry API as a dictionary.
    """
    resp = requests.get(sentry_url)
    if resp.status_code != 200:
        raise RuntimeError(f"Sentry API request failed: {resp.status_code} - {resp.text}")
    sentry_response = resp.json()
    return sentry_response

def fetch_sentry_object_details_from_des(sentry_designation):
    """
    The above Sentry API hook does not actually include the 'ENERGY' field... 
    BUT
    That is accessible through another URL in this function.
    1. sentry_designation: str - 'designation' value, which would be found in the above function.

    Returns:
    dict - The JSON response from the Sentry API for the specific designation as a dictionary.
    """
    # example: "https://ssd-api.jpl.nasa.gov/sentry.api?des=1997 TC25"
    url = "https://ssd-api.jpl.nasa.gov/sentry.api?des=" + sentry_designation
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f"Sentry API request failed: {resp.status_code} - {resp.text}")
    sentry_object_details_json = resp.json()    
    return sentry_object_details_json


# -------------------------------------------------------- #
# ----- MATH FOR WHEN SENTRY != AVAILABLE ------- #
# -------------------------------------------------------- #

def compute_average_velocity(velocities_list):
    return ( sum(velocities_list) / len(velocities_list) )

def compute_mass_kg_from_diameter(estimated_diameter_meters, density_g_cm3=2.6):
    # Convert diameter from meters to centimeters
    diameter_cm = estimated_diameter_meters * 100
    radius_cm = diameter_cm / 2
    volume_cm3 = (4/3) * np.pi * (radius_cm ** 3)
    density_kg_m3 = density_g_cm3 * 1000  # Convert g/cm^3 to kg/m^3
    mass_kg = density_kg_m3 * (volume_cm3 / 1e6)  # Convert cm^3 to m^3 for mass calculation
    return mass_kg

def compute_kinetic_energy_Mt_from_massKG_and_velocityKPH(mass_kg, velocity_kph, *, return_unit='Mt'):
    """
    Compute kinetic energy from mass (kg) and velocity (km/h).

    This is an embarresingly low-level computation that does not factor in the effect of the atmosphere,
    additional gravitational pulls, angle of approach, etc, because it is a simple overnight thought.

    return_unit options: 'Mt' (megatons), 'tons' (metric tons), or 'J' (joules).
    """
    try:
        m = float(mass_kg)
        v_kph = float(velocity_kph)
    except (TypeError, ValueError):
        return None
    
    # protect against negative values (use absolute velocity, mass should be non-negative)
    if m < 0:
        return None
    v_m_s = abs(v_kph) / 3.6  # km/h -> m/s

    ke_joules = 0.5 * m * (v_m_s ** 2)

    if return_unit == 'Mt':
        return ke_joules / 4.184e15
    if return_unit == 'tons':
        return ke_joules / 4.184e9
    return ke_joules



# -------------------------------------------------------- #
# ----- PRIORITY FUNCTION ------- #
# -------------------------------------------------------- #
def get_damageString_from_neoID(neo_id) -> str:
    """
    INPUT: 'neo id' value for a given NEO. This could be obtained from 
            by calling on any NEO in:
            requests.(neo_url).json()['near_earth_objects']['id']

    RETURNS:
    str: Text based damage display in the event of impact.
    """
    asteroid = fetch_asteroid_dictionary(neo_id)
    name = asteroid.get('name')
    diameter_m = asteroid.get('estimated_diameter_meters')
    mass_kg = asteroid.get('mass_kg')
    velocity_infinity_kps = asteroid.get('v_inf_kps')
    kinetic_Energy_Mt = asteroid.get('energy_Mt')
    isPredicted = False
    if asteroid.get('ip') is not None:
        isPredicted = True
    impact_probability = asteroid.get('ip') if isPredicted else {None}

    # Build a string to explain the damage
    output = "BOOM!\n..."
    output += f"Asteroid {name}, just struck EARTH!"
    if isPredicted:
        output += f"This was a \'{impact_probability}\' probability of impact, and it did so at "
    else:
        output += "This was an UNPREDICTED strike, and it hit at "
    output += f"{velocity_infinity_kps} kilometers per SECOND! That's {velocity_infinity_kps * 3600}km/h!\n"
    output += f"Considering the size of {name} is {diameter_m} meters in diameter, with approximate mass of {mass_kg}kg,\n"
    output += f"that means it struck earth with an impact of {kinetic_Energy_Mt}Mt, which is equal to {(kinetic_Energy_Mt * 1000000):,.0f} million tons of TNT!"
    output += "\nTHAT'S A LOT OF DAMAGE!"

    return output

def get_damageData_from_neoID(neo_id) -> dict:
    """
    INPUT: 'neo id' value for a given NEO. This could be obtained from 
            by calling on any NEO in:
            requests.(neo_url).json()['near_earth_objects']['id']

    RETURNS:
        dict: 
            'name': name,
            'diameter': diameter_m,
            'mass': mass_kg,
            'velocity': velocity_infinity_kps,
            'energy': kinetic_Energy_Mt,
            'isPredicted': isPredicted,
            'ip': impact_probability
    """
    asteroid = fetch_asteroid_dictionary(neo_id)
    name = asteroid.get('name')
    diameter_m = asteroid.get('estimated_diameter_meters')
    mass_kg = asteroid.get('mass_kg')
    velocity_infinity_kps = asteroid.get('v_inf_kps')
    kinetic_Energy_Mt = asteroid.get('energy_Mt')
    isPredicted = False
    if asteroid.get('ip') is not None:
        isPredicted = True
    impact_probability = asteroid.get('ip') if isPredicted else {None}

    final_data = {
        'name': name,
        'diameter': diameter_m,
        'mass': mass_kg,
        'velocity': velocity_infinity_kps,
        'energy': kinetic_Energy_Mt,
        'isPredicted': isPredicted,
        'ip': impact_probability
    }

    return final_data

def get_impactEnergy_Mt_from_neoID(neo_id) -> float:
    """
    INPUT: 'neo id' value for a given NEO. This could be obtained from 
            by calling on any NEO in:
            requests.(neo_url).json()['near_earth_objects']['id']

    RETURNS:
        float: Kinetic Energy on Impact (Megatons) 
    """
    asteroid = fetch_asteroid_dictionary(neo_id)
    kinetic_Energy_Mt = asteroid.get('energy_Mt')
    
    return kinetic_Energy_Mt



## --- Get next close-approach-date -- ##
# def convert_approach_dates_to_DateTypeList(dates_list):
#     """
#     Input:
#         str[] -> The ['close_approach_date'] list from 
#                     (fetch_asteroid_dictionary(neo_id))['close_approach_date']
#     Return:
#         datetime[] -> The same list, but as DATETIME objects instead of str
#     """
#     # Today
#     current_date = datetime.now()

#     # Convert the dates str[] to DATE[]
#     dates_AS_dates = []
#     for date in dates_list:
#         date_AS_date = datetime.strptime(date, '%Y-%m-%d')
#         dates_AS_dates.append(date_AS_date)

#     return dates_AS_dates

def get_next_approach_date(dates_list):
    """
    Get the next upcoming 'close approach' according to the NASA API NEO dataset.
    Return the most recent approach if no predicted future approach.

    Input:
        str[] -> The ['close_approach_date'] list from 
                    (fetch_asteroid_dictionary(neo_id))['close_approach_date']
    
    Return:
        datetime -> The next (or most recent) 'close-approach'
    """
    # Today
    current_date = datetime.now()

    # Convert the dates str[] to DATE[]
    previous_dates = []
    next_approach_date = None
    for date in dates_list:
        date_AS_date = datetime.strptime(date, '%Y-%m-%d')
        if (date_AS_date < current_date):
            previous_dates.append(date_AS_date)
        else:
            next_approach_date = date_AS_date
    
    if next_approach_date is not None:
        return next_approach_date
    else:
        # Return the most recent approach if no predicted future approach
        return previous_dates[-1]


def get_next_approach_date_by_neoID(neo_id):
    """
    Return next or most recent 'close approach' as a date string (YYYY-MM-DD), or None.
    """
    current_date_str = datetime.now().strftime('%Y-%m-%d')

    neo_dict = fetch_asteroid_dictionary(neo_id)
    dates_list = neo_dict.get('close_approach_date', [])

    if not dates_list:
        return None

    dates_list.sort()  # sorts strings lex order as dates if in ISO format

    future_dates = [d for d in dates_list if d >= current_date_str]
    if future_dates:
        return future_dates[0]

    past_dates = [d for d in dates_list if d < current_date_str]
    if past_dates:
        return past_dates[-1]

    return None


def get_X_soonest_approaching_neo_IDs_from_global_list(limit=10):
    """
    Returns list of top X soonest approaching NEO IDs by sorting date strings.
    """
    top_X = []
    for i in global_list_of_saved_NEO_IDs[:limit]:
        approach_date_i = get_next_approach_date_by_neoID(i)
        top_X.append({'neo_id': i, 'next_approach': approach_date_i})

    # Sort by date string; treat None as very large to push to end
    top_X.sort(key=lambda x: x['next_approach'] if x['next_approach'] is not None else '9999-12-31')

    for entry in top_X:
        print(entry['neo_id'])
        print(entry['next_approach'])

    top_X_neo_IDs = [entry['neo_id'] for entry in top_X]
    return top_X_neo_IDs

# def get_next_approach_date_by_neoID(neo_id):
#     """
#     Get the next upcoming 'close approach' according to the NASA API NEO dataset.
#     Return the most recent approach if no predicted future approach.

#     Input:
#         str -> neo_id
    
#     Return:
#         datetime -> The next (or most recent) 'close-approach'
#     """
#     # Today
#     current_date = datetime.now()

#     neo_dict = fetch_asteroid_dictionary(neo_id)
#     dates_list = neo_dict.get('close_approach_date', [])

#     if not dates_list:
#         return None  # No dates available

#     # Convert string dates to datetime objects
#     dates_as_datetime = [datetime.strptime(date, '%Y-%m-%d') for date in dates_list]

#     # Sort dates in ascending order
#     dates_as_datetime.sort()

#     # Find earliest future date
#     future_dates = [d for d in dates_as_datetime if d >= current_date]
#     if future_dates:
#         return future_dates[0]

#     # If no future dates, return the most recent past date
#     past_dates = [d for d in dates_as_datetime if d < current_date]
#     if past_dates:
#         return past_dates[-1]

#     # Fallback
#     return None

# # TEST ASTEROID: 3092161
# # neo3092161 = fetch_asteroid_dictionary("3092161")
# # print_all_data_for_asteroid_dict(neo3092161)
# # plot_asteroid_dictionary(neo3092161)
# # print(neo3092161.get('is_sentry_object'))
# # get_damageString_from_neoID("3092161")



# # Test sorting
# # multipage_fetch_NEO_IDs(10)
# # print(global_list_of_saved_NEO_IDs)
# # for entry in global_list_of_saved_NEO_IDs:
# #     print(get_next_approach_date_by_neoID(entry))
# # results = []
# # for neo_id in global_list_of_saved_NEO_IDs:
# #     date = get_next_approach_date(neo_id)
# #     results.append({'id': neo_id, 'date': date})
# # results.sort(key=lambda x: x['date'])

# # top_10_ids = [entry['id'] for entry in results[:10]]
# # print(top_10_ids)
# # for j in top_10_ids:
# #     print(get_next_approach_date_by_neoID(j))


# # list_ = multipage_fetch_NEO_IDs()
# def get_X_soonest_approaching_neo_IDs_from_global_list(limit=10):
#     """
#     INPUT = 'X' == HOW MANY?

#     RETURNS LIST OF TOP 10 (soonest approaching) NEO IDs
#     """
#     top_X = []
#     for i in global_list_of_saved_NEO_IDs[:10]:
#         approach_date_i = get_next_approach_date_by_neoID(i)
#         # print(approach_date_i)
#         top_X.append({'neo_id': i, 'next_approach': approach_date_i})
#     top_X.sort(key=lambda x: (x['next_approach'] is None, x['next_approach']))
    
#     for entry in top_X:
#         print(entry['neo_id'])
#         print(entry['next_approach'])

#     top_X_neo_IDs = [entry['neo_id'] for entry in top_X]

#     return top_X_neo_IDs

def send_db_to_html(list_of_ids):
    data_dict = {}
    
    for neo_id in list_of_ids:
        data_dict[neo_id] = fetch_asteroid_dictionary(neo_id)


    return data_dict


"""
asteroid_db = {


}
"""

# top_10_soonest_IDs = get_X_soonest_approaching_neo_IDs_from_global_list(10)
# def populate_ASTEROID_db_by_neo_IDs(neo_ids_list):
    
#     asteroid_DB = {}

#     for each in neo_ids_list:
#         asteroid_DB



# asteroid_DB = populate_ASTEROID_db_by_neo_IDs()


# if __name__ == "__main__":

#     multipage_fetch_NEO_IDs(3)
#     data_dict = send_db_to_html(global_list_of_saved_NEO_IDs)
#     import json

#     try:
#         json.dumps(data_dict)  # Test if serializable
#         print("success")
#     except TypeError as e:
#         print("Serialization error:", e)
    
#     print(data_dict)

#     # print(get_damageString_from_neoID("3092161"))
#     # print(get_damageString_from_neoID("2001566"))

#     # plot_asteroid_dictionary(fetch_asteroid_dictionary("3092161"))
#     # plot_asteroid_dictionary(fetch_asteroid_dictionary("2001566"))

#     neo_2001566 = fetch_asteroid_dictionary("2001566")
#     neo_3092161 = fetch_asteroid_dictionary("3092161")


#     # test
#     plot_asteroid_dictionary(neo_2001566)
#     plot_asteroid_dictionary(neo_3092161)
    # Test sorting



    # multipage_fetch_NEO_IDs(10)
    # print(send_db_to_html(global_list_of_saved_NEO_IDs))
    # print(len(global_list_of_saved_NEO_IDs))
    # print(global_list_of_saved_NEO_IDs)
    

    

 

    # # def get_X_soonest_approaching_neo_IDs_from_global_list(limit=10):
    # #     """
    # #     INPUT = 'X' == HOW MANY?

    # #     RETURNS LIST OF TOP 10 (soonest approaching) NEO IDs
    # #     """
    # #     top_X = []
    # #     for i in global_list_of_saved_NEO_IDs[:10]:
    # #         approach_date_i = get_next_approach_date_by_neoID(i)
    # #         # print(approach_date_i)
    # #         top_X.append({'neo_id': i, 'next_approach': approach_date_i})
    # #     top_X.sort(key=lambda x: x['next_approach'])
    # #     for entry in top_X:
    # #         print(entry['neo_id'])
    # #         print(entry['next_approach'])

    # #     top_X_neo_IDs = [entry['neo_id'] for entry in top_X]

    # #     return top_X_neo_IDs


    # multipage_fetch_NEO_IDs(10)
    # print(global_list_of_saved_NEO_IDs)
    # ten_soonest_IDs = get_X_soonest_approaching_neo_IDs_from_global_list(100)
    # print(ten_soonest_IDs)


    

    