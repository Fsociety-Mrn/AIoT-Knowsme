# views/user_views.py
from flask import Blueprint, render_template

pages = Blueprint('pages', __name__)

@pages.route('/')
def user_profile():
 
    return render_template('user.html')
