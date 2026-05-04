from flask_sqlalchemy import SQLAlchemy #importa o ORM, ele será um tradutor entre o python e o SQL (classes e tabelas)

db = SQLAlchemy() #criei uma instancia separada, isso permite o db em qualquer model e evita import em loop

