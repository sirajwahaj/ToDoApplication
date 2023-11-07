from flask import (Flask,render_template, request,redirect,url_for,flash,jsonify)
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import requests

import model
import config
import utility
import http_request

app = Flask(__name__)

# #################### Config ##########################
# security mechanisms used in web applications to protect against Cross-Site Request 
app.secret_key = config.JWT_SECRET_KEY
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)

model.task_items = model.load_db("task.json")

# #################### ENDPOINT - AUTH PROCESS ##########################

# the 'Authorization' header with the JWT token 
def authorized_request():
    headers = {
        'Authorization': f"Bearer {config.jwt_token}"
    }

    # Make an HTTP GET request to the API with the 'Authorization' header
    request_url = request.url_root + "/protected"
    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        config.jwt_token = ""

    return response.status_code

def get_is_auth():
    return config.jwt_token != "" 

def requires_authentication(func):
    def decorated_function(*args, **kwargs):
        auth_result = authorized_request()
        if (auth_result != 200):
            return redirect(url_for("login")) 
    
        return func(*args, **kwargs)
    return decorated_function

# Custom authentication decorator
def allow_access_only_browser(func):
    def decorated_function(*args, **kwargs): 
        if utility.is_access_from_postman():
            return "Postman can't access to this URL"
        return func(*args, **kwargs)
    return decorated_function


@app.route("/protected", methods=["GET"], endpoint="protected")
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/login", methods=["GET","POST"], endpoint="login")
@allow_access_only_browser
def login():
    is_authen = get_is_auth()
    authForm = utility.AuthForm() 
    if not get_is_auth() :
        if request.method == "POST":
            config.jwt_token = create_access_token(identity=config.JWT_SECRET_KEY)
            flash("authorization has been successfully ", "success")
            return redirect(url_for("home"))
    
    return render_template("login.html", 
                           is_authen=is_authen, 
                           form=authForm)  

@app.route("/logout", endpoint="logout")
@allow_access_only_browser
def logout():
    config.jwt_token = ""
    flash("You have logout !! ", "success")
    return redirect(url_for("home"))


# #################### BACKEND ##########################
# 1. GET /tasks: Retrieves all tasks. For an "VG" (Very Good) requirement, add a "completed" parameter to filter by completed or uncompleted tasks.
@app.route("/tasks/", methods=["GET"])
def all_task():
    return model.task_items

# 2. POST /tasks: Adds a new task. The task is initially uncompleted when first added.
@app.route("/tasks/", methods=["POST"])
def add_new_task():
    model.add_new_task(request.form) 
    return {"status": 200, "result": "added new task"}

# 3. GET /tasks/{task_id}: Retrieves a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    return model.get_task_by_id(task_id)

# 4. DELETE /tasks/{task_id}: Deletes a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task_info = model.get_task_by_id(task_id)
    if not task_info:
        return {"taskId": task_id,"result": "Not found"} 

    model.delete_task_by_id(task_id)
    return {"taskId" :task_id,
        "result": "deleted"} 


# 5. PUT /tasks/{task_id}: Updates a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task_info = model.get_task_by_id(task_id)
    if not task_info:
        return {"taskId": task_id,"result": "Not found"} 
    
    update_task = {"id": task_id,
    "title": request.form['title'],
    "description": request.form['description'],
    "category": request.form['category'],
    "status": request.form['status']
    }

    model.update_task_by_id(task_id, update_task)
    return  {"taskId" :task_id,"result": update_task}


# 6. PUT /tasks/{task_id}/complete: Marks a task as completed.
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def set_task_completed(task_id):
    task_info = model.get_task_by_id(task_id)

    if task_info:
        task_to_update = task_info
        if not task_info["status"] == "Completed":
            task_to_update["status"] = "Completed"
            model.update_task_by_id(task_id, task_to_update)
            return  {"status": 200} 
        else:
            return {"status": 201, "msg": f"You already completed task"} 
    else:
        return {"status": 404, "msg": "Not found"}

# 7. GET /tasks/categories/: Retrieves all different categories.
@app.route("/tasks/categories", methods=["GET"])
def get_all_categories():
    return jsonify(result = model.get_all_categories())

# 8. GET /tasks/categories/{category_name}: Retrieves all tasks from a specific category.
@app.route('/tasks/categories/<category_name>', methods=['GET'])
def filter_by_category(category_name):
    return model.filter_by_category(category_name)

# #################### FRONTEND ##########################

@app.route('/', methods=['GET'], endpoint="home")
@allow_access_only_browser
def home(): 
    filter_items = http_request.request_all_tasks()

    deleteItemForm = utility.DeleteItemForm() 
    filter_form = utility.FilterForm(request.args, meta={"csrf": False}) 
    category_items = model.get_categories_tuples()
    category_items.insert(0, ("-", "---"))   
    filter_form.category.choices = category_items

    filter_form.status.choices.insert(0, ("-", "---"))
 
    if filter_form.validate():  
        filter_title = filter_form.title.data
        filter_status = filter_form.status.data
        fileter_category = filter_form.category.data
   
        if filter_title.strip():
            matching_tasks = []
            for task in filter_items:
                if filter_title.lower() in task["title"].lower():
                    matching_tasks.append(task)
            filter_items = matching_tasks
        else:
            filter_title = "-"

        if not filter_status == "-":
            matching_tasks = []
            for task in filter_items:
                if filter_status.lower() in task["status"].lower():
                    matching_tasks.append(task)
            filter_items = matching_tasks

        if not fileter_category == "-":
            matching_tasks = []
            for task in filter_items:
                if fileter_category.lower() in task["category"].lower():
                    matching_tasks.append(task)
            filter_items = matching_tasks

    return render_template("home.html",
                        is_authen = get_is_auth(),
                        items=filter_items,
                        categories=[],
                        form=filter_form,
                        filterTitle="",
                        filterStatus="",
                        filterCategory="",
                        deleteItemForm=deleteItemForm)

# -------- ITEM DETAIL  ------------
@app.route("/todo/<int:task_id>/detail", methods=["GET"], endpoint="detail_tasks")
def item(task_id):  
    deleteItemForm = utility.DeleteItemForm() 

    task_info = http_request.request_task_by_id(task_id) 
    if task_info:
        return render_template("item.html", 
                                is_authen = get_is_auth(),
                                item=task_info, 
                                deleteItemForm=deleteItemForm) 
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home"))

# -------- NEW ITEM  ------------
@app.route("/todo/new", methods=["GET", "POST"], endpoint="new_tasks")
@requires_authentication
def new_item():
    form = utility.NewItemForm() 
    category_items = category
    form.category.choices = category_items 

    if form.validate_on_submit():
        http_request.request_add_new_task(request.form)
        return redirect(url_for("home")) 
     
    return render_template("new_item.html", is_authen = get_is_auth(), form=form)

# -------- UPDATE ITEM  ------------
@app.route("/todo/<int:task_id>/edit", methods=["GET", "POST"], endpoint="edit_tasks")
@requires_authentication
def edit_item(task_id):
    return "render_template('home.html')"
        
# -------- COMPLATE TASK -------
@app.route("/todo/<int:task_id>/complate", methods=["POST"], endpoint="complete_tasks")
@requires_authentication
def set_task_completed(task_id):
    response = http_request.request_update_completed(task_id)
    if response.status_code == 200:
        flash(f"You have set completed to task", "success")
    else:
        flash(f"Warning: You already completed task", "danger")

    return redirect(url_for("home")) 
    
# -------- DELETE ITEM  ------------
@app.route("/todo/<int:task_id>/delete", methods=["POST"], endpoint="delete_tasks")
@requires_authentication
def delete_tasks(task_id): 
    http_request.request_delete_task(task_id)
    return redirect(url_for("home"))


# -------- ERROR HANDLER  ------------
app.register_error_handler(404, utility.page_404)
app.register_error_handler(405, utility.page_405)
app.register_error_handler(401, utility.page_401)


# if __name__ == '__main__':
#     app.run(debug=True)
