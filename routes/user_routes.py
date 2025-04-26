from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2
from flask_api import app


@app.route("/home_user")
def web_home_users():
    return render_template("user.html")