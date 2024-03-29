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
        self.covered = None

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
    
    # A method to get the optimal station locations and covered surrounding areas
    # based on the budget, the set_stations (set by user) and the existing
    # stations (if the toggle is enabled)
    def get_optimal(self, budget, set_stations, existing_stations=None, year=2024):
        year_convert = {2024:1.0, 2029: 4.12, 2034:7.24, 2039:10.36, 2044:13.48, 2049: 16.6}
        # year_convert = {2024:1.0, 2029: 4.12, 2034:9.24, 2039:13.36, 2044:17.48, 2049: 21.6} #75%
        yr_scalar = year_convert[year]
        # Create Sets and Params
        I = self.data['LHRS']
        J = I
        C = [1, 2, 3] #corresponding to 2, 4, and 8 charging stations
        Cap = {1: 96, 2: 192, 3: 384}  # Cars charged per day (2 per hr per port)
        d = dict(zip(I, self.data['demand']*yr_scalar))
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
        # print(existing_stations)
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
                    self.model.addConstr(x[int(key),set_stations[key]] == 1) #If this breaks, sanitize lhrs to int
        elif set_stations and existing_stations:
            for key in set_stations:
                if int(key) in existing_stations.keys() or set_stations[key] > 0:
                    set_ports = 2**set_stations[key] if (set_stations[key] > 0) else 0
                    exist_ports = existing_stations[int(key)] if (int(key) in existing_stations.keys()) else 0
                    num_ports = set_ports + exist_ports
                    stat_type = 0
                    if 0 < num_ports and num_ports < 3:
                        stat_type = 1
                    elif 2 < num_ports and num_ports < 7:
                        stat_type = 2
                    elif 6 < num_ports:
                        stat_type = 3
                    self.model.addConstr(x[int(key),stat_type] == 1) #If this breaks, sanitize lhrs to int
        # Optimize
        self.model.optimize()
        # self.model.printAttr('x')
        optimal = {}
        covered = {}
        ranges = {}
        for v in self.model.getVars():
            if f"{v.VarName}".startswith("x"):
                # print(v.VarName)
                # print(v.x)
                if int(v.x) == 1:
                    # print(v.VarName)
                    # print(v.x)
                    optimal.update({int(f"{v.VarName}"[2:7]):int(f"{v.VarName}"[8])})
                    source = int(f"{v.VarName}"[2:7])
                    if source in covered.keys():
                        current = covered[source]
                        current.update({source:0})
                        covered.update({source:current})
                    else:
                        covered.update({source:{source:0}})
                    for reciever, dist in paths[source].items():
                        if dist < R:
                            if reciever in ranges.keys():
                                current = ranges[reciever]
                                current.update({source:dist})
                                ranges.update({reciever:current})
                            else:
                                ranges.update({reciever:{source:dist}})

                elif int(v.x) == 0 and int(f"{v.VarName}"[2:7]) not in optimal.keys():
                    optimal.update({int(f"{v.VarName}"[2:7]):0})
            elif f"{v.varName}".startswith("y"):
                if int(v.x) == 1:
                    source = int(f"{v.varName}"[2:7])
                    reciever = int(f"{v.varName}"[8:13])
                    distance = paths[int(reciever)][int(source)]
                    if reciever in covered.keys():
                        current = covered[reciever]
                        current.update({source:distance})
                        covered.update({reciever:current})
                    else:
                        covered.update({reciever:{source:distance}})
        self.covered = covered
        self.optimal = optimal
        self.ranges = ranges
        # print(optimal)
        # print("COVERED:")
        # print(covered)
        # print("RANGES:")
        # print(ranges)
        return self.optimal
    
    def get_coverage(self):
        if self.covered:
            return self.covered
        else:
            raise Exception("Model must be optimized to get coverage!")
        
    def get_ranges(self):
        if self.ranges:
            return self.ranges
        else:
            raise Exception("Model must be optimized to get ranges!")
    