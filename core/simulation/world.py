import time
import numpy as np
import pandas as pd
from collections import namedtuple

# World settings

Region = pd.DataFrame({
    # id of region
    'region_id': [0, 1],
    # name of region
    'region_name': ['USA', 'India'],
    # probability of people travelling locally
    'travel_dom': [0.9, 0.9],
    # probability of people travelling internationally
    'travel_int': [0.2, 0.2],
    # probability of people begin quarantined
    'quarantie': [0.0, 0.0],
    # Xmin of region
    'xmin': [0, 110],
    # Xmax of region
    'xmax': [100, 210],
    # Ymin of region
    'ymin': [0, 0],
    # Ymax of region
    'ymax': [100, 100],
    # infection radius of region
    'infection_radius': [1.0, 1.0],
    # probability that a person in contact with infected person will also get infected
    'prob_of_spread': [0.2, 0.2],
    # variance of domestic travel
    'domestic_travel_step': [1.0, 1.0]
})

People = pd.DataFrame({
    'person_id': [],                            # unique id of the person
    'home_region_name': [],                     # home region of the person (static)
    'region_name': [],                          # current region of the person
    'x': [],                                    # current x position of the person
    'y': [],                                    # current y position of the person
    'alive': [],                                # 0/1 if person is alive or not
    'infection': [],                            # degree of infection the person has [0, 1]
})

class World(object):

    def __init__(self, num_people=1000):
        self.num_people = num_people
        self.people = People
        self.regions = Region
        self.t = 0

        self.initialize()

    def initialize(self):
        # initialize world dataframe
        print('Initializing a {}x{} world...'.format(len(self.regions), self.num_people))

        # loop for each region
        for i, region in enumerate(self.regions.region_name):
            # get region window
            xmin, xmax, ymin, ymax = self.regions.loc[i, ['xmin', 'xmax', 'ymin', 'ymax']].values.tolist()
            
            # create region population
            region_population = pd.DataFrame({
                'person_id': range(i*self.num_people+1, i*self.num_people+1+self.num_people),
                'home_region_name': [region] * self.num_people,
                'region_name': [region] * self.num_people,
                'x': np.random.uniform(low=xmin, high=xmax, size=(self.num_people, )),
                'y': np.random.uniform(low=ymin, high=ymax, size=(self.num_people, )),
                'alive': [1] * self.num_people,
                'infection': [0.0] * self.num_people,
            })

            # add region population to world population
            self.people = pd.concat([self.people, region_population], axis=0).reset_index(drop=True)
    
    def simulate(self):
        self.t += 1
        start = time.time()
        
        self.move()
        # self.spread_infections()

        end = time.time()
        print('Time taken to simulate: {} seconds'.format(end-start))
    
    def move(self):
        self.move_demestic()
        self.move_international()
    
    def move_demestic(self):
        # simulate domestic travel

        # join people and regions
        combined = pd.merge(self.people, self.regions, on='region_name')

        # get people who will move
        move_idx = np.random.random((combined.shape[0], )) < combined['travel_dom']
        
        # move people
        move_x = np.random.normal(scale=combined.loc[move_idx, 'domestic_travel_step']).reshape((-1, 1))
        move_y = np.random.normal(scale=combined.loc[move_idx, 'domestic_travel_step']).reshape((-1, 1))
        move_xy = np.concatenate([move_x, move_y], axis=1)
        combined.loc[move_idx, ['x', 'y']] += move_xy

        # ensure no one leaves region while travelling domestic
        combined.loc[move_idx, 'x'] = combined.loc[move_idx, 'x'].clip(combined.loc[move_idx, 'xmin'], combined.loc[move_idx, 'xmax'])
        combined.loc[move_idx, 'y'] = combined.loc[move_idx, 'y'].clip(combined.loc[move_idx, 'ymin'], combined.loc[move_idx, 'ymax'])

        # get new people dataframe from movers
        self.people.loc[move_idx, ['x', 'y']] = combined.loc[move_idx, ['x', 'y']]

    def move_international(self):
        # simulate international travel

        # if only one region in simulaton, return as no international travel possible
        if len(self.regions) == 1:
            return

        # join people and regions
        combined = pd.merge(self.people, self.regions, on='region_name')

        # get people who will move
        move_idx = np.random.random((combined.shape[0], )) < combined['travel_int']
        
        # update region name of movers to new random region
        combined.loc[move_idx, 'region_name'] = combined.loc[move_idx, 'region_name'].apply(lambda region: self.regions[self.regions.region_name != region].region_name.sample(n=1).item())
        
        # get new location of movers as midpoint of new region
        movers_comb = combined.loc[move_idx, ['region_name', 'x', 'y']].merge(self.regions, on='region_name').set_index(combined.loc[move_idx, :].index)
        movers_comb.loc[:, 'x'] = (movers_comb.xmin + movers_comb.xmax) / 2.0
        movers_comb.loc[:, 'y'] = (movers_comb.ymin + movers_comb.ymax) / 2.0

        # update co-ordinates and region name of international travellers
        self.people.loc[move_idx, ['x', 'y', 'region_name']] = movers_comb.loc[:, ['x', 'y', 'region_name']]
    
    def spread_infections(self):
        # infect new people

        for i, region in enumerate(self.regions.region_name):

            # get region population
            local = self.people.loc[self.people.region_name == region, :]
            
            # calculate distances between each person in the region
            Xdiff = (local.x.values[:, None] - local.x.values) ** 2
            Ydiff = (local.y.values[:, None] - local.y.values) ** 2
            # distance is N x N matrix of squared distances between each pair of points
            distance = Xdiff + Ydiff

            # filter distances for infected people only since they'll spread infection
            infected_mask = local.infection > 0.0
            infected_dist = distance[infected_mask]

            # calculate people in threshold distance
            thres = np.argwhere(infected_dist <= (self.regions.loc[i, 'infection_radius'] ** 2))
            thres_infectee = thres[:, 0]                        # already infected people
            thres_infected = thres[:, 1]                        # in threshold distance to infected people

            # index of people who are in threshold distance to infected people and are currently uninfected
            idx = local.loc[thres_infected, 'infection'] == 0.0
            
            infection_creators = thres_infectee[idx]
            candidates = thres_infected[idx]
            
            if candidates.size > 0:
                # get prob that each candidate will get infection
                cand_prob = np.random.random(candidates.shape) <= self.regions.loc[i, 'prob_of_spread']
                
                infection_creators = infection_creators[cand_prob]
                newly_infected = candidates[cand_prob]

                # infect candidates :(
                self.people.loc[newly_infected, 'infection'] = self.people.loc[infection_creators, 'infection']

if __name__ == '__main__':
    world = World()
    world.simulate()