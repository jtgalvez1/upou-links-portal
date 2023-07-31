from flask import Blueprint, jsonify, request

admin = Blueprint(name='admin', import_name=__name__)

from .controller import *

# Route to get user data
@admin.route('/getUserData', methods = ["GET"])
def get_users():
    users = list_user_data()
    return jsonify({
        'status'      : 200,
        'message'     : 'Succesfully retrieved users',
        'users'       : users
    })

# Route to change type of user
@admin.route('/changeUserType', methods = ["POST"])
def change_type():
    data = request.form.to_dict()
    email = data['email']
    userType = data['userType']
    change_user_type(email, userType)

    return jsonify({
        'status'      : 200,
        'message'     : 'Succesfully changed usertype',
    })