from app import app
from flask import jsonify, request

from Modules.DBWorker.WellWorker import WellWorker
from Modules.DBWorker.DataWorker import DataWorker
from Modules.DBWorker.BaselineWorker import BaselineWorker


@app.route('/temperature/data', methods=['GET'])
def data_access():
    worker = DataWorker()

    if request.method == 'GET':
        args = request.args
        try:
            data = worker.get_last_data(
                args['well_name'],
                float(args['start_interval']),
                float(args['end_interval'])
            )
            return jsonify(data), 200
        except ValueError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 400
        except IndexError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 404
        except FileNotFoundError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 404
        except ConnectionError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 522


@app.route('/temperature/well', methods=['GET', 'POST', 'DELETE'])
def well_access():
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


@app.route('/temperature/baseline', methods=['GET', 'POST'])
def baseline_access():
    worker = BaselineWorker()

    if request.method == 'POST':
        if request.json:
            data_array = worker.read_lasio(request.json['data'], request.json['well_id'])
            worker.update(data_array)
            return 'created', 201

    if request.method == 'GET':
        try:
            args = request.args
            baseline = worker.get(
                args['well_name'],
                float(args['start_interval']),
                float(args['end_interval'])
            )
            return jsonify({'baseline': baseline}), 200
        except ValueError:
            return jsonify({'baseline': None}), 404
        except ConnectionError:
            return jsonify({'baseline': None}), 522
