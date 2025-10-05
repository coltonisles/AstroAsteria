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


app = Flask(__name__)

@app.route('/')
def home():
    
    HookedOnSentry.multipage_fetch_NEO_IDs(10)
    
    closests = HookedOnSentry.get_X_soonest_approaching_neo_IDs_from_global_list(10)
    lsit_of_astroid = []

    for i in closests:
        lsit_of_astroid.append(HookedOnSentry.fetch_asteroid_dictionary(i)['name'])

    return render_template('index.html', items=lsit_of_astroid)





    
    

#grabs a top ten list of the closets astroids to earth



 




#A function that returns the asteriods distance in km's from earth

if __name__ == "__main__":
    app.run(debug=True)
    




    

            


        
