from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_required, current_user
from models.user import User
from extensions import db

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
        senha = request.form.get("password")
        
        if current_user.role != 'coordenador' and role == 'coordenador':
            flash("Coordenador nao pode criar outro coordenador.", "danger")
            
            return render_template("users/form.html", form_data={"nome": nome, "email": email, "role": role})
        
        if not senha:
            flash("Senha é obrigatória.", "danger")
            return render_template("users/form.html", form_data={"nome": nome, "email": email, "role": role})
        
        user = User(nome=nome, email=email, role=role)
        user.set_password(senha)
        db.session.add(user)
        db.session.commit()

        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("users.index"))
    
    return render_template("users/form.html")


@login_required
def show():
    usuarios = User.query.all()
    return render_template("users/show.html", usuarios=usuarios)

@login_required
def edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.nome = request.form.get("nome")
        user.email = request.form.get("email")
        role = request.form.get("role", "aluno")
        senha = request.form.get("senha")

        if current_user.role != 'coordenador' and role == 'coordenador':
            flash("Coordenador nao pode promover outro usuario a coordenador.", "danger")
            return render_template("users/form.html", user=user)

        user.role = role

        if senha:
            user.set_password(senha)

        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("users.show", user_id=user.id))

    return render_template("users/form.html", user=user)


@login_required
def delete(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == 'master':
        flash("Não é possível deletar o usuário master.", "danger")
        return redirect(url_for("users.index"))

    db.session.delete(user)
    db.session.commit()
    flash("Usuário deletado com sucesso!", "success")
    return redirect(url_for("users.index"))