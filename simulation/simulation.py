import pandas as pd
import simpy as simpy
import random
import statistics


class Station:
    def __init__(self, env):
        self.env = env
        self.pump_available = [simpy.Resource(env) for _ in range(2)]
        self.queue = simpy.Store(env)
        self.env.process(self.vehicle_generator())

    def vehicle_generator(self):
        arrival_time = 0
        while True:
            yield self.env.timeout(random.expovariate(1/5))  # Poisson arrival with rate 5 vehicles per minute
            self.env.process(self.vehicle(arrival_time))
            arrival_time += 1

    def vehicle(self, arrival_time):
        with self.queue.put((arrival_time, self.env.now)) as req:
            yield req
            with self.pump_available as pump:
                yield pump.request()
                yield self.env.timeout(1)  # Service time is 1 minute
                print(f"Vehicle arrived at {arrival_time} minutes, served at {self.env.now} minutes")

def gas_station_simulation():
    env = simpy.Environment()
    gas_station = Station(env)
    env.run(until=10)  # Run the simulation for 10 minutes

if __name__ == "__main__":
    gas_station_simulation()

class Simulation:
    def __init__(self, df):
        self.state = None
        self.results = None
        df['dist_to_next'] = (df['Sec Len'] + df['Sec Len'].shift(-1)) / 2
        df = df.astype({'AADT': int, 'LHRS': int,
                       'Latitude': float, 'Longitude': float})
        df['demand'] = df['AADT']*((1-(df['Truck %']/100))*0.033*0.02072)
        self.data = df
    
    def get_performance(self, current_state):
        if current_state == self.state:
            return self.results
        else:
            return 1