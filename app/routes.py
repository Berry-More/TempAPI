from app import app

from db import dataBase
from flask import redirect, url_for, jsonify, request

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
        print(args['name'])
        return args

    if request.method == 'POST':
        if request.json:
            new_data = {
                'time': request.json['time'],
                'depth': request.json['depth'],
                'temp': request.json['temp'],
                'place': request.json['places']
            }
            dataBase.post_data(new_data)
            return 'created', 201


@app.route('/temperature/places', methods=['GET'])
def places_access():
    try:
        places = dataBase.get_places()
        return jsonify({'places': places}), 200
    except ValueError:
        return jsonify({'places': None}), 200
    except ConnectionError:
        return jsonify({'places': None}), 522


@app.route('/temperature/depth-range', methods=['GET'])
def depth_access():
    try:
        args = request.args
        min_depth = dataBase.get_min_depth(args['time_start'], args['time_end'], args['place'])
        max_depth = dataBase.get_max_depth(args['time_start'], args['time_end'], args['place'])
        return jsonify({'depth-range': [min_depth, max_depth]}), 200
    except ConnectionError:
        return jsonify({'depth-range': None}), 522


# test route
# @app.route('/temperature/times', methods=['GET'])
# def times_access():
#     args = request.args
#     times = dataBase.get_times(args['time_start'], args['time_end'], args['place'])
#     return jsonify({'times': times}), 200
