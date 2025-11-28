from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from models.treinamento import Treinamento
from models.turma_model import Turma
from models.user import User
from extensions import db
from datetime import datetime

@login_required
def listar():
    treinamentos = Treinamento.query.all()
    return render_template("treinamento/listar.html", treinamentos=treinamentos)


@login_required
def listar_treinamentos():
    # Show only currently active treinamentos (no data_fim or in future)
    now = datetime.utcnow()
    treinamentos = Treinamento.query.filter((Treinamento.data_fim == None) | (Treinamento.data_fim > now)).all()
    return render_template("treinamento/dashboard.html", treinamentos=treinamentos)

@login_required
def novo():
    if current_user.role not in ('coordenador', 'master'):
        abort(403)

    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        data_inicio_str = request.form.get("data_inicio")
        data_fim_str = request.form.get("data_fim")

        if not nome or not data_inicio_str:
            flash("Nome e Data de Início são obrigatórios.", "danger")
            return render_template("treinamento/novo.html", form_data=request.form)
        
        try:
            data_inicio = datetime.fromisoformat(data_inicio_str)
            data_fim = datetime.fromisoformat(data_fim_str) if data_fim_str else None
        except ValueError:
            flash("Formato de data inválido.", "danger")
            return render_template("treinamento/novo.html", form_data=request.form)
        
        treinamento = Treinamento(
            nome = nome,
            descricao = descricao,
            data_inicio = data_inicio,
            data_fim = data_fim,
            coordenador_id = current_user.id
        )
        db.session.add(treinamento)
        db.session.commit()

        flash("Treinamento criado com sucesso!", "success")
        return redirect(url_for("treinamento.listar"))

    return render_template("treinamento/novo.html")


@login_required
def criar_treinamento():
    # alias to novo (compatibility with older route names)
    return novo()


@login_required
def detalhes_treinamento(id):
    treinamento = Treinamento.query.get_or_404(id)
    return render_template("treinamento/detalhes.html", treinamento=treinamento)


@login_required
def editar_treinamento(id):
    treinamento = Treinamento.query.get_or_404(id)
    # Very basic edit functionality: reuse novo template
    if current_user.role != 'coordenador':
        abort(403)

    if request.method == 'POST':
        treinamento.nome = request.form.get('nome') or treinamento.nome
        treinamento.descricao = request.form.get('descricao') or treinamento.descricao
        db.session.commit()
        flash('Treinamento atualizado com sucesso.', 'success')
        return redirect(url_for('treinamento.detalhes', id=id))

    return render_template('treinamento/novo.html', form_data=treinamento)


@login_required
def deletar_treinamento(id):
    treinamento = Treinamento.query.get_or_404(id)
    if current_user.role != 'coordenador':
        abort(403)
    db.session.delete(treinamento)
    db.session.commit()
    flash('Treinamento removido com sucesso.', 'success')
    return redirect(url_for('treinamento.listar'))


@login_required
def listar_turmas(treinamento_id):
    treinamento = Treinamento.query.get_or_404(treinamento_id)
    turmas = treinamento.turmas
    return render_template('treinamento/listar_turmas.html', treinamento=treinamento, turmas=turmas)


@login_required
def vincular_alunos(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    # List available alunos (active with role aluno)
    alunos = User.query.filter_by(role='aluno', ativo=True).all()

    if request.method == 'POST':
        selected_ids = set(int(aid) for aid in request.form.getlist('alunos_ids'))
        # Current students
        current_ids = set(a.id for a in turma.alunos)
        # Remove alunos not selected anymore
        for aid in current_ids - selected_ids:
            aluno = User.query.get(aid)
            if aluno:
                try:
                    turma.alunos.remove(aluno)
                except ValueError:
                    pass
        # Add new selecionados
        for aid in selected_ids - current_ids:
            aluno = User.query.get(aid)
            if aluno and aluno.role == 'aluno':
                turma.alunos.append(aluno)
        turma.matriculados = turma.alunos.count() if hasattr(turma.alunos, 'count') else len(turma.alunos)
        db.session.commit()
        flash('Alunos atualizados na turma com sucesso.', 'success')
        return redirect(url_for('treinamento.listar_turmas', treinamento_id=turma.treinamento_id))

    alunos_vinculados = [a.id for a in turma.alunos]
    return render_template('treinamento/vincular_alunos.html', turma=turma, alunos=alunos, alunos_vinculados=alunos_vinculados)


@login_required
def criar_turma(treinamento_id):
    treinamento = Treinamento.query.get_or_404(treinamento_id)
    if current_user.role != 'coordenador':
        abort(403)

    if request.method == 'POST':
        vagas = request.form.get('vagas')
        data_inicio_str = request.form.get('data_inicio')
        try:
            vagas_int = int(vagas) if vagas else 0
        except ValueError:
            flash('Vagas precisa ser um número inteiro.', 'danger')
            return render_template('treinamento/novo_turma.html', treinamento=treinamento)

        turma = Turma(treinamento_id=treinamento.id, vagas=vagas_int)
        if data_inicio_str:
            try:
                turma.data_inicio = datetime.fromisoformat(data_inicio_str)
            except ValueError:
                flash('Formato de data inválido para a turma.', 'danger')
                return render_template('treinamento/novo_turma.html', treinamento=treinamento)

        db.session.add(turma)
        db.session.commit()
        flash('Turma criada com sucesso!', 'success')
        return redirect(url_for('treinamento.listar_turmas', treinamento_id=treinamento.id))

    return render_template('treinamento/novo_turma.html', treinamento=treinamento)