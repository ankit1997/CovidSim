import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

from core.utils import animate_ops

from threading import Thread

plt.style.use("seaborn-dark")
for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
	plt.rcParams[param] = '#212946'
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
	plt.rcParams[param] = '0.9'

class Animate:

	def __init__(self, world, anim_func):
		self.world = world
		self.anim_func = anim_func

		# interpolation parameters
		self.animT0	= 0
		self.animTn = 10
		self.animDelta = 1

	def start(self):

		self.fig, self.ax = plt.subplots()
		self.ax.set(
			xlim=(self.world.regions.xmin.min()-50, self.world.regions.xmax.max()+50), 
			ylim=(self.world.regions.ymin.min()-50, self.world.regions.ymax.max()+50)
		)
		
		# coordinates
		self.new_coordinates = self.world.people.loc[:, ['x', 'y']].values
		self.old_coordinates = self.new_coordinates.copy()

		# colors
		self.new_color = animate_ops.get_colors(self.world.people.alive.values, self.world.people.infection.values)
		self.old_color = self.new_color.copy()

		scat = self.ax.scatter(self.world.people.x, self.world.people.y, s=0.5)
		self.ax.axis('off')
		self.ax.set_title('World')
		self.ax.grid(color='#2A3459')

		# set boundary for each region and name of the region
		x0 = self.world.regions.loc[:, 'xmin']
		width = self.world.regions.loc[:, 'xmax'] - x0
		y0 = self.world.regions.loc[:, 'ymin']
		height = self.world.regions.loc[:, 'ymax'] - y0
		# names = self.world.regions.loc[:, 'region_name']

		for i in range(len(self.world.regions)):
			self.ax.add_patch(Rectangle((x0[i]-2, y0[i]-2), width[i]+2, height[i]+2, fill=None, edgecolor='#FF8C00'))
			# self.ax.text(x0[i], y0[i]-10, names[i])

		ani = animation.FuncAnimation(self.fig, self.animate, interval=10, fargs=(scat,), blit=True, 
									frames=np.arange(self.animT0, self.animTn, self.animDelta))
		
		figManager = plt.get_current_fig_manager()
		figManager.window.showMaximized()

		plt.draw()
		plt.show()
	
	def animate(self, t, scat):

		# first frame of day
		if t == self.animT0:
			
			self.anim_func() # TODO: use parallel execution via Thread API

			# set new coordinates
			self.new_coordinates = self.world.people.loc[:, ['x', 'y']].values

			# set new color
			self.new_color = animate_ops.get_colors(self.world.people.alive.values, self.world.people.infection.values)

			# simulate in parallel (so that interpolation time is not wasted)
			# self.thread = Thread(target=self.world.simulate)
			# self.thread.start()

		# for any point in time t, interpolate between old and new coordinates and color
		coordinates = animate_ops.interpolate2D(self.new_coordinates, self.old_coordinates, t, self.animT0, self.animTn)
		# color = animate_ops.interpolate2D(self.new_color, self.old_color, t, self.animT0, self.animTn) # TODO: remove : unnecessary

		scat.set_offsets(coordinates)
		scat.set_color(self.new_color)

		# last frame of day
		if t == (self.animTn - self.animDelta):
			self.old_coordinates = self.new_coordinates
			self.old_color = self.new_color

			# wait for last simulation to end
			# self.thread.join() # TODO: use parallel execution

		return scat,
		