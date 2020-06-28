import requests
import pandas as pd

URL = 'https://data.cityofnewyork.us/resource/h9gi-nx95.json'
PATH = '~/Web-Applications/Motor-Vehicle-Collisions-NYC/data/MVC-NYC.csv'

r = requests.get(URL)
# print(r.status_code)

json = r.json()
pd.DataFrame(json).to_csv(PATH)