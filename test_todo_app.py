from app import app
import pytest
import model
from flask import request

model.task_filename = "task_test.json"
model.task_items = model.load_db(model.task_filename)

'''
We will test on task_test.json. 
You have to follow task_id in this file to test preview, update, delete.
We test only backend endpoints and Request JWT token (extra endpoint)

backend response tatus: 
200 : success
201 : not found
202 : title is empty
203 : task already completed
'''


@pytest.fixture
def client():
    # Create a test client for the Flask app
    with app.test_client() as client:
        yield client

# 1. GET /tasks: Retrieves all tasks. For an "VG" (Very Good) requirement, add a "completed" parameter to filter by completed or uncompleted tasks.
# @app.route("/tasks/", methods=["GET"])


def test_task_all_tasks(client):
    response = client.get('/tasks/')
    assert response.status_code == 200
    response_data = response.get_json()
    assert isinstance(response_data, list)

# 2. POST /tasks: Adds a new task. The task is initially uncompleted when first added.
# @app.route("/tasks/", methods=["POST"])


def test_task_new_record_success(client):
    headers = {}
    form_data = {"title": "Test form",
                 "description": "detail",
                 "category": "test task"
                 }

    response = client.post('/tasks/', data=form_data, headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 200


def test_task_new_record_failed(client):
    headers = {}
    form_data = {
        "description": "detail",
        "category": "test task"
    }

    response = client.post('/tasks/', data=form_data, headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 202

# 3. GET /tasks/{task_id}: Retrieves a task with a specific ID.
# @app.route("/tasks/<int:task_id>", methods=["GET"])


def test_task_get_task_found(client):
    task_id = 1
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    response_data = response.get_json()
    assert "id" in response_data


def test_task_get_task_not_found(client):
    task_id = 9999
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    response_data = response.get_json()
    assert not "id" in response_data


# 4. DELETE /tasks/{task_id}: Deletes a task with a specific ID.
# @app.route("/tasks/<int:task_id>", methods=["DELETE"])
def test_task_delete_task_found(client):
    task_id = 2
    # get token
    headers = {
        "User-Agent": "PostmanRuntime/7.34.0"
    }

    form_data = {"get": "token"}
    response = client.post('/login', data=form_data, headers=headers)
    response_data = response.get_json()

    # request delete
    headers = {
        'Authorization': f"Bearer {response_data["token"]}"
    }
    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 200


def test_task_delete_task_not_found(client):
    task_id = 3
    # get token
    headers = {
        "User-Agent": "PostmanRuntime/7.34.0"
    }

    form_data = {"get": "token"}
    response = client.post('/login', data=form_data, headers=headers)
    response_data = response.get_json()

    # request delete
    headers = {
        'Authorization': f"Bearer {response_data["token"]}"
    }
    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 201


def test_task_delete_without_unauthorized(client):
    task_id = 3
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 401

# 5. PUT /tasks/{task_id}: Updates a task with a specific ID.
# @app.route("/tasks/<int:task_id>", methods=["PUT"])


def test_task_update_record_success(client):
    task_id = 1
    headers = {}
    form_data = {
        "task_id": task_id,
        "title": "Test form-update",
        "description": "detail",
        "category": "test task",
        "status": "Pending"
    }

    response = client.put(f'/tasks/{task_id}', data=form_data, headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 200


def test_task_update_record_failed(client):
    task_id = 1
    headers = {}
    form_data = {
        "task_id": task_id,
        "title": "",
        "description": "detail",
        "category": "test task",
        "status": "Pending"
    }

    response = client.put(f'/tasks/{task_id}', data=form_data, headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 202

# 6. PUT /tasks/{task_id}/complete: Marks a task as completed.
# @app.route("/tasks/<int:task_id>/complete", methods=["PUT"])


def test_task_set_completed_200(client):
    task_id = 1
    response = client.put(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 200


def test_task_set_completed_201(client):
    task_id = 6
    response = client.put(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 201


def test_task_set_completed_203(client):
    task_id = 1
    response = client.put(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['status'] == 203

# 7. GET /tasks/categories/: Retrieves all different categories.
# @app.route("/tasks/categories", methods=["GET"])


def test_task_all_category_200(client):
    response = client.get('/tasks/categories')
    assert response.status_code == 200
    response_data = response.get_json()
    assert isinstance(response_data, dict)
    assert "result" in response_data
    assert isinstance(response_data["result"], list)

# 8. GET /tasks/categories/{category_name}: Retrieves all tasks from a specific category.
# @app.route('/tasks/categories/<category_name>', methods=['GET'])


def test_task_category_by_name_200(client):
    category_name = "medium"
    response = client.get(f'/tasks/categories/{category_name}')
    assert response.status_code == 200
    response_data = response.get_json()
    assert isinstance(response_data, list)


# Extra enpoint: Request JWT token
def test_request_jwt_token(client):
    headers = {
        "User-Agent": "PostmanRuntime/7.34.0"
    }

    form_data = {"get": "token"}
    response = client.post('/login', data=form_data, headers=headers)
    assert response.status_code == 200
    response_data = response.get_json()
    assert "token" in response_data
