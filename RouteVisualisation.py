# Libraries
import numpy as np
from numpy.core.einsumfunc import _einsum_path_dispatcher  #?????
from numpy.lib.nanfunctions import _nanprod_dispatcher
import pandas as pd
import folium
import openrouteservice as ors

#################################### Region and Store Type Visualisation ####################################
ORSkey = "5b3ce3597851110001cf6248354cfef3acb24131a10df048bf5cddaf"

data = pd.read_csv("Store_Data_Some_zero_GROUPED.csv")

coords = data[['Long', 'Lat']]
coords = coords.to_numpy().tolist()

m = folium.Map(location = list(reversed(coords[2])), zoom_start=10)

for i in range(0, len(coords)):
    if data.Region[i]== "North":
        iconCol = "green"
    elif data.Region[i]== "South":
        iconCol = "cadetblue"
    elif data.Region[i]== "East":
        iconCol = "lightred"
    elif data.Region[i]== "West":
        iconCol = "darkblue"
    elif data.Region[i]== "Central":
        iconCol = "purple"

    if  "Countdown" in data.Store[i]:
        icon = "cloud"
    elif "FreshChoice" in data.Store[i]:
        icon = "tag"
    elif "SuperValue" in data.Store[i]:
        icon = "map-pin"
    elif "Distribution" in data.Store[i]:
        icon = "certificate"
# Add a key for the different icons

    folium.Marker(list(reversed(coords[i])), popup =data.Store[i], icon = folium.features.CustomIcon(color = iconCol, icon=icon, icon_size=(5, 5))).add_to(m)
m.save("RegionMap.html")

########################################### Route Visualisation #################################################################




# Selecting which set of routes to visualise
weekday = False

if(weekday == True):
    # Import dataframe with stores and associated coordinates
    data_nonZero = pd.read_csv("Store_Data_Nonzero_GROUPED.csv").to_numpy()
    
    # Stores in all of the generated routes
    allRoutes = np.loadtxt(open("Ordered_Route_Matrix.csv"),  delimiter=",", skiprows=0)
    # Numbers of routes used
    routeVectors = np.loadtxt(open("RouteVector_Weekday.csv"),  delimiter=",", skiprows=0)

    rearranged = [None]*len(routeVectors) # Storage for all routes in correct order
    rearrangedNames = [None]*len(routeVectors) # Collecting namea of stores for each route in the correct order

    for i in range(0,len(routeVectors)):
        index = allRoutes[:,int(routeVectors[i])] # Each route that is in the solution is accessed to identify which stores it contains ans in which order
        indexStores = routeVectors[i]
        temp = [] # Temporary storage for stores of each route
        temp2 = [] # Temporary storage for store names for each route
        # Adding the distribution centre as the first store visited
        temp.append((data_nonZero[55, 3], data_nonZero[55, 2]))

        # Find the order of stores that are stored in index and rearrange them in rearranged
        for j in range(1,len(index)+1):
            for n in range(0,len(index)):
                if(j==index[n]): # 

                    # Appending the long then lat of the store 
                    if n<55:
                        temp.append((data_nonZero[n, 3],data_nonZero[n, 2])) # columns are in wong order
                        temp2.append(data_nonZero[n, 1])
                    else:
                        temp.append((data_nonZero[n+1, 3],data_nonZero[n+1, 2]))
                        temp2.append(data_nonZero[n+1, 1])


        # Appending the distribution centre as the last store visited. 
        temp.append((data_nonZero[55, 3], data_nonZero[55, 2]))
        
        
        rearranged[i] = temp
        rearrangedNames[i] = temp2
    
    print(rearrangedNames) # Printing out names of stores in each route in order
    

    # Accessing Openstreet maps
    client = ors.Client(key=ORSkey)

    routeMapped = [] # To store each route, consisting of tuples of coordinates for each store
    for i in range(len(routeVectors)):
        temp2 = rearranged[i]
        for j in range (0,len(temp2)-1):
            routeMapped.append( client.directions(coordinates = [rearranged[i][j],rearranged[i][j+1]], profile='driving-hgv', format = 'geojson', validate = False))


    routeMap = folium.Map(location= [-36.95770671222872,174.814071322196], zoom_start=10)

    # Creating a single list of coordinates
    rearrangedFull = []
    rearrangedFull.append(routes for routes in rearranged)

    for i in range(len(routeMapped)): # Whatever it currently is
    
        currentCoordPair = routeMapped[i]
    
        folium.PolyLine(locations = [ list(reversed(rearrangedFull)) for rearrangedFull in currentCoordPair['features'][0]['geometry']['coordinates']]).add_to(routeMap)
    
    # Adding stores
    for i in range(0, len(coords)):
        if data.Region[i]== "North":
            iconCol = "green"
        elif data.Region[i]== "South":
            iconCol = "cadetblue"
        elif data.Region[i]== "East":
            iconCol = "lightred"
        elif data.Region[i]== "West":
            iconCol = "darkblue"
        elif data.Region[i]== "Central":
            iconCol = "purple"

        if  "Countdown" in data.Store[i]:
            icon = "cloud"
        elif "FreshChoice" in data.Store[i]:
            icon = "tag"
        elif "SuperValue" in data.Store[i]:
            icon = "map-pin"
        elif "Distribution" in data.Store[i]:
            icon = "certificate"

        folium.Marker(list(reversed(coords[i])), popup =data.Store[i], icon = folium.Icon(color = iconCol, icon=icon)).add_to(routeMap)


    routeMap.save("WeekdayRoutesMap.html")

# Weekend

if(weekday == False):
    # Import dataframe with stores and associated coordinates for the weekend
    data_someZero = pd.read_csv("Store_Data_Some_zero_GROUPED.csv").to_numpy()
    
    # Stores in all of the generated routes (same as weekday, only the associated demand array was changed)
    allRoutes = pd.read_csv("Ordered_Route_Matrix.csv").to_numpy()
    
    # Numbers of routes used in the weekend solution
    routeVectors = pd.read_csv("RouteVector_Weekend.csv").to_numpy()

    rearranged = [None]*len(routeVectors) # Storage for all routes in correct order
    rearrangedNames = [None]*len(routeVectors) # Collecting namea of stores for each route in the correct order

    for i in range(0,len(routeVectors)):
        index = allRoutes[:,int(routeVectors[i])] # Each route that is in the solution is accessed to identify which stores it contains ans in which order
        indexStores = routeVectors[i,:]
        temp = [] # Temporary storage for stores of each route
        temp2 = []# Temporary storage for store names of each route

        # Adding the distribution centre as the first store visited
        temp.append((data_someZero[55, 3], data_someZero[55, 2]))

        # Find the order of stores that are stored in index and rearrange them in rearranged
        for j in range(1,len(index)):
            for n in range(0,len(index)):
                if(j==index[n]): # 
                    
                    # Appending the long then lat of the store 
                    if n<55:
                        temp.append((data_someZero[n, 3],data_someZero[n, 2])) # columns Long, Lat
                        temp2.append(data_someZero[n+1, 1]) # Store names
                    else:
                        temp.append((data_someZero[n+1, 3],data_someZero[n+1, 2])) # columns Long, Lat
                        temp2.append(data_someZero[n+1, 1]) # Store names


        # Appending the distribution centre as the last store visited. 
        temp.append((data_someZero[55, 3], data_someZero[55, 2]))

        rearranged[i] = temp # Recording coordindates of each store in order
        rearrangedNames[i] = temp2 # Recording names of each store in order
    
    print(rearrangedNames) # Printing out names of stores in each route in order
    

    # Plot each route on a map of Auckland
    
    # Accessing Openstreet maps
    client = ors.Client(key=ORSkey)

    # Getting directions from client
    routeMapped = []
    for i in range(len(routeVectors)):
        temp2 = rearranged[i]
        for j in range (0,len(temp2)-1):
            routeMapped.append( client.directions(coordinates = [rearranged[i][j],rearranged[i][j+1]], profile='driving-hgv', format = 'geojson', validate = False))


    routeMap = folium.Map(location= [-36.95770671222872,174.814071322196], zoom_start=10)

    # Creating a single list of coordinates
    rearrangedFull = []
    rearrangedFull.append(routes for routes in rearranged)

    # Creating lines for each route and adding to map
    for i in range(len(routeMapped)): # Whatever it currently is
    
        currentCoordPair = routeMapped[i]
    
        folium.PolyLine(locations = [ list(reversed(rearrangedFull)) for rearrangedFull in currentCoordPair['features'][0]['geometry']['coordinates']]).add_to(routeMap)
    
    # Adding store markers
    for i in range(0, len(coords)):
        if data.Region[i]== "North":
            iconCol = "green"
        elif data.Region[i]== "South":
            iconCol = "cadetblue"
        elif data.Region[i]== "East":
            iconCol = "lightred"
        elif data.Region[i]== "West":
            iconCol = "darkblue"
        elif data.Region[i]== "Central":
            iconCol = "purple"

        if  "Countdown" in data.Store[i]:
            icon = "cloud"
        elif "FreshChoice" in data.Store[i]:
            icon = "tag"
        elif "SuperValue" in data.Store[i]:
            icon = "map-pin"
        elif "Distribution" in data.Store[i]:
            icon = "certificate"

        folium.Marker(list(reversed(coords[i])), popup =data.Store[i], icon = folium.Icon(color = iconCol, icon=icon )).add_to(routeMap)

    routeMap.save("WeekendRoutesMap.html")



