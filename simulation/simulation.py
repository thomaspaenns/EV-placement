import pandas as pd

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