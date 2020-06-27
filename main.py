from core.plot.animate import Animate
from core.simulation.world import World

def main():
    world = World()
    animate = Animate(world.people, world.regions, world.simulate)
    animate.start()

if __name__ == '__main__':
    main()