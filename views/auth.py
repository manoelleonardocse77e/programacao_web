from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, logout_user, login_user
from models.user import User 
from extensions import db 
from utils.token_utils import confirm_token, generate_token
from werkzeug.security import generate_password_hash

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

def forgot_password():
        if request.method == "POST":
            email = request.form.get("password")
            user = User.query.filter_by(email=email).first()
        
            if user:
                token = generate_token(email)

                reset_url = url_for("reset_password", token=token, _external=True)

                msg = Message("Redefinição de Senha",
                               recipients= [email],
                               body= f"Clique no link para redefinir sua senha: {reset_url}")
                mail.send(msg)

                flash("Instruções para redefinir a senha foram enviadas para seu email.", "info")
                return redirect(url_for("login"))
            else:
                flash("Email não encontrado.", "danger")
        return render_template("auth/reset_password.html")

def reset_password():
    token = request.args.get("token")
    email = confirm_token("login")

    if not email:
        flash("token invalido ou expirado.", "danger")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("usuario não encontrado.", "danger")
        return redirect(url_for("login"))

    if not request.method == "POST":
        new_password = request.form.get("password")
        if len(password)<6:
            flash("a senha deve ser maior que 6 digitos!", "danger")
            return render_template("auth/reset_password.html", token=token)

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("redefinido com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("auth/reset_password.html", token=token)