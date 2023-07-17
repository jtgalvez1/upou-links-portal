from flask import Blueprint, jsonify, request

link = Blueprint(name='link', import_name=__name__)

from .controller import *

@link.route('/', methods=['GET'])
def get_links():
  links = list_links()

  return jsonify({
    'status'      : 200,
    'message'     : 'Succesfully retrieved links',
    'links'       : links
  })

@link.route('/', methods=['POST'])
def submit_link():
  form = request.form.to_dict()
  link = {
    'url'         : form['url'],
    'title'       : form['title'],
    'privacy'     : form['privacy'],
    'category'    : form.get('category'),
    'new_category': form.get('new_category'),
    'description' : form.get('description')
  }

  new_link = upsert_link(link)

  return jsonify({
    'status'      : 200,
    'message'     : 'Succesfully updated link for ' + new_link['url'],
    'link'        : new_link
  })

@link.route('/<column>/<value>', methods=['GET'])
def get_links_w_filter(column,value):
  try:
    privacy = request.args.get('priv')
  except:
    privacy = 'open'
  links = list_links(privacy,column,value)

  return jsonify({
    'status'      : 200,
    'message'     : 'Succesfully retrieved links',
    'links'       : links
  })

@link.route('/categories', methods=['GET'])
def get_categories():
  try:
    privacy = request.args.get('priv')
  except:
    privacy = 'open'

  categories = list_categories(privacy)

  return jsonify({
    'status'      : 200,
    'categories'  : categories
  })