import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

plt.style.use("seaborn-dark")
for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
	plt.rcParams[param] = '#212946'
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
	plt.rcParams[param] = '0.9'

class Animate:

	def __init__(self, people, regions, simulate):
		self.people = people
		self.regions = regions
		self.simulate = simulate

	def start(self):

		fig, ax = plt.subplots(figsize=(10, 10))
		ax.set(
			xlim=(self.regions.xmin.min()-50, self.regions.xmax.max()+50), 
			ylim=(self.regions.ymin.min()-50, self.regions.ymax.max()+50)
		)
		self.old_coordinates = self.people.loc[:, ['x', 'y']].values
		scat = ax.scatter(self.people.x, self.people.y, s=0.5)
		ax.axis('equal')
		ax.axis('off')
		ax.set_title('World')
		ax.grid(color='#2A3459')

		for i in range(len(self.regions)):
			x0 = self.regions.loc[i, 'xmin'].item()
			y0 = self.regions.loc[i, 'ymin'].item()
			width = self.regions.loc[i, 'xmax'].item() - x0
			height = self.regions.loc[i, 'ymax'].item() - y0
			ax.add_patch(Rectangle((x0, y0), width, height, fill=None, edgecolor='#08F7FE'))

			ax.text(x0, y0-5, self.regions.loc[i, 'region_name'])

		self.animT0	= 0
		self.animTn = 10
		self.animDelta = 1

		ani = animation.FuncAnimation(fig, self.animate, interval=1, fargs=(scat,), blit=True, 
									frames=np.arange(self.animT0, self.animTn, self.animDelta))
		plt.draw()
		plt.show()
	
	def animate(self, t, scat):

		# simulate
		if t == self.animT0:
			self.people, self.regions = self.simulate()

		# set new coordinates
		new_coordinates = self.people.loc[:, ['x', 'y']].values
		coordinates = ((t - self.animT0) / (self.animTn - self.animT0)) * new_coordinates + ((self.animTn - t) / (self.animTn - self.animT0)) * self.old_coordinates
		scat.set_offsets(coordinates)

		if t == (self.animTn - self.animDelta):
			self.old_coordinates = new_coordinates

		# set point color based on if person has infection or not
		inf = self.people.loc[:, 'infection'] > 0.0 # infected people
		
		color = np.array([[1.0, 0.5, 0]] * len(self.people)) #FF8C00
		# color = np.array([[1.0, 0.5, 1.0]] * len(self.people)) #FF8C00
		color[inf] = [1.0, 0.0, 0.0] # infected points are red
		scat.set_color(color)

		return scat,