import sys
import time
from core.plot.animate import Animate
from core.simulation.world import World

def main(args):
    world = World()
    world.initialize_infections(5)

    if '-profile' in args:
        t1 = time.time()
        for _ in range(100):
            world.simulate()
        t2 = time.time()
        print('Average time taken per simulation:', (t2-t1)/100.0, "seconds") # 0.2943538737297058 seconds
    else:
        animate = Animate(world)
        animate.start()

if __name__ == '__main__':
    main(sys.argv)