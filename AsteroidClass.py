import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import time
import requests
import pandas as pd
import os, io
import sys

class Asteroid:
    def __init__(self, neo_id: str, api_key: str):
        self.neo_id = neo_id
        self.api_key = api_key

        # init fields as None (or empty) to start
        self.designation = None
        self.name = None
        self.neo_ref_id = None
        self.absolute_magnitude_h = None
        self.estimated_diameter_meters = None
        self.close_approach_dates = []
        self.velocities_rel_kph = []
        self.miss_dist_km = []
        self.nasa_jpl_url = None
        self.is_sentry_object = False
        self.sentry_data_url = None
        self.sentry_dict = {}
        self.sentry_object_dict = {}
        # Sentry fields, where available:
        self.sentry_spkId = None
        self.sentry_fullname = None
        self.sentry_designation = None
        self.sentry_sentryId = None
        self.sentry_v_infinity = None
        self.sentry_estimated_diameter = None
        self.sentry_absolute_magnitude = None
        self.sentry_palermo_scale_ave = None
        self.sentry_impact_probability = None
        self.is_active_sentry_object = None
        self.url_impact_details = None
        self.sentry_details_mass_kg = None
        self.sentry_details_v_inf_kms = None
        self.sentry_details_ip = None
        # THE BIG ONE!!
        self.sentry_details_enery_Mt = None
        self.sentry_details_diameter_km = None

        # When first instantiated, fetch data to populate the available fields
        self._fetch_data()
    
    def _fetch_data(self):
        url = f"https://api.nasa.gov/neo/rest/v1/neo/{self.neo_id}?api_key={self.api_key}"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"NEO API request failed: {resp.status_code} - {resp.text}")
        neo_response = resp.json()

        # Now, harvest the original NEO fields
        self.designation = neo_response['designation']
        self.name = neo_response['name']
        self.neo_id = neo_response['id']
        self.neo_ref_id = neo_response['neo_reference_id']
        self.absolute_magnitude_h = neo_response['absolute_magnitude_h']

        # Compute estimated diameter in meters (average of min and max)
        estimated_diameter_min_meters = neo_response['estimated_diameter']['meters']['estimated_diameter_min']  # in meters
        estimated_diameter_max_meters = neo_response['estimated_diameter']['meters']['estimated_diameter_max']  # in meters
        if estimated_diameter_max_meters and estimated_diameter_max_meters:
            self.estimated_diameter_meters = (estimated_diameter_min_meters + estimated_diameter_max_meters) / 2  # average diameter in meters
        
        # hook into SBDB (ssd.jpl.nasa.gov) to get diameter, albedo, absolute magnitude, etc
        self.nasa_jpl_url = neo_response['nasa_jpl_url']

        if 'close_approach_data' in neo_response:   # it SHOULD be...
            for event in neo_response['close_approach_data']:
                self.close_approach_dates.append(event['close_approach_date'])
                self.velocities_rel_kph.append(float(event['relative_velocity']['kilometers_per_hour']))
                self.miss_dist_km.append(float(event['miss_distance']['kilometers']))

        # Sentry??
        self.is_sentry_object = neo_response['is_sentry_object']
        if self.is_sentry_object:
            self.sentry_data_url = neo_response['sentry_data']
            if self.sentry_data_url:
                sentry_json = self._fetch_sentry_data(self.sentry_data_url)
                # Now, harvest the SENTRY fields
                self.sentry_spkId = sentry_json['spkId']
                self.sentry_fullname = sentry_json['fullname']
                self.sentry_designation = sentry_json['designation']
                self.sentry_sentryId = sentry_json['sentryId']
                self.sentry_v_infinity = sentry_json['v_infinity']  # in km/s
                self.sentry_estimated_diameter = sentry_json['estimated_diameter']  # in meters
                self.sentry_absolute_magnitude = sentry_json['absolute_magnitude']
                self.sentry_palermo_scale_ave = sentry_json['palermo_scale_ave']
                self.sentry_impact_probability = sentry_json['impact_probability']
                self.is_active_sentry_object = sentry_json['is_active_sentry_object']
                self.url_impact_details = sentry_json['url_impact_details']

                # Let's go deeper... a hook within a hook... hookception... 
                # Access the Object Table for ENERGY and MASS directly, instead of computing.
                sentry_object_details_json = self._fetch_sentry_object_details(self.sentry_designation)
                # Now, harvest the SENTRY OBJECT DETAILS fields
                if 'data' in sentry_object_details_json and len(sentry_object_details_json['data']) > 0:
                    self.sentry_details_mass_kg = sentry_object_details_json['summary']['mass']  # in kg
                    self.sentry_details_v_inf_kms = sentry_object_details_json['summary']['v_inf']  # in km/s
                    self.sentry_details_ip = sentry_object_details_json['summary']['ip']  # impact probability
                    # THE BIG ONE!!
                    self.sentry_details_enery_Mt = sentry_object_details_json['summary']['energy']  # in Mt
                    self.sentry_details_diameter_km = sentry_object_details_json['summary']['diameter']  # in km

        

    def _fetch_sentry_data(self, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"NEO API request failed: {resp.status_code} - {resp.text}")
        return resp.json()
        

    def _fetch_sentry_object_details(self, sentry_designation):
        url = "https://ssd-api.jpl.nasa.gov/sentry.api?des=" + sentry_designation
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Sentry API request failed: {resp.status_code} - {resp.text}")
        return resp.json()  

    def __str__(self):
        lines = [
            f"Asteroid {self.name} (Designation: {self.designation})",
            f"NEO Reference ID: {self.neo_ref_id}",
            f"Absolute Magnitude (H): {self.absolute_magnitude_h}",
            f"Estimated Diameter (m): {self.estimated_diameter_meters}",
            f"Close Approaches: {len(self.close_approach_dates)}",
            f"Miss Distances (km): {self.miss_dist_km}"
            f"Relative Velocities (km/h): {self.velocities_rel_kph}"
            f"NASA JPL URL: {self.nasa_jpl_url}",
            f"Is Sentry Object: {self.is_sentry_object}",
        ]
        if self.is_sentry_object:
            sentry_lines = [
                f"Sentry Data URL: {self.sentry_data_url}",
                f"Sentry spkId: {self.sentry_spkId}",
                f"Sentry fullname: {self.sentry_fullname}",
                f"Sentry designation: {self.sentry_designation}",
                f"SentryId: {self.sentry_sentryId}",
                f"Sentry Vinf: {self.sentry_v_infinity}",
                f"Sentry estimated Diameter: {self.sentry_estimated_diameter}",
                f"Sentry Absolute Magnitude: {self.sentry_absolute_magnitude}",
                f"Sentry Palermo Scale: {self.sentry_palermo_scale_ave}",
                
                f"Sentry Ip: {self.sentry_impact_probability}"
            ]
            lines.extend(sentry_lines)
            if self.sentry_details_mass_kg is not None:
                sentry_details_lines = [
                    f"Sentry details - Mass (kg): {self.sentry_details_mass_kg}",
                    f"Sentry details - Vinf (km/s): {self.sentry_details_v_inf_kms}",
                    f"Sentry details - Impact Prob: {self.sentry_details_ip}",
                    f"Sentry deails - Kinetic Energy (Mt): {self.sentry_details_enery_Mt}",
                    f"Sentry details - Diameter (km): {self.sentry_details_diameter_km}"
                ]
            lines.extend(sentry_details_lines)
        return "\n".join(lines)
    

api_key = "EP74NmRl7BcxtiRjO4YZrAlJwIjOgeuWNP4Pwg4w"

print(Asteroid("3092161", api_key))





"""
THE BELOW IS SCRAP CODE
"""

# -------------------------------------------------------- #
# ----- SENTRY DATA FETCH WHOLE DB ------- #
# -------------------------------------------------------- #
# sentry_url = "https://ssd-api.jpl.nasa.gov/sentry.api"
# sentry_response = requests.get(sentry_url)
# sentry_data = sentry_response.json()

# all_sentry_asteroids = []
# def search_paged_sentry_dataset(page=0):
#     sentry_url = "https://ssd-api.jpl.nasa.gov/sentry.api"
#     sentry_response = requests.get(sentry_url)
#     sentry_data = sentry_response.json()
#     for entry in sentry_data:
#         all_sentry_asteroids.append(entry)
#     if 'next' in sentry_data and sentry_data['next']:
#         time.sleep(.1)  # Avoid hitting the server too quickly
#         search_paged_sentry_dataset(page + 1)
# sentry_asteroids_in_neo = []
# neo_ids_in_sentry = []
# actually_all_neo_asteroids = []
# page = 0

    

# # Print the keys of the sentry_data to see its structure
# print("Sentry Data Keys:", sentry_data.keys())
# # print the keys withinb the 'data' key
# print("Sentry Data 'data' Keys:", sentry_data.get('data', [])[:1])  # Print first entry to see structure
# """
# Sentry Data 'data' Keys: [{'id': 'bJ79X00B', 'n_imp': 4, 'h': '18.54', 'ps_cum': '-2.70', 'diameter': '0.66', 'fullname': '(1979 XB)', 'des': '1979 XB', 'v_inf': '23.7606234552547', 'range': '2056-2113', 'last_obs_jd': '2444222.5', 'ps_max': '-3.00', 'ts_max': '0', 'ip': '8.515158e-07', 'last_obs': '1979-12-15'}]
# """

# # Find that specific asteriod in the neo data
# specific_asteroid_id = "bJ79X00B"  # Example ID for (1979 XB)
# specific_asteroid_fullname = "(1979 XB)"
# specific_asteroid_des = "1979 XB"

# # search for that specific asteroid in the neo data
# neo_data = requests.get(neo_url).json()

# #find that specific asteroid in the neo data
# neo_data_neos = neo_data['near_earth_objects']
# for neo in neo_data_neos:
#     if neo['id'] == specific_asteroid_id or neo['name'] == specific_asteroid_fullname or neo['designation'] == specific_asteroid_des:
#         specific_asteroid_neo = neo
#         break

# print("Specific Asteroid NEO Data:", specific_asteroid_neo, "\n", "neo_id: ", specific_asteroid_neo['id'])
