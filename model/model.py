import gurobipy as gp
from gurobipy import GRB as GRB
import pandas as pd
import networkx as nx
import numpy as np

class Model:
    def __init__(self):
        self.data = self.pull_data(file_name='401_Data.csv')
        self.network = self.create_network(self.data)
        self.model = self.create_model(self.data, self.network)

    def pull_data(self, file_name):
        # df = pd.read_csv('401_Data.csv')
        df = pd.read_csv('model/401_Data.csv',
                 encoding='ISO-8859-1')
        df['dist_to_next'] = (df['Sec Len'] + df['Sec Len'].shift(-1)) / 2
        df = df.astype({'AADT':int, 'LHRS':int, 'Latitude':float, 'Longitude':float})
        df['demand'] = df['AADT']*((1-(df['Truck %']/100))*0.033*0.02072)
        return df

    def create_network(self, df):
        G = nx.Graph()
        for index, row in df.iterrows():
            next_index = index + 1
            if next_index < len(df):
                current_segment = row['LHRS']
                next_segment = df.loc[next_index, 'LHRS']
                G.add_edge(int(current_segment), int(next_segment), length=float(row['dist_to_next']))
        return G
    
    def create_model(self, df, G):
        # Create Sets and Params
        I = df['LHRS']
        J = I
        C = [1,2,3]
        Cap = {1:48,2:96,3:192} #Cars charged per hour (2 per port)
        d = dict(zip(I, df['demand']))
        f = {
            1:dict(zip(I, df['cost 1'])),
            2:dict(zip(I, df['cost 2'])),
            3:dict(zip(I, df['cost 3']))
        }
        R = 40
        Budget = 300000
        #Compute shortest path lengths
        paths = {}
        for lhrs_num in df['LHRS']:
            paths.update({lhrs_num: nx.shortest_path_length(G, source=lhrs_num, weight='length')})
        l = paths
        # Create environment with WLS license
        e = gp.Env(empty=True)
        e.setParam('WLSACCESSID', '7e2d40a7-904b-4d00-b37c-6993c3716fb6')
        e.setParam('WLSSECRET', '731bbd0f-37ee-4c88-9d28-c4f67b9c7952')
        e.setParam('LICENSEID', 2396892)
        e.start()
        # Create the model within the Gurobi environment
        model = gp.Model(env=e)