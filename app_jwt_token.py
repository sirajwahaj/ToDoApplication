'''
Exapmple of How to request basic JWT token
'''
from flask import (Flask, request, jsonify)
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import requests

import config

app = Flask(__name__)

# #################### Config ##########################
# security mechanisms used in web applications to protect against Cross-Site Request
app.secret_key = "set your JWT_SECRET_KEY"
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "set your JWT_SECRET_KEY"
jwt = JWTManager(app)


@app.route("/")
def home():
    return ("GET : http://127.0.0.1:5000/todo/delete <br>" +
            "GET : http://127.0.0.1:5000/login <br>" +
            "DELETE : http://127.0.0.1:5000/task/1 <br>" +
            "GET: http://127.0.0.1:5000/task/delete <br>"
            )


@app.route("/login", methods=["GET"], endpoint="get_token")
def get_token():
    config.jwt_token = create_access_token(identity=config.JWT_SECRET_KEY)
    return jsonify(token=config.jwt_token)


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    return jsonify(status=200, msg="deleted item")


@app.route("/task/delete")
def do_delete():
    task_id = 1
    headers = {
        'Authorization': f"Bearer {config.jwt_token}"
    }
    request_url = request.url_root + f"/tasks/{task_id}"
    response = requests.delete(request_url, headers=headers)
    return response.json()


if __name__ == '__main__':
    app.run(debug=True)
