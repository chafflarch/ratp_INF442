import numpy as np
import requests
import pandas as pd
import json 
from datetime import datetime, timedelta
import pytz

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
api_url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF%3AStopPoint%3AQ%3A473931%3A'

# Get the Paris timezone ; c'est un peu inutile mais on est sûr d'être à Paris
paris_timezone = pytz.timezone('Europe/Paris')
paris_time = datetime.now(paris_timezone)
request_time = paris_time.strftime('%Y-%m-%dT%H:%M:%S')
head = {'apiKey' : api_token , 'Date': request_time}
response = requests.get(api_url, headers=head)


# On veut : l'horaire auquel on a l'affichage  et les horaires prévus des prochains trains avec la direction

# Parse JSON
data = json.loads(response.content)
# Extract ExpectedArrivalTime values
expected_arrival_times = [visit["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"] for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]

# Print the extracted values
print("horaire du RER_B à l'arrêt Lozère vers Paris demandé à :  " + request_time)

for str_time in expected_arrival_times:
    #On remet dans le bon fuseau horaire : il faut le faire finement avec les décalages horaires
    # datatime.strptime prend le format de la date
    GMT_time = datetime.strptime(str_time,'%Y-%m-%dT%H:%M:%S.%fZ')
    # ajustement à l'heure de Paris
    paris_timezone = pytz.timezone('Europe/Paris')
    # il faut bien lui dire que l'horaire récupéré est en UTC
    GMT_time = GMT_time.replace(tzinfo=pytz.utc)
    Paris_time = GMT_time.astimezone(paris_timezone)
    print(Paris_time)


# pour automatiser encore plus, ce serait bien de passer de l'ArRName à l'ArRID en sachant déterminer quel est le bon sens
# Attention c'est l'horaire GMT qui est renvoyé, il faut magouiller pour avoir le temps de paris en sortie



