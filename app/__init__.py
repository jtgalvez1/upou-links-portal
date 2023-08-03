# Import Statements
from flask import Flask, render_template, session, redirect, make_response, request, url_for, send_from_directory
from flask_session import Session

from google.auth.transport.requests import Request

# Initializing application
app = Flask(__name__)
app.config.from_pyfile('configs.py')
Session(app)

print("Server listening on http://localhost:5000")

# Import functions and endpoints from API
from app.api.link.router import link
from app.api.user.router import user
from app.api.admin.router import admin
from app.api.announcements.router import announcements
app.register_blueprint(link, url_prefix="/api/v1/link")
app.register_blueprint(user, url_prefix="/api/v1/user")
app.register_blueprint(admin, url_prefix="/api/v1/admin")
app.register_blueprint(announcements, url_prefix="/api/v1/announcements")

from app.api.link.controller import *
from app.api.user.controller import *
from app.api.admin.controller import *
from app.api.announcements.controller import *
from .oauth import verify_token

# Checks user before every fetch request
@app.before_request
def check_user():
    if request.path.startswith('/static') or request.path.startswith('/favicon') or request.path == '/logout':
        return
    print(request.method + ' ' + request.path)

    if request.path.startswith('/admin') and session.get('user', { 'user_type' : 'guest' })['user_type'] != 'admin':
        return redirect('/')

    if request.path.startswith('/announcements') and session.get('user', { 'user_type' : 'guest' })['user_type'] != 'admin':
        return redirect('/')

    if session and session.get('user'):
        users = list_users('email', session['user']['email'])
        if len(users) == 1:
            user = users[0]
            user['bookmarks'] = get_user_bookmarks(user['id'])
            session['user'] = { **user, 'name': user.get('given_name') + ' ' + user.get('family_name')}
        else:
            session['user'] = { 'user_type' : 'guest', 'email' : 'null' }
    return


# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('error/404.html', categories_links = {}), 404


# pages routes

# Main route that fetches all necessary data
@app.route('/', methods=['GET'])
def index_page():
    categories_links = {}
    bookmark_links = []
    recents_links = []
    trending_links = list_trending_links(session.get('user', {'user_type':'guest'})['user_type'])
    if session and session.get('user'):
        bookmark_links = list_bookmark_links(session['user']['id'])
        recents_links = list_recently_visited_links(session['user']['id'])
    
    if len(bookmark_links) > 0:
        categories_links['Bookmarks'] = bookmark_links
    
    if len(recents_links) > 0:
        categories_links['Recently Visited'] = recents_links

    if len(trending_links) > 0:
        categories_links['Trending'] = trending_links


    categories = list_categories(session.get('user', {'user_type': 'guest'})['user_type'])
    for category in categories:
        category_links = links_by_category(category, session.get('user', {'user_type': 'guest'})['user_type'])

        if len(category_links) > 0:
            categories_links[category['name']] = category_links

    res = make_response(
            render_template(
                'index.html',
                categories_links = categories_links,
                user=session.get('user', None), 
                category_list = list_all_categories(), 
                privacy_settings = list_user_types(),
                announcements = get_valid_announcements()
        ))
    res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
    res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
    return res


# Route for searching links
@app.route('/search', methods=['GET'])
def search_page():
    term = request.args.get('term', 'asia')

    categories = list_categories(session.get('user', {'user_type': 'guest'})['user_type'])
    categories_links = {}

    for category in categories:
        result = []
        category_links = links_by_category(category, session.get('user', {'user_type': 'guest'})['user_type'])

        for link in category_links:
            if term in link['url'] or term in link['title'] or term in link['description']:
                result.append(link)

        if len(category_links) > 0:
            categories_links[category['name']] = result

    res = make_response(render_template('index.html',categories_links = categories_links,user=session.get('user', None), category_list = list_all_categories(), privacy_settings = list_user_types(), announcements = get_valid_announcements()))
    res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
    res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
    return res

# User Management Route
@app.route('/users', methods=['GET'])
@app.route('/admin', methods=['GET'])
def user_management_page():
    types = retrieve_user_types()

    usertypes = {}
    users = list_user_data()

    for utype in types:
        usertypes[utype[1]] = []
        for user in users:
            if user["user_type"] == utype[0]:
                usertypes[utype[1]].append(user)

    res = make_response(render_template('users.html', categories_links=usertypes, user=session.get('user', None), usertypes = usertypes, lentypes=len(usertypes)))
    res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
    res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
    return res

# Authentication Route
@app.route('/callback', methods=['POST', 'GET'])
def callback():
    credential = request.form.get('credential')
    user_google_data = verify_token(credential)
    if user_google_data:
        if len(list_users('email', user_google_data['email'])) == 1:
            user_google_data = { **user_google_data, 'user_type' : get_user_value(user_google_data['email'], 'user_type')}
        user = upsert_user(user_google_data)
        session['user'] = { **user, "name" : user.get('given_name') + " " + user.get('family_name', '') }

    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

# PWA routes
@app.route('/offline.html', methods=['GET'])
def offline():
    return app.send_static_file('offline.html')


@app.route('/service-worker.js', methods=['GET'])
def sw():
    return app.send_static_file('service-worker.js')

# @app.route('/app.js', methods=['GET'])
# def pwa():
#     return app.send_static_file('/pwa/app.js')

# announcement routes

# Route for announcement management
@app.route('/announcements', methods=['GET'])
def ap():

    res = make_response(render_template('announcements.html', categories_links={}, user=session.get('user', None), announcements=get_announcements()))
    res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
    res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
    return res