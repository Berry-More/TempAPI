from app import app
from flask import jsonify, request

from Modules.DBWorker.db import dataBase
from Modules.DBWorker.WellWorker import WellWorker

"""
Use 'request' package for work with API.

Example: 

params = {
    'time_start': start_time, 
    'time_end': end_time, 
    'place': 'Kluchi'
}

response = requests.get(
    'http://127.0.0.1:5000/temperature/times', 
    params=params
)
"""


@app.route('/temperature/data', methods=['GET', 'POST'])
def data_access():

    if request.method == 'GET':
        args = request.args
        try:
            data = dataBase.get_data(args['time_start'], args['time_end'], args['place'],
                                     args['depth_min'], args['depth_max'])
            return jsonify(data), 200
        except ValueError:
            return jsonify({'time': [], 'depth': [], 'temp': []}), 400
        except FileNotFoundError:
            return jsonify({'time': [], 'depth': [], 'temp': []}), 404
        except ConnectionError:
            return jsonify({'time': [], 'depth': [], 'temp': []}), 522

    if request.method == 'POST':
        if request.json:
            new_data = {
                'time': request.json['time'],
                'depth': request.json['depth'],
                'temp': request.json['temp'],
                'place': request.json['place']
            }
            dataBase.post_data(new_data)
            return 'created', 201


@app.route('/temperature/places', methods=['GET'])
def places_access():
    try:
        places = dataBase.get_places()
        return jsonify({'places': places}), 200
    except ValueError:
        return jsonify({'places': None}), 404
    except ConnectionError:
        return jsonify({'places': None}), 522


@app.route('/temperature/wells', methods=['GET', 'POST', 'DELETE'])
def wells_access():
    worker = WellWorker()

    if request.method == 'GET':
        try:
            wells = worker.get_wells()
            return jsonify({'wells': wells}), 200
        except ValueError:
            return jsonify({'wells': None}), 404
        except ConnectionError:
            return jsonify({'wells': None}), 522

    if request.method == 'POST':
        if request.json:
            new_well = WellWorker.request_to_well(request)
            WellWorker.post_well(new_well)
            return 'created', 201

    if request.method == 'DELETE':
        args = request.args
        try:
            well_id = int(args['well_id'])
            WellWorker.delete_well(well_id)
            return 'deleted', 200
        except ConnectionError:
            return 'has not deleted', 522


@app.route('/temperature/depth-range', methods=['GET'])
def depth_access():
    try:
        args = request.args
        min_depth = dataBase.get_min_depth(args['time_start'], args['time_end'], args['place'])
        max_depth = dataBase.get_max_depth(args['time_start'], args['time_end'], args['place'])
        return jsonify({'depth-range': [min_depth, max_depth]}), 200
    except ConnectionError:
        return jsonify({'depth-range': None}), 522
