from flask import Blueprint, jsonify, request, session

user = Blueprint(name='user', import_name=__name__)

from .controller import *
from app.oauth import verify_token

# Route to get users
@user.route('/', methods=['GET'])
def get_users():
   users = list_users()

   return jsonify({
      'status'        : 200,
      'users'         : users,
   })

# @user.route('/user_types', methods=['GET'])
# def get_user_types():
#   user_types = list_user_types()

#   return jsonify({
#     'status'      : 200,
#     'message'     : 'Succesfully retrieved user types.',
#     'user_types'  : user_types
#   })

# @user.route('/<email>', methods=['GET'])
# def get_user_by_email(email):
#   user = list_users('email', email)[0]

#   return jsonify({
#     'status'    : 200,
#     'user'      : user
#   })

# Authentication routes
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

# Function to bookmark a link
@user.route('/<userid>/bookmark/link/<link_id>', methods=['PUT'])
def bookmark(userid, link_id):
   action = bookmark_link(userid, link_id)
   try:
      log_activity(userid, 'BOOKMARK', link_id)
   except ValueError as ve:
      print(ve)
   return jsonify({
      'status'      : 200,
      'message'     : 'Successfully updated bookmark',
      'action'      : action
   })

# Function to add a new bookmark
@user.route('/addType', methods=["POST"])
def addType():
   form = request.form.to_dict()
   newname = form['usertypename']
   action = add_user_type(newname)
   return jsonify({
      'status'      : 200,
      'message'     : 'Successfully updated bookmark',
      'action'      : action
   })

# Function to log activity
@user.route('/<userid>/visit/link/<link_id>', methods=['GET'])
def visit(userid, link_id):
   log_activity(userid, 'VISIT', link_id)
   return jsonify({ 'status' : 200 })

# Function to add link
@user.route('/<userid>/add/link/<link_id>', methods=['GET'])
def add(userid, link_id):
   log_activity(userid, 'ADD', link_id)
   return jsonify({ 'status' : 200 })

# Function to edit link
@user.route('/<userid>/edit/link/<link_id>', methods=['GET'])
def edit(userid, link_id):
   log_activity(userid, 'EDIT', link_id)
   return jsonify({ 'status' : 200 })

# Function to remove link
@user.route('/<userid>/remove/link/<link_id>', methods=['GET'])
def remove(userid, link_id):
   log_activity(userid, 'REMOVE', link_id)
   return jsonify({ 'status' : 200 })

@user.route('/<email>', methods=['DELETE'])
def deluser(email):
   delete_user(email)
   return jsonify({
        'status'      : 200,
        'message'     : 'Successfully deleted user.'
    })