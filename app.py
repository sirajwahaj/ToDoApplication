from flask import (Flask,render_template, request,redirect,url_for,flash,jsonify)
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import requests

import model
import config
import utility
import http_request

'''
Backend response status: 
200 : success
201 : not found
202 : title is empty
203 : task already completed
'''

app = Flask(__name__)

# #################### Config ##########################
# security mechanisms used in web applications to protect against Cross-Site Request 
app.secret_key = config.JWT_SECRET_KEY
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)

# Load tasks from json
model.task_items = model.load_db(model.task_filename)

# #################### ENDPOINT - AUTH PROCESS ##########################
# check if user login
def get_is_auth():
    return config.jwt_token != "" 

# Custom authentication decorator
def allow_access_only_browser(func):
    def decorated_function(*args, **kwargs): 
        if utility.is_access_from_postman():
            return "Postman can't access to this URL"
        return func(*args, **kwargs)
    return decorated_function

# render login form
@app.route("/login", methods=["GET"], endpoint="login")
@allow_access_only_browser
def login():
    is_authen = get_is_auth()
    authForm = utility.AuthForm() 
    return render_template("login.html", 
                           is_authen=is_authen, 
                           form=authForm)  

# get token frontend-> redirect to home , postman -> show token
@app.route("/login", methods=["POST"], endpoint="get_token")
def get_token():
    config.jwt_token = create_access_token(identity=config.JWT_SECRET_KEY)
    if utility.is_access_from_postman():
        return jsonify(token=config.jwt_token)
    else:
        flash("authorization has been successfully ", "success")
        return redirect(url_for("home"))

# clear token on front end / backend still has token 
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
    response = model.task_items
    return response if response else []


# 2. POST /tasks: Adds a new task. The task is initially uncompleted when first added.
@app.route("/tasks/", methods=["POST"])
def add_new_task():
    response = model.add_new_task(request.form) 
    return jsonify(status = 200 if response else 202 , 
                   msg = "Success" if response else "Invalid submit form")


# 3. GET /tasks/{task_id}: Retrieves a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    response = model.get_task_by_id(task_id)
    return response if response else {}


# 4. DELETE /tasks/{task_id}: Deletes a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    task_info = model.get_task_by_id(task_id)
    if not task_info:
        return jsonify(status = 201, msg= "Not found")

    model.delete_task_by_id(task_id)
    return jsonify(status = 200, msg= "Success")


# 5. PUT /tasks/{task_id}: Updates a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task_info = model.get_task_by_id(task_id)
    if not task_info:
        return jsonify(status = 201, msg= "Not found") 
    
    response = model.update_task_by_id(task_id, request.form)

    return jsonify(status = 200 if response else 202 , 
                   msg = "Success" if response else "Invalid submit form") 


# 6. PUT /tasks/{task_id}/complete: Marks a task as completed.
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def set_task_completed(task_id):
    task_info = model.get_task_by_id(task_id)
    if task_info:
        task_to_update = task_info
        if not task_info["status"] == "Completed":
            task_to_update["status"] = "Completed"
            model.update_task_by_id(task_id, task_to_update)
            return  jsonify(status = 200, msg="success")  
        else:
            return jsonify(status = 203, msg="You already completed task") 
    else:
        return jsonify(status = 201, msg= "Not found")


# 7. GET /tasks/categories/: Retrieves all different categories.
@app.route("/tasks/categories", methods=["GET"])
def get_all_categories():
    response = model.get_all_categories()
    return jsonify(result = response if response else {})


# 8. GET /tasks/categories/{category_name}: Retrieves all tasks from a specific category.
@app.route('/tasks/categories/<category_name>', methods=['GET'])
def filter_by_category(category_name):
    response = model.filter_by_category(category_name)
    return jsonify(response if response else [])

# #################### FRONTEND ##########################
@app.route('/', methods=['GET'], endpoint="home")
@allow_access_only_browser
def home(): 
    # prepare filter form
    deleteItemForm = utility.DeleteItemForm() 
    filter_form = utility.FilterForm(request.args, meta={"csrf": False}) 
    category_items = model.get_categories_tuples()
    category_items.insert(0, ("-", "---"))   
    filter_form.category.choices = category_items

    filter_form.status.choices.insert(0, ("-", "---"))
    # do filter 
    if filter_form.validate():  
        filter_items = model.do_filter_task(filter_form)
    else:
        filter_items = http_request.request_all_tasks()

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
@allow_access_only_browser
def item(task_id):  
    deleteItemForm = utility.DeleteItemForm()  
    
    task_info = http_request.request_task_by_id(task_id) 
    if task_info:
        return render_template("item.html", 
                                is_authen = get_is_auth(),
                                item=task_info, 
                                deleteItemForm=deleteItemForm) 
    else: 
        flash("Not found item", "warning")

    return redirect(url_for("home"))

# -------- NEW ITEM  ------------
@app.route("/todo/new", methods=["GET", "POST"], endpoint="new_tasks")
@allow_access_only_browser
def new_item():
    form = utility.NewItemForm()
    form.category.choices = model.get_categories_tuples() 

    if form.validate_on_submit():
        response = http_request.request_add_new_task(request.form)
        if response["status"] == 200:
            flash(f"Added item", "success")
        else:
            flash(f"Some thing went wrong with adding item", "warning")
        return redirect(url_for("home")) 
     
    return render_template("new_item.html", is_authen = get_is_auth(), form=form)

# -------- UPDATE ITEM  ------------
@app.route("/todo/<int:task_id>/edit", methods=["GET", "POST"], endpoint="edit_tasks")
@allow_access_only_browser
def edit_item(task_id):
    task_info = http_request.request_task_by_id(task_id) 

    if task_info:
        form = utility.EditItemForm()
        # method POST : update data
        if form.validate_on_submit(): 
            response = http_request.request_update_task(request.form, task_id)
            # result
            if response["status"] == 200:
                flash("Item {} has been successfully updated"
                    .format(form.title.data), "success")
                return redirect(url_for("detail_tasks", task_id=task_id))
            else: 
                flash("Some thing wrong with update item process"
                .format(request.form.get("title")), "danger")    
        
        # method GET prepare form with task_info
        form.status.default = task_info["status"]
        form.process()
        form.title.data       = task_info["title"]
        form.description.data = task_info["description"]
        form.category.data = task_info["category"]

        return render_template("edit_item.html", 
                                is_authen = get_is_auth(),
                                item=task_info, form=form)
    else: 
        flash("Not found item", "warning")

    return redirect(url_for("home")) 
        
# -------- COMPLATE TASK -------
@app.route("/todo/<int:task_id>/complate", methods=["POST"], endpoint="complete_tasks")
@allow_access_only_browser
def set_task_completed(task_id):
    response = http_request.request_update_completed(task_id)
    if response["status"] == 200:
        flash(f"You have set completed to task", "success")
    elif response["status"] == 203:
        flash(f"You already completed task", "warning")
    elif response["status"] == 201:
        flash(f"Not found item", "warning")

    return redirect(url_for("home")) 
    
# -------- DELETE ITEM  ------------
@app.route("/todo/<int:task_id>/delete", methods=["POST"], endpoint="delete_tasks")
@allow_access_only_browser
def delete_tasks(task_id): 
    response = http_request.request_delete_task(task_id)
    if response["status"] == 200:
        flash(f"Deleted", "success")
    else:
        flash(f"Something went worong with authentication", "warning")
    return redirect(url_for("home"))


# -------- ERROR HANDLER  ------------
app.register_error_handler(404, utility.page_404)
app.register_error_handler(405, utility.page_405)
app.register_error_handler(401, utility.page_401)


# if __name__ == '__main__':
#     app.run(debug=True)
