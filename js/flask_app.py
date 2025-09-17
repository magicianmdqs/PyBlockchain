from flask import request, Flask, render_template, redirect, url_for, flash, session
from Crypto.Hash import SHA256

password_hash = ["febe2ae28820f98801f2c6cf4b260e02e6fa975a3e56800604ebf8917a97669f"]
app = Flask(__name__, template_folder="templates")
app.secret_key = "supersecret"

@app.route("/", methods=["GET", "POST"])
def login():
    password = request.form.get("id_password")
    if password:
        if password_hash[0] == SHA256.new(password.encode("utf-8")).hexdigest():
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("wrong password!")
            session["logged_in"] = False
    return render_template("login.html")


@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/logout")
def log_out():
    session["logged_in"] = False
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=7070,debug=True)
