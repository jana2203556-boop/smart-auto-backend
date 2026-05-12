from flask import Flask
from flask_cors import CORS
from database.db import mysql

import config

from routes.auth import auth_bp
from routes.spareparts import spareparts_bp
from routes.orders import orders_bp
from routes.workshops import workshops_bp
from routes.admin import admin_bp

app = Flask(__name__)

CORS(app)

app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = config.MYSQL_DB
app.config["SECRET_KEY"] = config.SECRET_KEY

mysql.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(spareparts_bp, url_prefix="/spareparts")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(workshops_bp, url_prefix="/workshops")
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.route("/")
def home():
    return {"message": "Smart Auto Backend Running"}

if __name__ == "__main__":
    app.run(debug=True)