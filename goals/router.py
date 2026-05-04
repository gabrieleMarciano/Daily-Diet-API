from flask import Blueprint, request, jsonify
from goals.models import Goal
from core.database import db
from datetime import datetime

goals_bp = Blueprint('goals', __name__,url_prefix='/api/goals')

@goals_bp.route('/', methods=['POST'])
def create_goal():
    data = request.get_json()
    required_fields = ["calories_goal", "water_goal_ml"]

    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"O campo '{field}' é obrigatório"}), 400
    
    try:
        calories_goal = int(data["calories_goal"])
        water_goal_ml = int(data["water_goal_ml"])

        if calories_goal <= 0 or water_goal_ml <=0:
            return jsonify({"message": "Metas devem ser maiores que 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "calories_goal e water_goal_ml devem ser números inteiros positivos"}), 400
    
    # Datas (obrigatórias ou opcionais – aqui vamos exigir)
    if "start_date" not in data or "end_date" not in data:
        return jsonify({"message": "start_date e end_date são obrigatórios (YYYY-MM-DD)"}), 400
    
    try:
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            
            if end_date < start_date:
                return jsonify({"message": "end_date não pode ser antes de start_date"}), 400
    except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
        
    # Cria a nova meta
    goal = Goal(
        calories_goal=calories_goal,
        water_goal_ml=water_goal_ml,
        start_date=start_date,
        end_date=end_date
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({
        "message": "Meta diária criada com sucesso",
        "goal": {
            "id": goal.id,
            "calories_goal": goal.calories_goal,
            "water_goal_ml": goal.water_goal_ml,
            "start_date": goal.start_date.isoformat(),
            "end_date": goal.end_date.isoformat(),
            "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
        }
    }), 201
