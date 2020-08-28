import json
from flask import Flask, jsonify, request
from pandas import DataFrame

from core.simulation.simulate import Simulator

app = Flask(__name__)

num_people = 400
initial_infections = 10

world = Simulator(num_people)
world.initialize_infections(initial_infections)

APIs = [
    {
        'Endpoint': '/',
        'Description': 'Home Page'
    },
    {
        'Endpoint': '/get_world',
        'Description': 'Get the new state of the world'
    },
]

@app.route('/')
def index():
    return jsonify(APIs)

@app.route('/get_regions')
def get_regions():
    return world.regions.to_dict()

@app.route('/reset')
def reset():
    global world
    world = Simulator(num_people)
    world.initialize_infections(initial_infections)
    return {}

@app.route('/get_world', methods=['GET', 'POST'])
def get_world():
    if request.method == 'POST':
        req_data = json.loads(request.data)
        world.regions = DataFrame.from_dict(req_data)
    world.call()
    return jsonify(world.people.loc[:, ['x', 'y', 'alive', 'infection']].values.tolist())

if __name__ == '__main__':
    app.run(debug=True)