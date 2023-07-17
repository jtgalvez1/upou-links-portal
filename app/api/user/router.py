from flask import Blueprint, jsonify, request

user = Blueprint(name='user', import_name=__name__)

from .controller import *

@user.route('/user_types', methods=['GET'])
def get_user_types():
  user_types = list_user_types()

  return jsonify({
    'status'      : 200,
    'message'     : 'Succesfully retrieved user types.',
    'user_types'  : user_types
  })

@user.route('/<email>', methods=['GET'])
def get_user(email):
  user = list_users('email', email)[0]

  return jsonify({
    'status'    : 200,
    'user'      : user
  })