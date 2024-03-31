#!/usr/bin/python3
"""
create a new view for State objects that handles all default RESTful API
actions
"""
from models import storage
from api.v1.views import app_views
from flask import make_response, jsonify, abort, request, g
from models.state import State


@app_views.before_request
def new_storage_values():
    """Called before any request is made to refresh storage"""
    g.state_dict = storage.all(State)


@app_views.route('/states', methods=['GET', 'POST'], strict_slashes=False)
@app_views.route('/states/<state_id>', methods=['GET', 'DELETE', 'PUT'])
def all_states(state_id=None):
    """list of all or given state_id State Objects"""
    state_instances = [val.to_dict() for val in g.state_dict.values()]
    if not state_id:
        if request.method == 'GET':
            return make_response(jsonify(state_instances), 200)

        elif request.method == 'POST':
            if not request.is_json or not request.get_json().get('name', None):
                abort(400)
            data = request.get_json()
            new_instance = State(**data)
            new_instance.save()
            data = storage.get("State", new_instance.id).to_dict()
            return make_response(jsonify(data), 201)

    obj_inst = storage.get('State', state_id)
    if not obj_inst:
        abort(404)
    if request.method == 'GET':
        return make_response(jsonify(obj_inst.to_dict()), 200)

    elif request.method == 'DELETE':
        storage.delete(obj_inst)
        storage.save()
        return jsonify({}), 200

    elif request.method == 'PUT':
        if not request.is_json:
            abort(400)
        data = request.get_json()
        for key in data.keys():
            if key not in ['id', 'created_at', 'update_id']:
                setattr(obj_inst, key, data[key])
        obj_inst.save()
        return obj_inst.to_dict()