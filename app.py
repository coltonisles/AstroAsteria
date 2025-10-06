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
import json
import base64

load_dotenv()


app = Flask(__name__)

@app.route('/')
def home():
    
    HookedOnSentry.multipage_fetch_NEO_IDs(10)
    
    closests = HookedOnSentry.get_X_soonest_approaching_neo_IDs_from_global_list(10)
    list_of_astroid = []

    for i in closests:
        list_of_astroid.append(HookedOnSentry.fetch_asteroid_dictionary(i)['name'])
        
    json_file = HookedOnSentry.send_db_to_html(closests)

    #json.dumps(json_file)

   



    return render_template('index.html', items=list_of_astroid, item2=json_file)



if __name__ == "__main__":
    app.run(debug=False)
    




    

            


        
