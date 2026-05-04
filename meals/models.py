from datetime import datetime #importa a função de data e hora atual
from core.database import db

class Meal(db.Model): #classe python que representa uma tabela
    __tablename__ = "meals" #nome da tabela

    id = db.Column(db.Integer, primary_key=True) #coluna id, chave primária

    name = db.Column(db.String(100), nullable=False) #sem espaço vazio, evita dados inválidos e refeições sem nome
    description = db.Column(db.Text)

    category = db.Column(db.String(50)) #café, almoço ou jantar
    calories = db.Column(db.Integer, nullable=False) #base de tudo (metas), obrigatório

    is_on_diet = db.Column(db.Boolean, default=True) #dentro ou fora da dieta

    is_favorite = db.Column(db.Boolean, default=False) # marca favoritos
    
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    time = db.Column(db.Time, default=lambda: datetime.utcnow().time())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
