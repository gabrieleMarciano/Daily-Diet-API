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

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    # Busca a meta pelo ID ou retorna 404 automaticamente
    goal = Goal.query.get_or_404(goal_id)
    
    data = request.get_json()
    
    # Se não enviou nada para atualizar
    if not data:
        return jsonify({"message": "Envie pelo menos um campo para atualizar"}), 400
    
    updated = False
    
    # Atualiza calories_goal se veio no JSON
    if "calories_goal" in data:
        try:
            new_calories = int(data["calories_goal"])
            if new_calories <= 0:
                return jsonify({"message": "calories_goal deve ser maior que 0"}), 400
            goal.calories_goal = new_calories
            updated = True
        except (ValueError, TypeError):
            return jsonify({"message": "calories_goal deve ser número inteiro positivo"}), 400
    
    # Atualiza water_goal_ml se veio
    if "water_goal_ml" in data:
        try:
            new_water = int(data["water_goal_ml"])
            if new_water <= 0:
                return jsonify({"message": "water_goal_ml deve ser maior que 0"}), 400
            goal.water_goal_ml = new_water
            updated = True
        except (ValueError, TypeError):
            return jsonify({"message": "water_goal_ml deve ser número inteiro positivo"}), 400
    
    # Atualiza start_date se veio
    if "start_date" in data:
        try:
            new_start = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            goal.start_date = new_start
            updated = True
        except ValueError:
            return jsonify({"message": "Formato de start_date inválido. Use YYYY-MM-DD"}), 400
    
    # Atualiza end_date se veio
    if "end_date" in data:
        try:
            new_end = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            if new_end < goal.start_date:
                return jsonify({"message": "end_date não pode ser antes de start_date"}), 400
            goal.end_date = new_end
            updated = True
        except ValueError:
            return jsonify({"message": "Formato de end_date inválido. Use YYYY-MM-DD"}), 400
    
    # Se nada foi atualizado
    if not updated:
        return jsonify({
            "message": "Nenhum campo válido foi enviado para atualizar",
            "current_goal": {
                "id": goal.id,
                "calories_goal": goal.calories_goal,
                "water_goal_ml": goal.water_goal_ml,
                "start_date": goal.start_date.isoformat(),
                "end_date": goal.end_date.isoformat()
            }
        }), 200
    
    # Salva as alterações
    db.session.commit()
    
    return jsonify({
        "message": "Meta atualizada com sucesso",
        "updated_goal": {
            "id": goal.id,
            "calories_goal": goal.calories_goal,
            "water_goal_ml": goal.water_goal_ml,
            "start_date": goal.start_date.isoformat(),
            "end_date": goal.end_date.isoformat(),
            "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
        }
    }), 200