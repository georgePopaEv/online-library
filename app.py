
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort, Api
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2
from flask_api import app
import routes.home_routes
import routes.user_routes
import routes.book_routes
import routes.admin_routes





# Smorest (Swagger/OpenAPI)
app.config["API_TITLE"] = "Books REST API"
app.config["API_VERSION"] = "V1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
api=Api(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    app.run(DEBUG=True)
