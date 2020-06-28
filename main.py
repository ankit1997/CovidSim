from core.plot.animate import Animate
from core.simulation.world import World

def main():
    world = World()
    world.people.loc[[1, 2, 3, 4, 5, 6, 7], 'infection'] = 0.5
    animate = Animate(world)
    animate.start()

if __name__ == '__main__':
    main()