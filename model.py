
import json 

task_items = []
task_filename = "task.json"
category_filename = "category.json"

def load_db(filename):
    json_dict = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
                try:
                    json_dict = json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Wrong JSON format: {e}")
                except ValueError:
                    print("File is not json format")
    except FileNotFoundError:
        f = open(filename, "w", encoding="utf-8")
        f.writelines("[]")  

    return json_dict

def get_max_id():
    if not task_items: 
        return 1
    else: 
        # Find the maximum ID in the list
        max_id = max(task["id"] for task in task_items)
        # Calculate the next ID
        return max_id + 1   

def save_db():
    with open(task_filename, 'w') as f:
        return json.dump(task_items, f, indent=4) 

def get_task_by_id(task_id): 
    for task in task_items:
        if task["id"] == task_id:
            return task
    return None


def add_new_task(form):
    if not "title" in form:
       return False
    
    description = form['description'] if "description" in form else ""
    category = form['category'] if "category" in form else "Default"

    if form['title'].strip():
        new_task = {"id": get_max_id(),
            "title": form['title'],
            "description": description,
            "category": category,
            "status": "Pending"
        } 
        task_items.append(new_task)
        save_db()
        return True
    else:
        return False
    
def update_task_by_id(task_id, form):
    if not "title" in form:
       return False
    
    description = form['description'] if "description" in form else ""
    category = form['category'] if "category" in form else "Default"
    status = form['status'] if "status" in form else "Pending"

    if form['title'].strip():
        update_task = {"id": task_id,
            "title": form['title'],
            "description": description,
            "category": category,
            "status": "Completed" if status.lower() == 'completed' else "Pending",
        }

        for index, task in enumerate(task_items):
            if task["id"] == task_id:
                task_items[index] = update_task
                save_db()
                return True
        return False
    else:
        return False


def delete_task_by_id(task_id):
    for index, task in enumerate(task_items):
        if task["id"] == task_id:
            del task_items[index] 
            save_db()
            break

def get_all_categories():
    categoreis = set()
    for value in task_items:
        categoreis.add(value['category'])
    return list(categoreis)


def filter_by_category(category_name):
    tasks_list = list()

    for task in task_items:
        if task['category'].lower() == category_name.lower():
            tasks_list.append(task)

    return tasks_list


def get_categories_tuples():
    cateigries = get_all_categories()
    return [(item, item) for item in cateigries]

def do_filter_task(filter_form):
    # get all task
    filter_items = task_items

    filter_title = filter_form.title.data
    filter_status = filter_form.status.data
    fileter_category = filter_form.category.data
    # filter text search
    if filter_title.strip():
        matching_tasks = []
        for task in filter_items:
            if filter_title.lower() in task["title"].lower():
                matching_tasks.append(task)
        filter_items = matching_tasks
    else:
        filter_title = "-"
    # filter status
    if not filter_status == "-":
        matching_tasks = []
        for task in filter_items:
            if filter_status.lower() in task["status"].lower():
                matching_tasks.append(task)
        filter_items = matching_tasks
    # filter category
    if not fileter_category == "-":
        matching_tasks = []
        for task in filter_items:
            if fileter_category.lower() in task["category"].lower():
                matching_tasks.append(task)
        filter_items = matching_tasks
    return filter_items



