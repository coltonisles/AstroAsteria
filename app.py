import HookedOnSentry
from flask import Flask, render_template_string, render_template
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

api_key = str(os.getenv('API_KEY'))
url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={api_key}"
response = requests.get(url)
data = response.json()

app = Flask(__name__)

@app.route('/')
def home():
    
    closests = HookedOnSentry.get_X_soonest_approaching_neo_IDs_from_global_list(10)

    return render_template('index.html', items=closests)





    
    

#grabs a top ten list of the closets astroids to earth



 




#A function that returns the asteriods distance in km's from earth

if __name__ == "__main__":
    app.run(debug=True)
    




    

            


        
