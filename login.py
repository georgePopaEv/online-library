
from flask import Flask, render_template, request, url_for, session, jsonify, redirect
from flask_smorest import abort
from config import read_from_db, database_config
from flask_restful import abort
app = Flask(__name__)
app.secret_key = "secret_key"


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

                if query[0]['is_admin'] == 'Da':
                    return redirect(url_for("web_home"))
                else:
                    return redirect(url_for("web_home_users"))

        return render_template("login.html")

    except Exception as e:
        return f"Eroare: {str(e)}"


@app.route("/home")
def web_home():
    return render_template("admin_page.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/view_members")
def view_members():
    query = read_from_db("SELECT full_name FROM project.users WHERE is_admin != 'Da'")
    return render_template("view_members.html", members=query)


@app.route("/home_user")
def web_home_users():
    return render_template("user.html")

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/books")
def get_all_books():
    return {"books": list(read_from_db("select * from project.books").values())}

@app.route("/books/<string:book_id>")
def get_book_by_id(book_id):
    try:
        return read_from_db(f"select * from project.books where book_id = {int(book_id)}")
    except KeyError:
        return {"message": "Bad request, Book Not found"}









if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5010)
    app.run(DEBUG=True)
