from flask import Blueprint, jsonify, request
from time import time

announcements = Blueprint(name='announcements', import_name=__name__)

from .controller import *

@announcements.route('/addAnnouncement', methods=["POST"])
def add_announce():
    data = request.form.to_dict()
    image = request.files.to_dict().get('image', '')

    file_name = ''
    if image != '':
        file_name = (f"{str(int(time()))}_{image.filename}")
        image_path = app.config['IMAGES_PATH'] + file_name
        image.save(image_path)

    announcement = {
        'name' : data['name'],
        'description' : data['desc'],
        'datetime' : data['enddate'],
        'image' : file_name
    }

    newAnnouncement = add_announcement(announcement)
    return jsonify({
    'status'      : 200,
    'message'     : "Succesfully added announcement!",
    })

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