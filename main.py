import sys
import time
from core.plot.animate import Animate
# from core.simulation.world import World
from core.simulation.simulate import Simulator

def main(args):

    world = Simulator(int(args[1]))
    world.initialize_infections(5)

    if '-profile' in args:
        t1 = time.time()
        for _ in range(100):
            world.call()
        t2 = time.time()
        print('Average time taken per simulation:', (t2-t1)/100.0, "seconds") # 0.24 seconds
    else:
        animate = Animate(world, world.call)
        animate.start()

if __name__ == '__main__':
    main(sys.argv)