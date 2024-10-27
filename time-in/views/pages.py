from flask import Blueprint, render_template

pages = Blueprint('pages', __name__)


@pages.route('/')
def index():
    return render_template('index.html')


@pages.route('/pages/face-recognition')
def face_recognition():
    return render_template('pages/face-recognition.html')


@pages.route('/pages/face-register')
def face_register():
    return render_template('pages/face-register.html')


@pages.route('/pages/face-training')
def face_training():
    return render_template('pages/face-training.html')

# @pages.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404