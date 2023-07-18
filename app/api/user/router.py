from flask import Blueprint, jsonify, request, session

user = Blueprint(name='user', import_name=__name__)

from .controller import *
from app.oauth import verify_token

@user.route('/', methods=['GET'])
def get_users():
   users = list_users()

   return jsonify({
      'status'        : 200,
      'users'         : users,
   })

@user.route('/user_types', methods=['GET'])
def get_user_types():
  user_types = list_user_types()

  return jsonify({
    'status'      : 200,
    'message'     : 'Succesfully retrieved user types.',
    'user_types'  : user_types
  })

@user.route('/<email>', methods=['GET'])
def get_user_by_email(email):
  user = list_users('email', email)[0]

  return jsonify({
    'status'    : 200,
    'user'      : user
  })

@user.route('/signin', methods=['POST'])
def sigin():
    credential = request.form.get('credential')
    user_google_data = verify_token(credential)
    if user_google_data:
        if len(list_users('email', user_google_data['email'])) == 1:
            user_google_data = { **user_google_data, 'user_type' : get_user_value(user_google_data['email'], 'user_type')}
        user = upsert_user(user_google_data)
        session['user'] = { **user, "name" : user.get('given_name') + " " + user.get('family_name') }

    return jsonify({
       'status'     : 200,
       'message'    : 'Succesful Login',
       'user'       : user
    })

@user.route('/<userid>/bookmark/<link_id>', methods=['PUT'])
def bookmark(userid, link_id):
   action = bookmark_link(userid, link_id)
   return jsonify({
      'status'      : 200,
      'message'     : 'Successfully updated bookmark',
      'action'      : action
   })