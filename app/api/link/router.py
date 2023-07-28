from flask import Blueprint, jsonify, request
from time import time

link = Blueprint(name='link', import_name=__name__)

from .controller import *

# @link.route('/', methods=['GET'])
# def get_links():
#   privacy = request.args.get('priv', 'guest')
#   links = list_links(privacy)

#   return jsonify({
#     'status'      : 200,
#     'message'     : 'Succesfully retrieved links',
#     'links'       : links
#   })

@link.route('/', methods=['POST'])
def submit_link():
  form = request.form.to_dict()
  image = request.files.to_dict().get('image', '')

  # process image file before adding link
  file_name = ''
  if image != '':
    # file_name = (f"{str(int(time()))}_{image.filename}").replace(' ','_').replace('-','_')
    file_name = (f"{str(int(time()))}_{image.filename}")
    image_path = app.config['IMAGES_PATH'] + file_name
    image.save(image_path)

  link = {
    'url'         : form['url'],
    'title'       : form['title'],
    'privacy'     : form['privacy'],
    'category'    : form.get('category'),
    'new_category': form.get('new_category'),
    'description' : form.get('description'),
    'image'       : file_name
  }

  new_link = upsert_link(link)

  return jsonify({
    'status'      : 200,
    'message'     : 'Succesfully updated link for ' + new_link['url'],
    'link'        : new_link
  })

# @link.route('/<column>/<value>', methods=['GET'])
# def get_links_w_filter(column,value):
#   try:
#     privacy = request.args.get('priv')
#   except:
#     privacy = 'guest'
#   links = list_links(privacy,column,value)

#   return jsonify({
#     'status'      : 200,
#     'message'     : 'Succesfully retrieved links',
#     'links'       : links
#   })

# @link.route('/categories', methods=['GET'])
# def get_categories():
#   try:
#     privacy = request.args.get('priv')
#   except:
#     privacy = 'guest'

#   categories = list_categories(privacy)

#   return jsonify({
#     'status'      : 200,
#     'categories'  : categories
#   })

@link.route('/<link_id>', methods=['DELETE'])
def delete_link(link_id):
    remove_link_from_db(link_id)

    return jsonify({
        'status'      : 200,
        'message'     : 'Successfully deleted link.'
    })