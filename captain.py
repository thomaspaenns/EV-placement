from model.model import Model
from simulation.simulation import Simulation
# from frontend import Frontend
import pandas as pd

class Captain:
    def __init__(self):
        self.model = Model()
        self.sim = Simulation()
        # self.frontend = Frontend(self.model, self.sim)

if __name__ == '__main__':
    Captain()