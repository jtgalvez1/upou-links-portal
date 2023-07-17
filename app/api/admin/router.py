from flask import Blueprint, jsonify, request

link = Blueprint(name='link', import_name=__name__)

from .controller import *

@link.route('/getUserData', methods = ["GET"])
def get_users():
    users = list_users()
    return jsonify({
        'status'      : 200,
        'message'     : 'Succesfully retrieved links',
        'users'       : users
    })

@link.route('/changeUserType', methods = ["POST"])
def change_type():
    data = request.form.to_dict()
    email = data['email']
    userType = data['userType']
    change_user_type(email, userType)
