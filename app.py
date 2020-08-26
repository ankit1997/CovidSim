import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from core.simulation.simulate import Simulator
from core.utils import animate_ops

fig, ax = plt.subplots()

def plot_setup():

    plt.style.use("seaborn-dark")
    for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
        plt.rcParams[param] = '#212946'
    for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
        plt.rcParams[param] = '0.9'

    fig.set_figheight(12)
    fig.set_figwidth(15)
    ax.axis('equal')
    ax.set_title('World')
    ax.grid(color='#2A3459')

    x0 = world.regions.loc[:, 'xmin']
    width = world.regions.loc[:, 'xmax'] - x0
    y0 = world.regions.loc[:, 'ymin']
    height = world.regions.loc[:, 'ymax'] - y0
    names = world.regions.loc[:, 'region_name']

    for i in range(len(world.regions)):
        ax.add_patch(Rectangle((x0[i]-5, y0[i]-5), width[i]+10, height[i]+10, fill=None, edgecolor='#FF8C00'))
        ax.text(x0[i], y0[i]-15, names[i])

N = 500

world = Simulator(N)
world.initialize_infections(5)
plot_setup()
animT0 = 0
animTn = 5
animDelta = 1

coord = world.people.loc[:, ['x', 'y']].values
color = animate_ops.get_colors(world.people.alive.values, world.people.infection.values)
scat = ax.scatter(coord[:, 0], coord[:, 1], s=5)
the_plot = st.pyplot(fig)

def animate(t, coord_t, color_t):
    scat.set_offsets(coord_t)
    scat.set_color(color_t)
    the_plot.pyplot(plt)

def simulate(i):
    world.call()

for i in range(100):
    
    simulate(i)
    coord_new = world.people.loc[:, ['x', 'y']].values
    # coord_new = np.clip(coord + np.random.normal(size=(N*6, 2)) * 10.0, 0, 100)
    color = animate_ops.get_colors(world.people.alive.values, world.people.infection.values)
    
    for t in range(animT0, animTn, animDelta):
        coord_t = animate_ops.interpolate2D(coord_new, coord, t, animT0, animTn)
        animate(t, coord_t, color)
    
    coord = coord_new