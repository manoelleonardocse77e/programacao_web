from app import app
from models.treinamento import Treinamento
from models.user import User

with app.app_context():
    print('Treinamentos:', Treinamento.query.count())
    print('Users:', User.query.count())
    print('Alunos:', User.query.filter_by(role='aluno').count())
