import numpy as np
from core.utils import ops
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

plt.style.use("seaborn-dark")
for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
	plt.rcParams[param] = '#212946'
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
	plt.rcParams[param] = '0.9'

class Animate:

	def __init__(self, world):
		self.world = world

		# interpolation parameters
		self.animT0	= 0
		self.animTn = 8
		self.animDelta = 1

	def start(self):

		self.fig, self.ax = plt.subplots(figsize=(10, 10))
		self.ax.set(
			xlim=(self.world.regions.xmin.min()-50, self.world.regions.xmax.max()+50), 
			ylim=(self.world.regions.ymin.min()-50, self.world.regions.ymax.max()+50)
		)
		self.old_coordinates = self.world.people.loc[:, ['x', 'y']].values
		scat = self.ax.scatter(self.world.people.x, self.world.people.y, s=2)
		self.ax.axis('equal')
		self.ax.axis('off')
		self.ax.set_title('World')
		self.ax.grid(color='#2A3459')

		# set boundary for each region and name of the region
		x0 = self.world.regions.loc[:, 'xmin']
		width = self.world.regions.loc[:, 'xmax'] - x0
		y0 = self.world.regions.loc[:, 'ymin']
		height = self.world.regions.loc[:, 'ymax'] - y0
		names = self.world.regions.loc[:, 'region_name']

		for i in range(len(self.world.regions)):
			self.ax.add_patch(Rectangle((x0[i], y0[i]), width[i], height[i], fill=None, edgecolor='#FF8C00'))
			self.ax.text(x0[i], y0[i]-5, names[i])

		ani = animation.FuncAnimation(self.fig, self.animate, interval=10, fargs=(scat,), blit=True, 
									frames=np.arange(self.animT0, self.animTn, self.animDelta))
		plt.draw()
		plt.show()
	
	def animate(self, t, scat):

		# simulate
		if t == self.animT0:
			self.world.simulate()

		# set new coordinates
		new_coordinates = self.world.people.loc[:, ['x', 'y']].values

		coordinates = ops.interpolate2D(new_coordinates, self.old_coordinates, t, self.animT0, self.animTn)
		scat.set_offsets(coordinates)

		if t == (self.animTn - self.animDelta):
			self.old_coordinates = new_coordinates

		# set point color based on if person has infection or not
		inf = self.world.people.loc[:, 'infection'] > 0.0 # infected people

		color = np.array([[0.03, 0.96, 0.99]] * len(self.world.people)) #08F7FE
		color[inf] = [1.0, 0.0, 0.0] # infected points are red
		scat.set_color(color)

		return scat,
		