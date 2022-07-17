import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO Initialize the database
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint:  GET /drinks
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    '''
    Fetches all drinks with a short description
    Return the drinks array or the error handler
    '''
    try:
        #drinks = [drink.short() for drink in Drink.query.all()]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        return jsonify({
            'success': False,
            'error': "Unknown error occurred"
        }), 500

'''

@app.route('/headers')
@requires_auth(permission='')
def headers(payload):
    print(payload)
    return 'not implemented'
'''

'''
@TODO implement endpoint GET /drinks-detail
'''

@app.route('/drinks', methods=['GET'], endpoint='get_drinks_details')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    '''
    Fetches all drinks with a long description
    Return the drinks array or the error handler
    '''
    try:
        drinks = [drink.long() for drink in Drink.query.all()]

        return json.dumps({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        return json.dumps({
            'success': False,
            'error': "Error occurred"
        }), 500


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'], endpoint='post_drink')
@requires_auth('post:drinks')
def create_drink(payloads):
    '''
    Creates a new drink and returns its long discription
    Return the created drink details or the error handler.
    '''
    drink_detail =  request.get_json()

    drink = Drink()
    drink.title = drink_detail['title']
    drink.recipe = json.dumps(drink_detail['recipe'])
    print(drink.title, file=sys.stderr)
    print(drink.recipe, file=sys.stderr)
        
    try:
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except Exception as e:
        print(e)
        abort(400)


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

@app.route('/drinks/<id>', methods=['PATCH'], endpoint='patch_drink')
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
     """
     Updates a drink if it exists
     Return the updated drink info or the error handler
     """

     drink_info = request.get_json()
     drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()
     
     # if not existing
     if not drink_to_update:
        abort(404)
    
     # Compare and update the title or recipe
     try:
        if drink_info['title']:
            drink_to_update.title = drink_info['title']
        if drink_info['recipe']:
            drink_to_update.recipe = json.dumps(drink_info['recipe'])
        
        drink_to_update.update()
     except Exception as e:
        print(e)
        abort(400)
     
     #print(drink_to_update.title, file=sys.stderr)
     #print(drink_to_update.recipe, file=sys.stderr)
     
     return jsonify({
            'success': True,
            'drinks': [drink_to_update.long()]
        }), 200


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

@app.route('/drinks/<id>', methods=['DELETE'], endpoint='delete_drink')
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """
     deletes a drink if it exists
     Return the deleted drink info or the error handler
    """
    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink_to_delete:
        abort(404)

    try:
        drink_to_delete.delete()
    except Exception as e:
        print(e)
        abort(400)

    #print(f'Deleted: {drink_id}')
    return jsonify({
            'success': True,
            'drinks': drink_id
        }), 200



# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "Internal server error"
                    }), 500


