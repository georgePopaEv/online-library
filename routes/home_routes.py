from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort

from flask_api import app
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2

@app.route("/")
def welcomes():
    return render_template("index.html")


@app.route("/login")
def home():
    return render_template("login_new.html")

@app.route("/login", methods=["POST"])
def web_login():
    try:
        if request.method == "POST":
            user = request.form['username']
            passwd = request.form['password']

            query = read_from_db(f"""
                SELECT username, password, is_admin
                FROM project.users
                WHERE username = '{user}' AND password = '{passwd}'
            """)

            if not query or isinstance(query[0], str):
                abort(400, message="Userul nu exista")
            else:
                session['user'] = user
                session['is_admin'] = query[0]['is_admin']
                # TO DO sa scapam de "da" si sa primeasca valori true folse
                if session['is_admin'] == "Da":
                    return redirect(url_for("web_home"))
                else:
                    return redirect(url_for("web_home_users"))

        return render_template("login_new.html")

    except Exception as e:
        return f"Eroare: {str(e)}"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

