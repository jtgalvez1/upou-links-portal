from flask import Blueprint, jsonify, request
from time import time

announcements = Blueprint(name='announcements', import_name=__name__)

from .controller import *

# Route for getting announcements
@announcements.route('/', methods=["POST"])
def add_announce():
    data = request.form.to_dict()
    image = request.files.to_dict().get('image', '')

    print(data)

    file_name = ''
    if image != '':
        file_name = (f"{str(int(time()))}_{image.filename}")
        image_path = app.config['IMAGES_PATH'] + file_name
        image.save(image_path)

    announcement = {
        'name' : data['name'],
        'description' : data['desc'],
        'datetime' : data['enddate'],
        'link'        : data['link'],
        'image' : file_name
    }

    newAnnouncement = add_announcement(announcement)
    return jsonify({
    'status'      : 200,
    'message'     : "Succesfully added announcement!",
    })

# Route to change visibility
@announcements.route('/changeVisibility', methods = ["POST"])
def change_vis():
    data = request.form.to_dict()
    name = data['name']
    visibility = 1 if data['visibility']=="true" else 0
    change_visibility(name, visibility)

    return jsonify({
        'status'      : 200,
        'message'     : 'Succesfully changed visibililty',
    })

# Route to change end date
@announcements.route('/changeEndDate', methods = ["POST"])
def change_end():
    data = request.form.to_dict()
    name = data['name']
    enddate = data['date']
    change_enddate(name, enddate)

    return jsonify({
        'status'      : 200,
        'message'     : 'Succesfully changed enddate',
    })

# Route to change any column in table
@announcements.route('/<announcement_id>/<column>/<value>', methods = ['PUT'])
def change_announcement_column(announcement_id, column, value):
    image = request.files.to_dict().get('image', '')

    columns = {
        'id'        : "id",
        'name'      : "name",
        'desc'      : "description",
        'enddate'   : "ends_at",
        'image'     : "image",
        'visibility': "is_visible"
    }

    file_name = ''
    if column == 'image':
        file_name = (f"{str(int(time()))}_{image.filename}")
        image_path = app.config['IMAGES_PATH'] + file_name
        image.save(image_path)
        value = file_name

    change_announcement_column_value(announcement_id,columns[column],value)

    return jsonify({
        'status'       : 200,
        'message'      : 'Successfully changed ' + columns[column]
    })

# Route to delete announcement
@announcements.route('/<announcement_id>', methods=['DELETE'])
def delete_announcement_endpoint(announcement_id):
    print(announcement_id)
    delete_announcement(announcement_id)

    return jsonify({
        'status'        : 200,
        'message'       : 'Succesfully deleted announcement.'
    })