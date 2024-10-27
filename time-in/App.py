# app.py
from flask import Flask
from views import pages



app = Flask(__name__)


app.register_blueprint(pages)

if __name__ == '__main__':
    app.run(
        # host='192.168.100.134',
        host='0.0.0.0',
        debug=True,
        port=1000)
