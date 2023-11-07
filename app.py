from flask import Flask,render_template

import utility

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/new_tasks', methods=['GET'])
def new_tasks():
    return "render_template('home.html')"

@app.route('/logout', methods=['GET'])
def logout():
    return "render_template('home.html')"

@app.route('/login', methods=['GET'])
def login():
    return "render_template('home.html')"

# -------- ERROR HANDLER  ------------
app.register_error_handler(404, utility.page_404)
app.register_error_handler(405, utility.page_405)
app.register_error_handler(401, utility.page_401)


# if __name__ == '__main__':
#     app.run(debug=True)
