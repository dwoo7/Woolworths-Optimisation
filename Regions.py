import numpy as np
import pandas as pd

def set_boundaries(filename):

    #read in stores data file and add region column to the end
    stores_df = pd.read_csv(filename)
    stores_df["Region"] = ""
    loc_len = len(stores_df.index)
    
    
    ######## BOUNDARIES FOR THE EAST REGION ########
    #Left bound of East region - Countdown Meadowbank
    CD_Meadowbank_index = int(stores_df[stores_df['Store']=='Countdown Meadowbank'].index.values)
    CD_Meadowbank_x = stores_df.loc[CD_Meadowbank_index]['x']

    #South bound of East region - FreshChoice Otahuhu
    FC_Otahuhu_index = int(stores_df[stores_df['Store']=='FreshChoice Otahuhu'].index.values)
    FC_Otahuhu_y = stores_df.loc[FC_Otahuhu_index]['y']

    
    ######## BOUNDARIES FOR THE NORTH REGION ########
    #South bound in North region - Countdown Birkenhead
    CD_Birkenhead_index = int(stores_df[stores_df['Store']=='Countdown Birkenhead'].index.values)
    CD_Birkenhead_y = stores_df.loc[CD_Birkenhead_index]['y']

    #Left bound in North region - Countdown Glenfield
    CD_Glenfield_index = int(stores_df[stores_df['Store']=='Countdown Glenfield'].index.values)
    CD_Glenfield_x = stores_df.loc[CD_Glenfield_index]['x']
    

    ######## BOUNDARIES FOR THE CENTRAL REGION ########
    #Left bound - Countdown Pt Chevalier
    CD_PtChev_index = int(stores_df[stores_df['Store']=='Countdown Pt Chevalier'].index.values)
    CD_PtChev_x = stores_df.loc[CD_PtChev_index]['x']

    #Right bound - Countdown Greenlane
    CD_Greenlane_index = int(stores_df[stores_df['Store']=='Countdown Greenlane'].index.values)
    CD_Greenlane_x = stores_df.loc[CD_Greenlane_index]['x']

    #Countdown Lynfield exception
    CD_Lynfield_index = int(stores_df[stores_df['Store']=='Countdown Lynfield'].index.values)
    CD_Lynfield_x = stores_df.loc[CD_Lynfield_index]['x']



    #assigning each store to their respective region
    for i in range (loc_len):

        store_x = stores_df.loc[i]['x']
        store_y = stores_df.loc[i]['y']

        #All stores south of the Distribution Centre (DC)
        if store_y < 0:
             stores_df.loc[i, 'Region'] = 'South'
        
        #All stores in the Northern region bound by Countdown Birkenhead and Glenfield
        elif store_y >= CD_Birkenhead_y and store_x >= CD_Glenfield_x:
            stores_df.loc[i, 'Region'] = 'North'

        #All stores in the Eastern region bound by Countdown Meadowbank and FreshChoice Otahuhu
        elif store_x >= CD_Meadowbank_x and store_y >= FC_Otahuhu_y:
            stores_df.loc[i, 'Region'] = 'East'
        
        #All stores in the Central region bound by Countdown Pt Chevalier and Greenlane
        elif store_x >= CD_PtChev_x and store_x <= CD_Greenlane_x and store_x != CD_Lynfield_x:
            stores_df.loc[i, 'Region'] = 'Central'
        
        #Distribution Centre (x,y) = (0,0)
        elif store_x == 0 and store_y == 0:
            stores_df.loc[i, 'Region'] = 'Central/Distribution'

        #remaining stores assigned to West region
        else:
            stores_df.loc[i, 'Region'] = 'West'

    #check accuracy
    Southcount = 0
    Eastcount = 0
    Centralcount = 0
    Northcount = 0
    Westcount = 0

    for i in range(loc_len):
        if stores_df.loc[i, 'Region'] == 'West':
            Westcount += 1
        elif stores_df.loc[i, 'Region'] == 'South':
            Southcount += 1
        elif stores_df.loc[i, 'Region'] == 'Central':
            Centralcount += 1
        elif stores_df.loc[i, 'Region'] == 'North':
            Northcount += 1
        elif stores_df.loc[i, 'Region'] == 'East':
            Eastcount += 1
    
    stores_df.to_csv(filename.split('.csv')[0] + "_GROUPED.csv")

    #print("South count = {}".format(Southcount))
    #print("East count = {}".format(Eastcount))
    #print("Central count = {}".format(Centralcount))
    #print("West count = {}".format(Westcount))
    #print("North count = {}".format(Northcount))

if __name__ == "__main__":

    set_boundaries("Store_Data_Nonzero.csv")
    set_boundaries("Store_Data_Some_zero.csv")