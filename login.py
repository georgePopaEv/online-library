
from flask import Flask, render_template, request, url_for, session, jsonify, redirect
from flask_smorest import abort
from config import read_from_db, database_config

app = Flask(__name__)
app.secret_key = "secret_key"
ADMIN = {
    "admin": "admin1"
}

USERS = {
    "user": "user1"
}

@app.route("/login", methods=["POST"])
def web_login():
    if request.method == "POST":
        user = request.form['username']
        passwd = request.form['password']
        print(user, type(user))
        query = read_from_db(f"select username, password from project.users where username = '{user}' and password = '{passwd}'")
        print(query)
        if not query:
            abort(400, message="Userul nu exista")
        else:
            session['user'] = user
            return redirect(url_for("web_home_users"))
        #TO DO - adaug coloana si verificare admin user.
        # if user in ADMIN:
        #     if passwd == ADMIN[user]:
        #         session['user'] = user
        #         return redirect(url_for("web_home"))
        # elif user in USERS:
        #     if passwd == USERS[user]:
        #         session['user'] = user
        #         return redirect(url_for("web_home_users"))

        return "Invalid credentials <a href='/'>Try Again</a>"

    return render_template("login.html")

@app.route("/home")
def web_home():
    return render_template("admin_page.html")

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

# app.config["SQLALCHEMY_DATABASE_URI"] = "adresa bazei noastre de date postgresql:localgost:5432parola/database_name"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123456@localhost:5432/books"
# app.config["SQLALCHEMY_TRACK_MODIFICATION"]= False
# "postgres"
# db.init_app(app)
# with app.app_context():
#     db.create_all()