from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_required, current_user
from models.user import User
from extensions import db

users_bp= Blueprint('users', __name__, url_prefix = "/users")
@login_required
def index():
    usuarios = User.query.all()
    return render_template("users/index.html", usuarios=usuarios)


@login_required
def create():
    if request.method =="POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        role = request.form.get("role", "aluno")
        user = User(nome=nome, email=email, role=role)
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        flash("Usuário criado com sucesso!", "sucess")
        return redirect(url_for("users.index"))
    
    return render_template("users/form.html")
