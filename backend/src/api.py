# from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
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
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]

        return jsonify({
            "success":True,
            "drinks": formatted_drinks
        })
    except:
        abort(401)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    try:

        formatted_drinks = [drink.long() for drink in drinks]
        print(formatted_drinks)

        return jsonify({
            "success": True,
            "drinks": formatted_drinks
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_new_drink(payload):

    new_post = request.get_json()
    title = new_post["title"]
    recipe = new_post["recipe"]
    # print(title)

    for ingredient in recipe:
        color = ingredient["color"]
        parts = ingredient["parts"]
        name = ingredient["name"]

    found_drink = Drink.query.filter_by(title=title).first()
    if found_drink:
        abort(400)
    
    if not title or not recipe:
        abort(400)

    drink = Drink(
        title = title,
        recipe = json.dumps(recipe)
    )

    print("Drink is:", drink)

  
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })

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
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):

    drink = Drink.query.filter(id==Drink.id).first()
    print("drink is",drink)
    
    if not drink:
        abort(404)

    data = request.get_json()
    title = data["title"]
    recipe = data.get("recipe")
    
    
    drink.title = title
    
    if recipe:
        for ingredient in recipe:    
            if not ingredient:
                abort(400)

            color = ingredient["color"]
            parts = ingredient["parts"]
            name = ingredient["name"]
            
    drink.recipe = json.dumps(recipe)


    drink.update()

    
    return jsonify({
        "success":True,
        "drinks": [drink.long()]
    })

    # except:
    #     db.session.rollback()
    #     # abort(500)


        
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
@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.filter(id==Drink.id).one_or_none()
    print(drink)

    if not drink:
        abort(404)

    try:
        # drink.delete()

        return jsonify({
            "success":True,
            "delete": id
        })
    except:
        db.session.rollback()
        abort(500)

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
        "message": "bad request"
    }), 400

@app.errorhandler(409)
def insertion_error(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "Insertion error occured, since item already exists"
    }, 409)

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500
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
        "message": error.error["description"]
    }), error.status_code