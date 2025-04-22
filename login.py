
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2


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
                # TO DO sa scapam de "da" si sa primeasca valori true folse
                if session['is_admin'] == "Da":
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
def welcome():
    return render_template("welcome.html")

@app.route("/login")
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


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        page_count = request.form['page_count']
        author_name = str(request.form['author_id'])
        genre_name = request.form['genre_id']
        print(genre_name)
        if not title or not description or not page_count or not author_name or not genre_name:
            flash("Please fill in all fields.", "error")
            return render_template("add_book.html")
        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute(f"select * from project.authors where full_name = '{author_name}'")
            query_author = cursor.fetchall()

            if not query_author:
                cursor.execute(
                    "insert into  project.authors (full_name) VALUES (%s) RETURNING author_id",
                    (author_name,)
                )
                author_id = cursor.fetchone()[0]

                connection.commit()
            else:
                author_id = query_author[0][0]
            insert_query = """
                            insert into project.books (title, description, page_count, author_id, genre_id)
                            values (%s, %s, %s, %s, %s)
                        """
            cursor.execute(insert_query, (title, description, int(page_count), author_id, int(genre_name)))
            connection.commit()
            cursor.close()
            connection.close()

            flash("Book added successfully!", "Success")
            return redirect(url_for("web_home"))
        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while adding the book.", "Error")
            return render_template("add_book.html")
    elif request.method == "GET":
        query = read_from_db("select * from project.genres")
        list_genres = [(gen["genre_name"], gen["genre_id"]) for gen in query]
        return render_template("add_book.html", genres = list_genres)

    return render_template("add_book.html")


@app.route("/remove_member", methods=["GET", "POST"])
def remove_member():
    if request.method == "POST":
        user_id_to_remove = request.form.get('user_id')
        if user_id_to_remove:
            try:
                connection = psycopg2.connect(**database_config)
                cursor = connection.cursor()
                cursor.execute("delete from project.users where user_id = %s", (user_id_to_remove,))
                connection.commit()
                flash("User removed successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
            finally:
                cursor.close()
                connection.close()
        return redirect(url_for("remove_member"))

    users = read_from_db("select user_id, full_name FROM project.users where is_admin != 'Da'")
    return render_template("remove_member.html", users=users)



@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        fullname = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form['is_admin']

        if not fullname or not username or not password or not is_admin:
            flash("Please fill in all fields.", "error")
            return render_template("add_member.html")

        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute("select * from project.users where username = %s", (username,))
            query_user = cursor.fetchall()

            if query_user:
                flash("User already exists.", "error")
            else:
                cursor.execute(
                    "insert into project.users (full_name, username, password, is_admin) values (%s, %s, %s, %s)",
                    (fullname, username, password, is_admin)
                )
                connection.commit()
                flash("User added successfully!", "success")

            cursor.close()
            connection.close()
            return redirect(url_for("add_member"))

        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while adding the user.", "error")
            return render_template("add_member.html")

    return render_template("add_member.html")


@app.route("/view_books")
def view_books():
    query = """
        select b.title, b.description, b.page_count, a.full_name as author, g.genre_name as genre
        from project.books b
        join project.authors a on b.author_id = a.author_id
        join project.genres g on b.genre_id = g.genre_id
    """
    books = read_from_db(query)
    return render_template("view_books.html", books=books)

@app.route("/user_view_books")
def user_view_books():
    query = """
        select b.title, b.description, b.page_count, a.full_name as author, g.genre_name as genre
        from project.books b
        join project.authors a on b.author_id = a.author_id
        join project.genres g on b.genre_id = g.genre_id
    """
    books = read_from_db(query)
    return render_template("user_view_books.html", books=books)

@app.route("/remove_book", methods=["GET", "POST"])
def remove_book():
    if request.method == "POST":
        book_id_to_remove = request.form.get('book_id')
        if book_id_to_remove:
            try:
                connection = psycopg2.connect(**database_config)
                cursor = connection.cursor()
                cursor.execute("delete from project.books where book_id = %s", (book_id_to_remove,))
                connection.commit()
                flash("Book removed successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
            finally:
                cursor.close()
                connection.close()
        return redirect(url_for("remove_book"))

    books = read_from_db("select book_id, title from project.books")
    return render_template("remove_book.html", books=books)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5011)
    app.run(DEBUG=True)
