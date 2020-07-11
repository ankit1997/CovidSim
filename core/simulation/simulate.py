import numpy as np
import pandas as pd
from numba import njit
from queue import Queue
from random import random, shuffle, normalvariate

from core.simulation.entity.people import PEOPLE
from core.simulation.entity.regions import REGIONS

PROB_LETHAL = 0.3

class Simulator(object):

	'''
		Simulator class
		Arguments:
			`num_people`: Number of people per region
	'''

	def __init__(self, num_people):
		self.num_people = num_people
		self.people = PEOPLE
		self.regions = REGIONS
		self.T = 0
		self.frameQueue = Queue()
		self.create_people()
	
	def create_people(self):
		# create people per region

		print('Creating a {}x{} world...'.format(len(self.regions), self.num_people))

		# loop for each region
		for i, region in enumerate(self.regions.region_id):
			
			# get region window
			xmin, xmax, ymin, ymax = self.regions.loc[i, ['xmin', 'xmax', 'ymin', 'ymax']].values.tolist()
			
			# create region population
			region_population = pd.DataFrame({
				'person_id': range(i*self.num_people+1, i*self.num_people+1+self.num_people),
				'home_region_id': [region] * self.num_people,
				'region_id': [region] * self.num_people,
				'x': (np.random.random(size=(self.num_people, ))) * (xmax-xmin) + xmin,
				'y': (np.random.random(size=(self.num_people, ))) * (ymax-ymin) + ymin,
				'alive': [1] * self.num_people,
				'infection': [0.0] * self.num_people,
			})

			# add region population to world population
			self.people = pd.concat([self.people, region_population], axis=0).reset_index(drop=True)
	
	def initialize_infections(self, num_infections=5):
		# set few people with infections
		idx = self.people.sample(n=num_infections).index
		self.people.loc[idx, 'infection'] = 0.1
	
	def set_policy(self, region_id, key, value):
		# update region policy
		self.regions.loc[self.regions.region_id == region_id, key] = value
	
	def get_SIR(self):
		return self._get_SIR(
			self.people.loc[:, ['region_id', 'alive', 'infection']].values,
			self.regions.loc[:, ['region_id', 'xmax', 'ymin', 'ymax', 'visible_infection']].values
		)
	
	def call(self):

		# current timestep
		self.T += 1

		# travel people around
		self.people.loc[:, 'x'], self.people.loc[:, 'y'], self.people.loc[:, 'region_id'] = self.travel(
			self.people.loc[:, ['home_region_id', 'region_id', 'x', 'y', 'alive']].values, 
			self.regions.loc[:, ['region_id', 'xmin', 'xmax', 'ymin', 'ymax', 'travel_dom', 'travel_int_in', 'travel_int_out', 'domestic_travel_step']].values
		)

		# spread infection
		self.people.loc[:, 'infection'] = self.spread_infections(
			self.people.loc[:, ['x', 'y', 'alive', 'infection', 'region_id']].values, 
			self.regions.loc[:, ['region_id', 'prob_of_spread', 'infection_radius']].values
		)

		# change severity
		self.people.loc[:, 'alive'], self.people.loc[:, 'infection'] = self.change_severity(
			self.people.loc[:, 'alive'].values, 
			self.people.loc[:, 'infection'].values
		)

		# social distancing
		self.people.loc[:, 'x'], self.people.loc[:, 'y'] = self.social_distancing(
			self.people.loc[:, ['x', 'y', 'alive', 'region_id']].values,
			self.regions.loc[:, ['region_id', 'xmin', 'xmax', 'ymin', 'ymax', 'social_distancing']].values
		)

	@staticmethod
	@njit
	def _get_SIR(people, regions):
		# returns the fraction of susceptible (S), Infected-unknown(I_), Infected-known (I), Removed (R) values
		# additionally sends the x,y coordinates of bar plot used in animation

		region_id, alive, infection = people[:, 0], people[:, 1], people[:, 2]
		r_region_id, r_xmax, r_ymin, r_ymax, visible_infection = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4]

		sir = np.empty(shape=(regions.shape[0], 6))

		for r in range(regions.shape[0]):
			N, S, I_, I, R = 0.0, 0, 0, 0, 0
			for p in range(people.shape[0]):
				if region_id[p] == r_region_id[r]:
					N += 1.0
					if alive[p] == 0:
						R += 1
					elif infection[p] == 0:
						S += 1
					elif infection[p] < visible_infection[r]:
						I_ += 1
					else:
						I += 1
			height = float(r_ymax[r] - r_ymin[r])
			sir[r, :] = [r_xmax[r], r_ymin[r], S*height/N, I_*height/N, I*height/N, R*height/N]
		
		return sir

	@staticmethod
	@njit
	def travel(people, regions):

		home_region_id, region_id, x, y, alive = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
		r_region_id, r_xmin, r_xmax, r_ymin, r_ymax, r_travel_dom, r_travel_int_in, r_travel_int_out, r_step = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4], regions[:, 5], regions[:, 6], regions[:, 7], regions[:, 8]

		idx = np.arange(regions.shape[0])
		
		for i in range(people.shape[0]):
			
			# find properties of current region
			for r in range(regions.shape[0]):
				if region_id[i] == r_region_id[r]:
					break
			
			# domestic travel
			if alive[i] > 0 and r_travel_dom[r] > random():

				# find out bounds of current region and step size for domestic travel
				xm, xM, ym, yM, step = r_xmin[r], r_xmax[r], r_ymin[r], r_ymax[r], r_step[r]
				
				# travel within step size 
				x[i] = x[i] + normalvariate(0.0, 1.0) * step
				y[i] = y[i] + normalvariate(0.0, 1.0) * step

				# clip position to within bounding box
				x[i] = xm if x[i] < xm else (xM if x[i] > xM else x[i])
				y[i] = ym if y[i] < ym else (yM if y[i] > yM else y[i])
			
			# international travel
			if alive[i] > 0 and r_travel_int_out[r] > random():

				# shuffle international destinations
				shuffle(idx)
				
				# find new region to go to
				for j in range(len(idx)):

					# found new region which accepted person i
					if home_region_id[i] != r_region_id[idx[j]] and r_travel_int_in[idx[j]] > random():

						new_region_id = r_region_id[idx[j]]

						# find random position inside new region
						new_region_x = random() * (r_xmax[idx[j]] - r_xmin[idx[j]]) + r_xmin[idx[j]]
						new_region_y = random() * (r_ymax[idx[j]] - r_ymin[idx[j]]) + r_ymin[idx[j]]
						
						# update position and region id
						x[i] = new_region_x
						y[i] = new_region_y
						region_id[i] = new_region_id

		return x, y, region_id
	
	@staticmethod
	@njit
	def spread_infections(people, regions):

		x, y, alive, infection, region_id = people[:, 0], people[:, 1], people[:, 2], people[:, 3], people[:, 4]
		r_region_id, r_prob_spread, r_infection_radius = regions[:, 0], regions[:, 1], regions[:, 2]

		for i in range(people.shape[0]): # infectant
			if alive[i] == 0 or infection[i] == 0.0: # valid infectant is alive and has infection
				continue

			# get region properties - infection radius and probability of spread
			radius, prob = -1.0, -1.0
			for j in range(regions.shape[0]):
				if r_region_id[j] == region_id[i]:
					radius = r_infection_radius[j]
					prob = r_prob_spread[j]
					break
			
			for j in range(people.shape[0]): # infectee

				if alive[j] == 0 or infection[j] > 0.0: # valid infectee is alive and doesn't have infection
					continue
				
				if ((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2) <= radius ** 2 and random() <= prob:
					# infection can spread (with some probability) if uninfected people (j) are in close proximity with infected people (i)
					infection[j] = min(infection[j] + 0.01, 1.0)

		return infection
	
	@staticmethod
	@njit
	def change_severity(alive, infection):

		for i in range(alive.shape[0]):

			# for people with small signs of infection, a small change that its common flu and will heal automatically
			# TODO: parameterize this value
			# if alive[i] > 0 and infection[i] < 0.2 and random() < 0.1:
			# 	infection[i] /= 2.0
			
			if alive[i] > 0 and infection[i] > 0.0 and infection[i] < 1.0:
				infection[i] = min(infection[i] + 0.01, 1.0)
			
			if alive[i] > 0 and infection[i] == 1.0:
				alive[i] = 0
			
		
		return alive, infection
	
	@staticmethod
	@njit
	def social_distancing(people, regions):
		# apply social distancing through pretty dump repel force

		x, y, alive, region_id = people[:, 0], people[:, 1], people[:, 2], people[:, 3]
		r_region_id, r_xmin, r_xmax, r_ymin, r_ymax, r_social_dist = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3], regions[:, 4], regions[:, 5]

		K = 100.0

		# loop through all regions and apply social distancing
		for r in range(regions.shape[0]):

			n_iter = int(r_social_dist[r] * 100)
			xm, xM, ym, yM = r_xmin[r], r_xmax[r], r_ymin[r], r_ymax[r] # region's bounding box

			# keep looping multiple times based on social distancing factor to maximize distance between 2 people
			for _ in range(n_iter):

				# calculate the force exerted on person i by localites
				for i in range(people.shape[0]):
					
					# person should be alive and belong to the region `r` under consideration
					if alive[i] == 0.0 or region_id[i] != r_region_id[r]:
						continue
					
					# change in (x, y)
					delta_x, delta_y = 0.0, 0.0
					
					# loop through all other people in same region
					for j in range(people.shape[0]):

						# person `j` should be alive, in same region as that of person `i` and must not be equal to `i`
						if region_id[i] != region_id[j] or alive[j] == 0.0 or i == j:
							continue

						# calculate distance between i and j
						dist_ij = (x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2

						# calculate direction of force (for super position)
						delta_x = delta_x + ( K * ( x[i] - x[j] ) ) / ( dist_ij**2 + 0.0000001 )
						delta_y = delta_y + ( K * ( y[i] - y[j] ) ) / ( dist_ij**2 + 0.0000001 )
					
					# get new position of persion i
					x[i] = x[i] + delta_x
					y[i] = y[i] + delta_y

					# clip values within the region's bounding box
					x[i] = xm if x[i] < xm else (xM if x[i] > xM else x[i])
					y[i] = ym if y[i] < ym else (yM if y[i] > yM else y[i])
					
		return x, y