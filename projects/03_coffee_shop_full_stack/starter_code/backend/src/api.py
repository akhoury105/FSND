import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        selection = Drink.query.all()
        drinks = [drink.short() for drink in selection]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)
        
'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drink-detail')
def get_drinks_detailed(payload):
    try:
        selection = Drink.query.all()
        drinks = [drink.long() for drink in selection]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)

'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drinks(payload):
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        if not body:
            abort(404)
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except:
        abort(422)

'''
@Done implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drinks(payload, id):
    #Grab form data and query for drink by id.
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    #Check to see if we have a drink with that id.
    if drink == None:
        abort(404)
    #If we do then make the requested updates.
    else:
        if 'title' in body:
            title = body.get('title')
            drink.title = title
        if 'recipe' in body:
            recipe = body.get('recipe')
            drink.recipe = recipe
        try:
            drink.update()
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(422)

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(payload, id):
    # Get the drink by the id.
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # Abort if we don't have a drink.
    if drink == None:
        abort(404)

    # Delete the drink.
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(422)


## Error Handling
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
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(AuthError):
    return jsonify(AuthError.error), AuthError.status_code