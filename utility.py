from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length
from werkzeug.utils import escape

from flask import request,render_template

# #################### WT-FORM ##########################
class ItemForm(FlaskForm):
    title       = StringField("Title", 
                              validators=[InputRequired("Input is required!"),
                                          Length(min=5, max=100, message="Input must be between 5 and 20 characters long")])
    description = TextAreaField("Description")
    category = StringField("Category", validators=[InputRequired()])
    # category    = SelectField("Category", coerce=int, validators=[InputRequired()])
 
class NewItemForm(ItemForm):
    submit      = SubmitField("Submit")

class EditItemForm(ItemForm):
    status    = SelectField("status",
                            choices=[('Pending', 'Pending'),
                                    ('Completed', 'Completed')],
                            coerce=str)
    submit      = SubmitField("Update item")

class DeleteItemForm(FlaskForm):
    submit      = SubmitField("Delete item")

class AuthForm(FlaskForm):
    submit      = SubmitField("Get Token")
    
        # {{ form.title.label }}
        #     {{ form.title(class="form-control") }}
class FilterForm(FlaskForm):
    title       = StringField("Title", validators=[Length(max=20)])
    category    = SelectField("Category", choices=[], coerce=str)
    status    = SelectField("status",
                            choices=[('Pending', 'Pending'),
                                    ('Completed', 'Completed')],
                            coerce=str)
    submit      = SubmitField("Filter")



# #################### FLASK ##########################
def is_access_from_postman():
    user_agent = request.headers.get('User-Agent') 
    substring = "Postman"
    return substring in user_agent

def get_error_tag(status, msg):
    return {"status": status,
            "msg": msg}

def page_404(e):
    if is_access_from_postman():
        return "404: Page Not Found"
    else:
        return render_template("errors/404.html")

def page_405(e):
    if is_access_from_postman():
        return "405: Method Not Allowed"
    else:
        return render_template("errors/405.html")

def page_401(e):
    if is_access_from_postman():
        return "401: Unauthorized Error"
    else:
        return render_template("errors/401.html")

