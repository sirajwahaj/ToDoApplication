import requests
from flask import request
import model

def request_all_tasks():
    request_url = request.url_root + "/tasks"
    response = requests.get(request_url)
    if response.status_code == 200:  # Check for a successful HTTP status code
        return response.json()
    else:
        return []
    
 
    

def request_task_by_id(task_id):
    request_url = request.url_root + f"/tasks/{task_id}" 
    response = requests.get(request_url)
    if response.status_code == 200:  # Check for a successful HTTP status code
        return response.json()
    else:
        return None
    
def request_add_new_task(form):
    new_task = {"id": model.get_max_id(),
                "title": form['title'],
                "description": form['description'],
                "category": form['category'],
                "status": "Pending"
                }
    request_url = request.url_root + f"/tasks/" 
    # Send a POST request with the form data
    return requests.post(request_url, data=new_task)

def request_delete_task(task_id):
    request_url = request.url_root + f"/tasks/{task_id}" 
    return requests.delete(request_url)

def request_update_task(form, task_id):
    update_task = {"id": task_id,
            "title": form['title'],
            "description": form['description'],
            "category": form['category'],
            "status": form['status']
            } 
            # Backend endpoint
    request_url = request.url_root + f"/tasks/{task_id}" 
    # Send a POST request with the form data
    return requests.put(request_url, data=update_task)

def request_update_completed(task_id):
    request_url = request.url_root + f"/tasks/{task_id}/complete" 
    return requests.put(request_url)