from extensions import db
from datetime import date

# Tabela associativa Turma x Alunos
turma_alunos = db.Table(
    "turma_alunos",
    db.Column("turma_id", db.Integer, db.ForeignKey("turmas.id"), primary_key=True),
    # Users table is 'user' model -> FK to user.id
    db.Column("aluno_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)

class Turma(db.Model):
    __tablename__ = "turmas"
    id = db.Column(db.Integer, primary_key=True)
    treinamento_id = db.Column(db.Integer, db.ForeignKey("treinamentos.id"))
    vagas = db.Column(db.Integer, nullable=False)
    data_inicio = db.Column(db.Date, default=date.today)
    matriculados = db.Column(db.Integer, default=0)

    alunos = db.relationship(
        "User",
        secondary=turma_alunos,
        backref="turmas_inscrito",
        lazy="dynamic"
    )

    treinamento = db.relationship("Treinamento", backref="turmas")
