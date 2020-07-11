import sys
import time
from flask import Flask, request
from threading import Thread

from core.plot.animate import Animate
from core.simulation.simulate import Simulator

try:
    num_people = int(sys.argv[1])
except Exception as exp:
    print('Parameter 1 must be a number')
    exit()

app = Flask(__name__)
world = Simulator(num_people)
anim_started = False

def profile():
    t1 = time.time()
    for _ in range(100):
        world.call()
    t2 = time.time()
    print('Average time taken per simulation:', (t2-t1)/100.0, "seconds") # 0.24 seconds

def main():

    Thread(target=app.run).start()

    world.initialize_infections(5)
    animate = Animate(world, world.call)
    animate.start()

@app.route('/')
def start_simulation():
    return "Simulation has already begun"

@app.route('/change_policy')
def change_policy():
    # change policy of region
    # request parameters : `region_id`, `key`, `value`
    # example: http://127.0.0.1:5000/change_policy?region_id=5&key=social_distancing&value=0.7

    region_id = int(request.args['region_id'])
    key = request.args['key']
    value = float(request.args['value'])
    world.set_policy(region_id, key, value)

    return "Policy updated successfully"

if __name__ == '__main__':
    if '-profile' in sys.argv:
        profile()
    else:
        main()