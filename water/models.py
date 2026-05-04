from datetime import datetime
from core.database import db

class WaterIntake(db.Model): #uma classe == uma tabela
    __tablename__ = "water_intakes"

    id = db.Column(db.Integer, primary_key=True)
    amount_ml= db.Column(db.Integer, nullable=False) #quantidade ingerida em ml, obrigatório
    date = db.Column(db.Date, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow) #quando a água foi ingerida
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
