import json
from flask import Flask, jsonify, request
from pandas import DataFrame
from threading import Lock

from core.simulation.simulate import Simulator

app = Flask(__name__)
lock = Lock()

num_people = 100
initial_infections = 10

world = Simulator(num_people)
world.initialize_infections(initial_infections)

@app.route('/get_regions')
def get_regions():
    return world.regions.to_dict()

@app.route('/reset')
def reset():
    global world
    with lock:
        world = Simulator(num_people)
        world.initialize_infections(initial_infections)
    return {}

@app.route('/add_person_to_region', methods=['GET', 'POST'])
def add_person_to_region():
    if request.method == 'POST':
        with lock:
            req_data = json.loads(request.data)
            world.add_people_to_region(req_data['region_id'], req_data['num_people'])
    return {}

@app.route('/get_world', methods=['GET', 'POST'])
def get_world():
    if request.method == 'POST':
        req_data = json.loads(request.data)
        world.regions = DataFrame.from_dict(req_data)
    with lock:
        world.call()
    return jsonify({'data': world.people.loc[:, ['x', 'y', 'alive', 'infection']].values.tolist(), 'time': round(world.T)})

if __name__ == '__main__':
    app.run(debug=True)