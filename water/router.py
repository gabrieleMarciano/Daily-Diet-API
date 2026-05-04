from flask import Blueprint, request, jsonify
from .models import WaterIntake  # ajuste o caminho se necessário
from core.database import db
from datetime import datetime

water_bp = Blueprint('water', __name__, url_prefix='/api/water')

@water_bp.route('/add', methods=['POST'])
def add_water_intake():
    data = request.get_json() # pega o corpo da requisição e transforma em dicionário
    
    # Validação básica
    if not data or "amount_ml" not in data: #verifica se o json é válido e se tem o campo  oobrigatório 
        return jsonify({"message": "O campo 'amount_ml' é obrigatório"}), 400
    
    try: #bloco que tenta converter o valor, mas pode dar erro
        amount_ml = int(data["amount_ml"])
        if amount_ml <= 0: #quantidade não pode ser zero ou negativa (não faz sentido ingerir água negativa).
            return jsonify({"message": "A quantidade deve ser maior que 0 ml"}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "'amount_ml' deve ser um número inteiro positivo"}), 400
    
    # Data e hora: se não vier, usa o momento atual
    intake_date = datetime.utcnow().date()  # só a data
    intake_time = datetime.utcnow().time()  # só a hora
    
    if "date" in data: #Se o usuário mandou "date" no JSON → usa esse valor.
        try:
            intake_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if "time" in data:
        try:
            intake_time = datetime.strptime(data["time"], "%H:%M").time()
        except ValueError:
            return jsonify({"message": "Formato de hora inválido. Use HH:MM"}), 400
    
    # Cria o registro
    water = WaterIntake(
        amount_ml=amount_ml,
        date=intake_date,  # aqui vai a data (sem hora)
        created_at=datetime.combine(intake_date, intake_time)  # combina data + hora para created_at
    )
    
    db.session.add(water)
    db.session.commit()
    
    return jsonify({
        "message": "Ingestão de água registrada com sucesso!",
        "water_intake": {
            "id": water.id,
            "amount_ml": water.amount_ml,
            "date": water.date.isoformat(),
            "created_at": water.created_at.isoformat()
        }
    }), 201

@water_bp.route('/delete/<int:water_id>', methods=['DELETE'])
def delete_water_intake(water_id):
    # Busca o registro pelo ID
    # Se não existir → já retorna 404 automaticamente
    water = WaterIntake.query.get_or_404(water_id)
    
    # Remove o registro
    db.session.delete(water)
    
    # Confirma a exclusão no banco
    db.session.commit()
    
    # Retorna mensagem de sucesso
    return jsonify({
        "message": f"Ingestão de água (ID {water_id}) excluída com sucesso!",
        "amount_ml": water.amount_ml,  # mostra quanto foi excluído
        "date": water.date.isoformat()
    })

@water_bp.route('/', methods=['GET'])
def get_water_intakes():
    # Query base: todas as ingestões
    query = WaterIntake.query.order_by(WaterIntake.created_at.desc())  # ordena do mais recente pro mais antigo

    # Filtro por período (start_date e end_date)
    start_date_str = request.args.get('start_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            query = query.filter(WaterIntake.date >= start_date)
        except ValueError:
            return jsonify({"message": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    end_date_str = request.args.get('end_date')
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(WaterIntake.date <= end_date)
        except ValueError:
            return jsonify({"message": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400

    # Filtro opcional por quantidade mínima (ex: ?min_amount=500)
    min_amount_str = request.args.get('min_amount')
    if min_amount_str:
        try:
            min_amount = int(min_amount_str)
            query = query.filter(WaterIntake.amount_ml >= min_amount)
        except ValueError:
            return jsonify({"message": "min_amount deve ser número inteiro"}), 400

    # Executa a query
    intakes = query.all()

    if not intakes:
        return jsonify({
            "message": "Nenhuma ingestão de água encontrada com os filtros aplicados",
            "intakes": [],
            "total": 0
        }), 200

    # Monta a lista de dicionários
    intakes_list = []
    for intake in intakes:
        intakes_list.append({
            "id": intake.id,
            "amount_ml": intake.amount_ml,
            "date": intake.date.isoformat(),
            "created_at": intake.created_at.isoformat(),
            "updated_at": intake.updated_at.isoformat() if intake.updated_at else None
        })

    return jsonify({
        "message": "Ingestões de água encontradas",
        "total": len(intakes_list),
        "total_ml": sum(i["amount_ml"] for i in intakes_list),  # soma rápida do total
        "intakes": intakes_list
    }), 200

@water_bp.route('/total', methods=['GET'])
def get_water_total():   
    # Meta diária de água (em ml) - por enquanto fixa, depois vem do banco
    DAILY_WATER_GOAL = 2000  # 2 litros = 2000 ml

    # Começa com a query base
    query = WaterIntake.query

    # Filtro por período (igual ao GET anterior)
    start_date_str = request.args.get('start_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            query = query.filter(WaterIntake.date >= start_date)
        except ValueError:
            return jsonify({"message": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    end_date_str = request.args.get('end_date')
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(WaterIntake.date <= end_date)
        except ValueError:
            return jsonify({"message": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400

    # Executa a query
    intakes = query.all()

    # Calcula o total consumido no período
    total_ml = sum(intake.amount_ml for intake in intakes)

    # Número de dias únicos no período (para calcular média diária)
    unique_dates = set(intake.date for intake in intakes)
    num_days = len(unique_dates) if unique_dates else 1  # evita divisão por zero

    # Progresso em relação à meta (para o período inteiro)
    goal_for_period = DAILY_WATER_GOAL * num_days
    progress_percentage = (total_ml / goal_for_period * 100) if goal_for_period > 0 else 0

    return jsonify({
        "message": "Total de água consumida calculado com sucesso",
        "period": {
            "start_date": start_date_str or "início dos registros",
            "end_date": end_date_str or "hoje",
            "days_covered": num_days
        },
        "total_ml": total_ml,
        "total_litros": round(total_ml / 1000, 2),
        "average_ml_per_day": round(total_ml / num_days, 1) if num_days > 0 else 0,
        "goal_for_period_ml": goal_for_period,
        "progress_percentage": round(progress_percentage, 1),
        "goal_daily_ml": DAILY_WATER_GOAL,
        "intakes_count": len(intakes)
    }), 200