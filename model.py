
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
    new_task = {"id": get_max_id(),
        "title": form['title'],
        "description": form['description'],
        "category": form['category'],
        "status": "Pending"
        } 
    task_items.append(new_task)
    save_db()

def delete_task_by_id(task_id):
    for index, task in enumerate(task_items):
        if task["id"] == task_id:
            del task_items[index] 
            save_db()
            break

def update_task_by_id(task_id, update_task):
    for index, task in enumerate(task_items):
        if task["id"] == task_id:
            task_items[index] = update_task
            save_db()

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



