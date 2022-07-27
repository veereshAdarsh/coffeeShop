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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
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
def getDrinks():
    #Fetch all drinks from DB
    allDrinks = Drink.query.all()
    drinks = [drink.short() for drink in allDrinks]
    return jsonify({
        'success' : True,
        'drinks' : drinks
    }), 200

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
#Get drink details only when user provides authentication
def get_drink_details(payload):
        allDrinks = Drink.query.all()
        drinks = [drink.long() for drink in allDrinks]
        return jsonify({
            'success' : True,
            'drinks': drinks
        }), 200


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
#Create drinks
def post_drink(payload):
    body = request.get_json()
    print(body)
    try:
        drink = Drink()
        drink.title = body['title']
        drink.recipe = json.dumps(body['recipe'])
        drink.insert()
        drinks=[drink.long()]

        return jsonify({
            'success' : True,
            'drinks': drinks
        })
    
    except:
        abort(422)


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
@app.route('/drinks/<int:drinkID>', methods=['PATCH'])
@requires_auth('patch:drinks')
#Update drinks
def update_drink(payload, drinkID):
    body = request.get_json()
    print(body)

    drink = Drink.query.filter(Drink.id==drinkID).one_or_none()
    if not drink:
        abort(404)
    
    try:
        title = body.get('title')
        recipe = body.get('recipe')

        if title != None:
            drink.title = title

        if recipe != None:
            drink.recipe = json.dumps(body['recipe'])
        
        drink.update()

        drinks = [drink.long()]
        return jsonify({
            'success' : True,
            'drinks' : drinks
        }), 200
    
    except:
        abort(422)


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
@app.route('/drinks/<int:drinkID>', methods=['DELETE'])
@requires_auth('delete:drinks')
#Delete drinks by id
def delete_drinks(payload, drinkID):
    drink = Drink.query.filter(Drink.id==drinkID).one_or_none()

    if not drink:
        abort(404)
    
    try:
        drink.delete()
        return jsonify({
            'success' : True,
            'delete': drink.id
        }), 200
    except:
        abort(422)


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
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success' : False,
        'error' : error.status_code,
        'message' : error.error['description']
    }), error.status_code