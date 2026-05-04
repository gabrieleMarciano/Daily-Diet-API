import os #acessar as variaveis do ambiente
from flask import Flask #cria a aplicação Flask
from dotenv import load_dotenv #carrega o env
from core.database import db #importa o OBJETO db
from meals.router import meals_bp
from water.router import water_bp
from goals.router import goals_bp

#Esse arquivo é criado porque ele é o ponto de partida da aplicação

def create_app(): #como criar o APP
    load_dotenv() #lê o env 

    app = Flask(__name__) #name == a main se for rodado diretamente
    # CADA PEDAÇO VEM DO ENV, isso permite  trocar o banco sem mexer no código
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app) #aqui o flask+banco de dados estão conectados

    app.register_blueprint(meals_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(goals_bp)

    # Rota de teste
    @app.route("/")
    def home():
        return "API está funcionando!"

    return app

#aqui a aplicação nasce
app = create_app()

#essa linha pergunta se o arquivo foi executado diretamente. Se sim, roda o servidor. Se não, não roda.
#Isso evita bugs quando outros arquivos importam o app
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000, debug=True) #liga o servidor, aceita conexês externas, porta padrão, recarrega automaticamente


