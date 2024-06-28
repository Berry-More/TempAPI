from app import app
from flask import jsonify, request

from Modules.DBWorker.db import dataBase
from Modules.DBWorker.WellWorker import WellWorker


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
