import numpy as np

class PolicyManager(object):

    DAILY_EXPENSE_FACTOR = 1e3
    
    def __init__(self, world):
        self.world = world
    
    def add_medic(self, x, y, capacity, rating):
        self.world.medics.loc[len(self.world.medics)] = [x, y, capacity, rating]
