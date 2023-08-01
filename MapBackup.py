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
'''
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

    folium.Marker(list(reversed(coords[i])), popup =data.Store[i], icon = folium.Icon(color = iconCol, icon=icon)).add_to(m)
m.save("RegionMap.html")
'''
########################################### Route Visualisation #################################################################




# Selecting which set of routes to visualise
weekday = True

if(weekday == True):
    # Import dataframe with stores and associated coordinates
    data_nonZero = pd.read_csv("Store_Data_Nonzero_GROUPED.csv").to_numpy()
    
    # Stores in all of the generated routes
    allRoutes = pd.read_csv("Ordered_Route_Matrix.csv").to_numpy()
    # Numbers of routes used
    routeVectors = pd.read_csv("RouteVector_Weekday.csv").to_numpy()

    rearranged = [None]*len(routeVectors) # Storage for all routes in correct order

    for i in range(0,len(routeVectors)):
        index = allRoutes[:,int(routeVectors[i])] # Each route that is in the solution is accessed to identify which stores it contains ans in which order
        indexStores = routeVectors[i,:]
        temp = [] # Temporary storage for stores of each route
        # Adding the distribution centre as the first store visited
        temp.append((data_nonZero[55, 3], data_nonZero[55, 2]))

        # Find the order of stores that are stored in index and rearrange them in rearranged
        for j in range(1,len(index)):
            for n in range(0,len(index)):
                if(j==index[n]): # 
                    # Appending the long then lat of the store 
                    temp.append((data_nonZero[n, 3],data_nonZero[n, 2])) # columns are in wong order

        # Appending the distribution centre as the last store visited. 
        temp.append((data_nonZero[55, 3], data_nonZero[55, 2]))

        rearranged[i] = temp

    # Plot each route on a map of Auckland
    # Map of Weekday Routes

    # Accessing Openstreet maps
    client = ors.Client(key=ORSkey)

    routeMapped = []



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

    for i in range(0,len(routeVectors)):
        index = allRoutes[:,int(routeVectors[i])] # Each route that is in the solution is accessed to identify which stores it contains ans in which order
        indexStores = routeVectors[i,:]
        temp = [] # Temporary storage for stores of each route
        # Adding the distribution centre as the first store visited
        temp.append((data_someZero[55, 3], data_someZero[55, 2]))

        # Find the order of stores that are stored in index and rearrange them in rearranged
        for j in range(1,len(index)):
            for n in range(0,len(index)):
                if(j==index[n]): # 
                    # Appending the long then lat of the store 
                    temp.append((data_someZero[n, 3],data_someZero[n, 2])) # columns are in (Long, Lat) order

        # Appending the distribution centre as the last store visited. 
        temp.append((data_someZero[55, 3], data_someZero[55, 2]))

        rearranged[i] = temp

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

        folium.Marker(list(reversed(coords[i])), popup =data.Store[i], icon = folium.Icon(color = iconCol, icon=icon )).add_to(routeMap)

    routeMap.save("WeekendRoutesMap.html")



########################################### Demand Visualisation ############################################

'''

import seaborn as sns
import matplotlib.pyplot as plt ###???

# Seperate the data into regions 
North = data.loc[data["Region"]=='North']
South = data.loc[data["Region"]=='South']
East = data.loc[data["Region"]=='East']
West = data.loc[data["Region"]=='West']
Central= data.loc[data["Region"]=='Central']

# Import data for different day types
data_someZero = data
data_nonZero = pd.read_csv("Store_Data_Nonzero_GROUPED.csv")


# Some 0 data
fig = plt.figure()
plt.title("Saturday Demand Estimation")
# North 
ax1 = fig.add_subplot(2,3,1, xlabel="North Region")
#ax1 = plt.subplot(111)
sns.barplot(x="Store", y="Demand Estimate", hue="Store", data= North, ax=ax1, palette= "viridis")
ax1.axes.xaxis.set_visible(False)
ax1.legend(loc='right')
# South
ax2 = fig.add_subplot(2,3,2, xlabel="South Region")
#ax2 = plt.subplot(112)
sns.barplot(x="Store", y="Demand Estimate", hue="Store", data= South, ax=ax2,  palette= "flare")
ax2.axes.xaxis.set_visible(False)
ax2.axes.yaxis.set_visible(False)
ax2.legend(loc='right')
# East 
ax3 = fig.add_subplot(2,3,3, xlabel="East Region")
#ax3 = plt.subplot(113, sharey= 121)
sns.barplot(x="Store", y="Demand Estimate", hue="Store", data= East, ax=ax3,  palette= "icefire")
ax3.axes.xaxis.set_visible(False)
ax3.axes.yaxis.set_visible(False)
ax3.legend(loc='right')
# West
ax4 = fig.add_subplot(2,3,4, xlabel="West Region Stores")
#ax4 = plt.subplot(211)
sns.barplot(x="Store", y="Demand Estimate", hue="Store", data= West, ax=ax4,  palette= "pastel")
ax4.axes.xaxis.set_visible(False)
ax4.axes.yaxis.set_visible(False)
ax4.legend(loc='right')
# Central 
ax5 = fig.add_subplot(2,3,5, xlabel="Central Region Stores")
#ax5 = plt.subplot(212)
sns.barplot(x="Store", y="Demand Estimate", hue="Store", data= Central, ax=ax5,  palette= "YlOrRd")
ax5.axes.xaxis.set_visible(False)
ax5.axes.yaxis.set_visible(False)
ax5.legend(loc='right')


plt.close(2)
plt.close(3)
#plt.tight_layout()
# No 0 data
fig2 = plt.figure()


#f, ax = plt.subplots(1, 2, sharex=False)

#sns.displot(data_someZero, x= "Store", y= "Demand", col= "Region", ax= ax[0])

#sns.displot(data_nonZero, x= "Store", y= "Demand", col= "Region", ax=ax[1] )
# Removing distribution centre for demand estimation plot
#data_someZero.drop(index= 55, axis=0, inplace=True)

g = sns.catplot(x= "Region", y= "Demand Estimate", hue="Store", kind="bar", data =data_someZero, dodge=True, col="Region", col_wrap=3, sharex=False, palette=sns.color_palette("rocket"), )
for axes in g.axes.ravel():
    axes.legend()
#g.axes.ravel()
plt.show()




plt.show()
'''
