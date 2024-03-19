import requests
import pandas as pd
import json 
import time
import pytz
from datetime import datetime, timedelta
# On a à disposion l'ensemble du planning très à l'avance (30j) actualisé trois fois par jour 
#: https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/information/
# Mais ce n'est pas vraiment avec cela que l'on va avoir la réalité des délais engendrés pour un passager... 


#obj : récupérer tous les horaires d'arrivée réels du RER B à Lozère pendant une période de temps : 



# la base de la requête : 
arret = "Lozère"
csv_file = '/Users/charlesbenichouchaffanjon/Documents/Poly/Code/projet_INF442/csv_stops'
df = pd.read_csv(csv_file, sep=';')
print(df.loc[(df['ArRName'] == arret) & (df['ArRType'] == "rail") ])
api_token = '2Btko3bnqjqsyYIE6g8rJX7YwxjJ8pua'
api_url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF%3AStopPoint%3AQ%3A474069%3A'
paris_timezone = pytz.timezone('Europe/Paris')
paris_time = datetime.now(paris_timezone)
request_time = paris_time.strftime('%Y-%m-%dT%H:%M:%S')
head = {'apiKey' : api_token , 'Date': request_time}



def real_arrival_times(delta_t):  # delta_t : temps en seconde pendant lequel on regarde tous les horaires d'arrivée exacts ; 
    t =0
    while(t<= delta_t):
        response = requests.get(api_url, headers=head)
        data = json.loads(response.content)
        first_vehicle_at_stop =  [visit["MonitoredVehicleJourney"]["MonitoredCall"]["VehicleAtStop"] for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]][0]
        if(first_vehicle_at_stop):
                # On stocke la ref du train et l'horaire de la première requête qui renvoie un first_vehicle_at_stop True : 
                # On prend l'horaire d'arrivée réel - l'horaire d'arrivée prévu comme le retard dans cette convention ; 
            

        time.sleep(10) 
        t+=10


real_arrival_times(30)