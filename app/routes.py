from app import app
from flask import jsonify, request

from Modules.DBWorker.WellWorker import WellWorker
from Modules.DBWorker.DataWorker import DataWorker


@app.route('/temperature/data', methods=['GET'])
def data_access():
    worker = DataWorker()

    if request.method == 'GET':
        args = request.args
        try:
            data = worker.get_last_data(args['well_name'])
            return jsonify(data), 200
        except ValueError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 400
        except IndexError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 404
        except FileNotFoundError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 404
        except ConnectionError:
            return jsonify({'time': None, 'depth': [], 'temp': [], 'place': None}), 522


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
