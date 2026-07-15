from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = "secret123"  # needed for flash messages

# ---------- Database Connection ----------
def get_connection():
    return pymysql.connect(
        host="localhost",     # change if using remote DB
        user="root",          # your MySQL username
        password="root",      # your MySQL password
        database="flaskdb"    # database you created
    )

# ---------- Routes ----------
@app.route('/')
def index():
    con = get_connection()
    cur = con.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    con.close()
    return render_template("index.html", users=rows)

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        con = get_connection()
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
                        (name, email, password))
            con.commit()
            flash("User Added Successfully!", "success")
        except pymysql.err.IntegrityError:
            flash("Email already exists!", "danger")
        con.close()
        return redirect(url_for("index"))

    return render_template("add_user.html")

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    con = get_connection()
    cur = con.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        name = request.form['name']  
        email = request.form['email']
        password = request.form['password']
        cur.execute("UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                    (name, email, password, id))
        con.commit()
        con.close()
        flash("User Updated Successfully!", "info")
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM users WHERE id=%s", (id,))
    row = cur.fetchone()
    con.close()
    return render_template("edit_user.html", user=row)

@app.route('/delete/<int:id>')
def delete_user(id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    cur.execute("ALTER TABLE users AUTO_INCREMENT = 1")
    con.commit()
    con.close()
    flash("User Deleted Successfully!", "danger")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
