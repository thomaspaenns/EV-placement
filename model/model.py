import gurobipy as gp
from gurobipy import GRB as GRB
import pandas as pd
import networkx as nx
import numpy as np


class Model:
    def __init__(self, df):
        self.data = self.pull_data(df)
        self.network = self.create_network(self.data)
        self.model = self.create_model(self.data, self.network)
        self.optimal = None
        self.set_stations = None

    def pull_data(self, df):
        df['dist_to_next'] = (df['Sec Len'] + df['Sec Len'].shift(-1)) / 2
        df = df.astype({'AADT': int, 'LHRS': int,
                       'Latitude': float, 'Longitude': float})
        df['demand'] = df['AADT']*((1-(df['Truck %']/100))*0.033*0.02072)
        return df

    def create_network(self, df):
        G = nx.Graph()
        for index, row in df.iterrows():
            next_index = index + 1
            if next_index < len(df):
                current_segment = row['LHRS']
                next_segment = df.loc[next_index, 'LHRS']
                G.add_edge(int(current_segment), int(next_segment),
                           length=float(row['dist_to_next']))
        return G

    def create_model(self, df, G):
        # Create environment with WLS license
        e = gp.Env(empty=True)
        e.setParam('WLSACCESSID', '7e2d40a7-904b-4d00-b37c-6993c3716fb6')
        e.setParam('WLSSECRET', '731bbd0f-37ee-4c88-9d28-c4f67b9c7952')
        e.setParam('LICENSEID', 2396892)
        e.start()
        # Create the model within the Gurobi environment
        model = gp.Model(env=e)
        return model
    
    def get_optimal(self, budget, set_stations, existing_stations=None):
        # Create Sets and Params
        I = self.data['LHRS']
        J = I
        C = [1, 2, 3] #corresponding to 2, 4, and 8 charging stations
        Cap = {1: 96, 2: 192, 3: 384}  # Cars charged per day (2 per hr per port)
        d = dict(zip(I, self.data['demand']))
        f = {
            1: dict(zip(I, self.data['cost 1'])),
            2: dict(zip(I, self.data['cost 2'])),
            3: dict(zip(I, self.data['cost 3']))
        }
        R = 40 # Coverage range from a station (km)
        # Compute shortest path lengths
        paths = {}
        for lhrs_num in self.data['LHRS']:
            paths.update({lhrs_num: nx.shortest_path_length(
                self.network, source=lhrs_num, weight='length')})
        l = paths
        #Do budget calculation for existing stations
        if existing_stations:
            for key in existing_stations:
                num_ports = existing_stations[key]
                stat_type = 0
                if 0 < num_ports and num_ports < 3:
                    existing_stations.update({key:2})
                    stat_type = 1
                elif 2 < num_ports and num_ports < 7:
                    existing_stations.update({key:4})
                    stat_type = 2
                elif 6 < num_ports:
                    existing_stations.update({key:8})
                    stat_type = 3
                budget = budget + f[stat_type][key]
        # Remove old constraints and decision variables
        self.model.remove(self.model.getVars()) #Might break
        self.model.remove(self.model.getConstrs())
        # Add decision variables
        x = self.model.addVars(I, C, vtype=GRB.BINARY, name="x")
        y = self.model.addVars(I, J, vtype=GRB.BINARY, name="y")
        # Add generic constraints
        [self.model.addConstr(sum(x[i, c] for c in C) <= 1) for i in I]
        [self.model.addConstr(
            sum(d[j]*y[i, j] for j in J) <= sum(Cap[c]*x[i,c] for c in C)
        ) for i in I]
        [self.model.addConstr(l[i][j]*y[i,j] <= R) for i in I for j in J]
        self.model.addConstr(sum(f[c][i]*x[i,c] for i in I for c in C) <= budget)
        self.model.setObjective(sum(d[j]*y[i,j] for i in I for j in J), sense=GRB.MAXIMIZE)
        # Add must-have station constraints and existing station constraints
        if set_stations and not existing_stations:
            for key in set_stations:
                if set_stations[key] > 0:
                    self.model.addConstr(x[key,set_stations[key]] == 1) #If this breaks, sanitize lhrs to int
        if set_stations and existing_stations:
            for key in set_stations:
                if set_stations[key] > 0:
                    if key in existing_stations.keys():
                        num_ports = existing_stations[key] + 2^set_stations[key]
                        stat_type = 0
                        if 0 < num_ports and num_ports < 3:
                            stat_type = 1
                        elif 2 < num_ports and num_ports < 7:
                            stat_type = 2
                        elif 6 < num_ports:
                            stat_type = 3
                        self.model.addConstr(x[key,stat_type] == 1) #If this breaks, sanitize lhrs to int
                    else:
                        self.model.addConstr(x[key,set_stations[key]] == 1) #If this breaks, sanitize lhrs to int
        # Optimize
        self.model.optimize()
        optimal = {}
        for v in self.model.getVars():
            if f"{v.VarName}".startswith("x"):
                if int(v.x) == 1:
                    optimal.update({f"{v.VarName}"[2:7]:f"{v.VarName}"[8]})
                else:
                    optimal.update({f"{v.VarName}"[2:7]:0})
        self.optimal = optimal
        return self.optimal

