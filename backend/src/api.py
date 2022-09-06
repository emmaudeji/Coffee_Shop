import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask import Flask, session, redirect

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

AUTH0_DOMAIN = 'dev-zuydypff.us.auth0.com'

app = Flask(__name__)
setup_db(app)
CORS(app)
cors = CORS(app, resource={r"/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,PUT,DELETE,OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
'''

db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    print(all_drinks)

    if len(all_drinks) == 0:
        abort(404)

    drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    try:
        drinks = Drink.query.all()
        if drinks:
            print(drinks)
            data = [drink.short() for drink in drinks]
        else:
            data = []
    except Exception as e:
        print(e)
        abort(500)
    return jsonify({"success": True, "drinks": data})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()

    if body is None:
        abort(404)

    new_title = body.get('title')
    new_recipe = body.get('recipe')

    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()
        drink = new_drink.long()

        return jsonify({
            'success': True,
            'drinks': drink
        })

    except Exception as e:
        print(e)
        abort(404)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()
    selected_drink = Drink.query.get(drink_id)

    if selected_drink is None:
        abort(404)

    if body is None:
        abort(404)

    try:
        selected_drink.title = body.get('title')
        selected_drink.recipe = json.dumps(body.get('recipe'))
        selected_drink.update()

        return jsonify({
            'success': True,
            'drinks': [selected_drink.long()]
        })

    except Exception as e:
        print(e)
        abort(404)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    selected_drink = Drink.query.get(drink_id)

    if selected_drink is None:
        abort(404)

    try:
        selected_drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })

    except Exception as e:
        print(e)
        abort(404)


'''
Logout Endpoint
@app.route('/logout')
def logout():
    auth.logout()
    print("logging out")
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    # params = {'returnTo': url_for('home', _external=True), 'client_id': 'YOUR_CLIENT_ID'}
    return redirect('https://' + AUTH0_DOMAIN + '/v2/logout?')
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "process is unprocessable"
                    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource was not found"
    }), 404


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "its's not authorized"
    }), 401


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''