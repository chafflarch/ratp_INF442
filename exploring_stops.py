import numpy as np
import requests
import pandas as pd
import json 
from datetime import datetime, timedelta
import pytz




#################################################################################
# GOAL 1 : get the current time arrival and departure at Lozère for the RERB with direction and VehicleJourneyName and know if it is at the stop
# Sur Unitary-Real-Time, la limite est à 1 000 000  request par jour, donc on est large, mais dans Global-Real-Time,
#si l'on vient à l'utiliser, on descent à 1 000  request par jour
#################################################################################

arret = "Lozère"
#correspondance avec arrêt Id
csv_file = '/Users/charlesbenichouchaffanjon/Documents/Poly/Code/projet_INF442/csv_stops'
df = pd.read_csv(csv_file, sep=';')  # préciser le séparateur est essentiel sinon il fait des erreurs sur certaines lignes

#To get the refs
#print(df.loc[(df['ArRName'] == arret) & (df['ArRType'] == "rail") ])
# on se retrouve avec trois ID différents pour Lozère rail ... Possiblement dans un sens, dans l'autre et les deux à la gare
# 474063 vers Saint-Rémy
# 473931 vers CdG
# 474069 est un arrêt fictif qui chapeaute les deux 


'''
pour automatiser encore plus, ce serait bien de passer de l'ArRName à l'ArRID en sachant déterminer quel est le bon sens sans tester la direction : 
S'il y a une base de donnée qui référence cela, je ne l'ai pas trouvée : le sens des lignes existe-t-il dans PRIM ? 
Pour l'instant, le plus simple est de garder les infos dans les deux sens, puis les trier
'''



# (TO BE HIDDEN)
api_token = '2Btko3bnqjqsyYIE6g8rJX7YwxjJ8pua'

api_url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF%3AStopPoint%3AQ%3A473931%3A'
# Get the Paris timezone ; Attention la base de donnée est en GMT
paris_timezone = pytz.timezone('Europe/Paris')
paris_time = datetime.now(paris_timezone)
request_time = paris_time.strftime('%Y-%m-%dT%H:%M:%S')
head = {'apiKey' : api_token , 'Date': request_time}
response = requests.get(api_url, headers=head)
 
# Parse JSON
data = json.loads(response.content)
# Extract the values from response
expected_arrival_times = [visit["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"] 
                          for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]

directions_packed = [visit["MonitoredVehicleJourney"]["DirectionName"] 
                     for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]

directions =[train_direction[0]["value"] for train_direction in directions_packed]

VJNs = [visit["MonitoredVehicleJourney"]["VehicleJourneyName"][0]["value"] 
                        for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]

vehicle_at_stop =  [visit["MonitoredVehicleJourney"]["MonitoredCall"]["VehicleAtStop"] for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]

# Print the extracted values
# On veut l'horaire auquel on a l'affichage 
print("horaire du RER_B à l'arrêt Lozère (dans les deux sens) : demandé à  " + request_time)

for i, str_time in enumerate(expected_arrival_times):
    #On remet dans le bon fuseau horaire : il faut le faire finement avec les décalages horaires
    # datatime.strptime prend le format de la date
    # EAT for expected_arrival_times
    GMT_EAT = datetime.strptime(str_time,'%Y-%m-%dT%H:%M:%S.%fZ')
    # ajustement à l'heure de UTC à Paris
    GMT_EAT = GMT_EAT.replace(tzinfo=pytz.utc)
    Paris_EAT = GMT_EAT.astimezone(paris_timezone)
    print("Paris_EAT = " + str(Paris_EAT)
          + 'direction = ' + directions[i]
          + '; VJN = ' + VJNs[i] 
          + '; vehicle is at stop = ' + str(vehicle_at_stop[i]))  # On assume qu'il n'y a qu'une direction par train !







