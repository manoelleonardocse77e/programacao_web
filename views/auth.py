from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, logout_user, login_user
from models.user import User 
from extensions import db 

# @auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect (url_for("dashboard"))
        else:
            flash("Credenciais inválidas.", "danger")
    return render_template("auth/login.html")

@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))