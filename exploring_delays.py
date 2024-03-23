import requests
import pandas as pd
import json 
import time
import pytz
from datetime import datetime, timedelta


# On a à disposion l'ensemble du planning très à l'avance (30j) actualisé trois fois par jour 
#: https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/information/
# Mais ce n'est pas vraiment avec cela que l'on va avoir la réalité des délais engendrés pour un passager... 
 # ça évite de croiser avec le planning prévu plusieurs jours à l'avance et qui ne correspond à rien pour les voyageurs du RER B

''' 
    1ère approche : On regarde 30 min avant l'horaire annoncé d'un train, puis on attend d'observer son arrivée réelle
    Cela correspond assez bien à l'expérience utilisateur
    Il y a peut-être une base de donnée qui compile des données historiques comparables, mais je n'ai pas encore trouvé
    Pour l'instant, on le fait en temps réel sur l'API
'''
####################################################################################################
# GOAL 2 : récupérer tous les ['VehicleJourneyName', 'forcasted_arrival_time30M' , 'arrival_time'] du RER B à Lozère vers CDG pendant une période de temps : 
# on identifie un train à VehicleJourneyName (VJN) : e.g. [{"value": "PIST76"}] identifiant unique dans la journée (?) 
####################################################################################################


# la base de la requête : pour Lozère vers  CDG i.e. 473931
api_token = '2Btko3bnqjqsyYIE6g8rJX7YwxjJ8pua'
api_url = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF%3AStopPoint%3AQ%3A473931%3A'
paris_timezone = pytz.timezone('Europe/Paris')



# DOESN'T WORK WELL YET

def real_arrival_times(delta_t):  # delta_t : temps en seconde pendant lequel on regarde tous les horaires d'arrivée exacts ; 

    # sort un dataframe à trois colonnes : la ref du train (que l'on peut lier à l'horaire prévu) , l'horaire prévu 30min avant et l'horaire réel d'arrivée

    df = pd.DataFrame(columns=['VehicleJourneyName', 'forcasted_arrival_time30M' , 'arrival_time'])
    count = 0 #pour le nombre de request
    arrival_times = []
    t =0
    while(t<= delta_t):
        
        request_time = datetime.now(paris_timezone).strftime('%Y-%m-%dT%H:%M:%S')
        head = {'apiKey' : api_token , 'Date': request_time}
        response = requests.get(api_url, headers=head)
        data = json.loads(response.content)

        ##################################
        # check for new train to add to the list
        # désolé la ligne est affreuse
        current_VJNs = [visit["MonitoredVehicleJourney"]["VehicleJourneyName"][0]["value"] 
                        for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"] 
                        if ("AEROPORT CH.DE GAULLE 2-MITRY CLAYE" in [direction["value"] for direction in visit["MonitoredVehicleJourney"]["DirectionName"]])]
        
        new_VJNs = [vjn for vjn in current_VJNs if vjn not in df['VehicleJourneyName'].values]
        # Create DataFrame with new values and placeholder values
        new_rows = pd.DataFrame({'VehicleJourneyName': new_VJNs,
                         'forcasted_arrival_time30M': [None] * len(new_VJNs),
                         'arrival_time': [None] * len(new_VJNs)})
        df = pd.concat([df, new_rows], ignore_index=True)


        ##################################
        #check for the 'forcasted_arrival_time30M' of those that aren't yet defined
        # Iterate over DataFrame rows where 'forcasted_arrival_time30M' is None
        # It is supposed to work (maybe a mistake in the then-now... )
        now = datetime.now(paris_timezone)
        for index, row in df[df['forcasted_arrival_time30M'].isnull()].iterrows():
            row_VJN = row[0]
            expected_arrival_time = [visit["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"] 
                                     for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"] 
                                     if (visit["MonitoredVehicleJourney"]["VehicleJourneyName"][0]["value"]==row_VJN)]
            
            # check of expected arrival_time isn't empty : 
            # sometimes it is apparently, at the moment the first VJN value disappears i.e. when a train arrives and if it has no forcasted_arrival_time30M
            if(expected_arrival_time!=[]):
                then = datetime.fromisoformat(expected_arrival_time[0]).astimezone(paris_timezone)
                time_difference = then - now
                #we check 30 minutes before expected_arrival
                # and we want to be sure the prediction is really about 30min before and not much less
                if ((time_difference.total_seconds() < 30 * 60) & (time_difference.total_seconds() > 25 * 60) ): # DEBUG 
                    df.loc[index , 'forcasted_arrival_time30M'] = then
                 

        ##################################
        #check if first train in stack at stop 
        first_vehicle_at_stop =  [visit["MonitoredVehicleJourney"]["MonitoredCall"]["VehicleAtStop"] 
                                  for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]]
        # check if this list isn't void
        if( (first_vehicle_at_stop!=[]) & first_vehicle_at_stop[0] ): 
                # get the VJNname of it  : 
                first_VJN = [visit["MonitoredVehicleJourney"]["VehicleJourneyName"][0]["value"] 
                                for visit in data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]][0]
                
                df.loc[df['VehicleJourneyName'] == first_VJN, 'arrival_time'] = request_time

        # affichage en console pour le débugage 
        print("df après " + str(count) + " requests")
        print(df)
        time.sleep(10) 
        t+=10
        count+=1



real_arrival_times(3600)


# suivre les trains plutôt ; moins précis : passé/pas passé plutôt que temps à l'arrêt ; Quel retard est significatif pour quelqu'un ?

# retard à l'arrivée, retard pendant le trajet ; Que présentent les bases de données de retard ; 

# capacité à absorber des flux exceptionels ; stade de france ; 

# essayer de détecter les travaux dans les données historiques ; 

# ségrégation des flux : unsupervised ? puis coupler avec des données de flux : où habite ? où travail ; là où ils arrivent 
# tourniquet: on compte à la sortie ; 

# sheet pour savoir ce qu'il y a dans les datasets ; 