import numpy as np
import requests
import pandas as pd
import json 
# first goal : get the current time arrival and departure at Lozère for the RERB

arret = "Lozère"
#correspondance avec arrêt Id
csv_file = '/Users/charlesbenichouchaffanjon/Documents/Poly/Code/projet_INF442/csv_stops'
# préciser le séparateur est essentiel sinon il fait des erreurs sur certaines lignes
df = pd.read_csv(csv_file, sep=';')

print(df.loc[(df['ArRName'] == arret) & (df['ArRType'] == "rail") ])
# on se retrouve avec trois ID différents pour Lozère rail ... Possiblement dans un sens, dans l'autre et les deux à la gare
# deux sont en ArRFareZone = 4

# appel à la base de donnée ; 
# 474063 a l'air d'être vers Saint-Rémy
# 473931 vers CdG

# token for this dataset 2Btko3bnqjqsyYIE6g8rJX7YwxjJ8pua (ne vaut que pour les API)

api_token = '2Btko3bnqjqsyYIE6g8rJX7YwxjJ8pua'
api_url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF%3AStopPoint%3AQ%3A474063%3A'
head = {'apiKey' : api_token}
response = requests.get(api_url, headers=head)


# On veut : l'horaire auquel on a l'affichage  et les horaires prévus des prochains trains avec la direction

request_time = ''



# Parse JSON
data = json.loads(response.content)
# Extract ExpectedArrivalTime values
expected_arrival_times = [visit["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"] for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]

# Print the extracted values
for time in expected_arrival_times:
    print(time)





