from flask import Blueprint, app, request, jsonify #request permite acessar os dados que o cliente enviou e jssonify tranforma
#dicionários python em respostas JSNON bonitinhas
from meals.models import Meal 
from core.database import db
from datetime import datetime

meals_bp = Blueprint('meals', __name__, url_prefix='/api/meals')

@meals_bp.route('/add', methods=['POST'])
def add_meal():

    data = request.json #Pega o corpo da requisição (que deve vir em formato JSON) e transforma em dicionário Python.

    #Aqui vou validar os campos obrigatórios

    required_fields = ["name", "category", "calories", "is_on_diet"]
    for field in required_fields:
        if field not in data:
            #Se algum não estiver no dicionário data → retorna erro 400 (Bad Request) com mensagem clara.
            return jsonify({"message": f"'{field}' é obrigatório"}), 400
    
    #Criando a refeição
    meal = Meal(
        name=data["name"],
        description=data.get("description"),
        category=data["category"],
        calories=data["calories"],
        is_on_diet=data["is_on_diet"],
        date=datetime.strptime(data.get("date"), "%Y-%m-%d") if data.get("date") else datetime.utcnow(),
        time=datetime.strptime(data.get("time"), "%H:%M").time() if data.get("time") else None
    )

    # Salvando no banco
    db.session.add(meal)
    db.session.commit()
    return jsonify({"message": "Refeição adicionada com sucesso!", "meal": {
        "id": meal.id,
        "name": meal.name,
        "category": meal.category,
        "calories": meal.calories,
        "is_on_diet": meal.is_on_diet,
        "date": meal.date.isoformat(),
        "time": meal.time.isoformat() if meal.time else None
    }}), 201

@meals_bp.route('/update/<int:meal_id>', methods=["PUT"])
def update_meal(meal_id):
    """
    Atualiza uma refeição existente pelo ID.
    Apenas os campos enviados no JSON serão alterados.
    """
    #1. Busca a refeição no banco ou retorna 404 automaticamente se não existir
    meal = Meal.query.get_or_404(meal_id)

    #2. Pega o JSON enviado no corpo de requisição
    data = request.get_json()

    #3. se não enviou nada útil - erro claro
    if not data or not isinstance(data, dict): #válida se tem um dado ou se não é uma string
        return jsonify({"message": "Envie um JSON válido com os campos a atualizar!"}),400
    
    #4. Atulização condicional - olha campo por campo e muda SÓ se veio no JSON
    updated= False #Vamos usar para saber se algo mudou de verdade 

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():# Isso verifica se a string depois de tirar os espaços fica vazia.
            return jsonify({"message": "O campo 'name' deve ser estar preenchido!"}), 400
        meal.name = data["name"].strip() #Salva o nome limpo, sem espaços desnecessários nas pontas.
        updated = True
    

    if "description" in data:
        meal.description = data["description"].strip() if data["description"] else None
        updated = True

    if "category" in data: #Vê se o usuario mandou o campo category, se sim entra no bloco e se não pula para o próximo campo
        if not isinstance(data["category"], str) or not data ["category"].strip(): #Duas verificações juntas com or (se qualquer uma for verdadeira → erro)
            return jsonify({"message": "O campo 'category' não pode estar vazio!"}),400
        meal.category = data["category"].strip() #→ Se passou nas validações → pega o valor, tira espaços das pontas e salva no objeto meal.
        updated = True

    if "calories" in data:
        try:
            calories = float(data["calories"]) #→ Converte o valor para número decimal (float).
            if calories < 0:
                return jsonify({"message": "Calorias não podem ser negativas!"}), 400
            meal.calories = calories
            updated = True
        except (ValueError, TypeError):
            return jsonify({"message": "O campo 'calories' deve ser um número (ex: 350.5 ou 400)"}), 400
        
    if "is_on_diet" in data:
        if isinstance(data["is_on_diet"], str): #→ Se for texto (string) → trata de forma flexível
            meal.is_on_diet=data["is_on_diet"].lower() in ("true", "1", "sim", "yes", "verdadeiro") #Converte para minúsculo e verifica se é uma das palavras que significam "sim"
        else:
            meal.is_on_diet = bool(data["is_on_diet"])
        updated = True

    if "date" in data:
        try:
            meal.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
            updated = True
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD (ex: 2026-01-29)"}), 400
    
    if "time" in data:
        if data["time"] in (None, "", "null"):
            meal.time = None
        else:
            try:
                meal.time = datetime.strptime(data["time"], "%H:%M").time()
            except ValueError:
                return jsonify({"message": "Formato de hora inválido. Use HH:MM (ex: 12:30) ou deixe vazio"}), 400
        updated = True

    if not updated:
        # Retorna aviso se nenhum campo foi alterado de verdade
        return jsonify({
            "message": "Nenhum campo válido foi enviado para atualizar",
            "current_meal": {
                "id": meal.id,
                "name": meal.name,
                "description": meal.description,
                "category": meal.category,
                "calories": meal.calories,
                "is_on_diet": meal.is_on_diet,
                "date": meal.date.isoformat() if meal.date else None,
                "time": meal.time.isoformat() if meal.time else None,
                "is_favorite": meal.is_favorite
            }  # ← chave do current_meal fechada aqui
        }), 200  # ← parênteses do jsonify fechados aqui

    # Se chegou aqui é porque algo foi atualizado
    db.session.commit()

    return jsonify({
        "message": "Refeição atualizada com sucesso!",
        "updated_meal": {
            "id": meal.id,
            "name": meal.name,
            "description": meal.description,
            "category": meal.category,
            "calories": meal.calories,
            "is_on_diet": meal.is_on_diet,
            "date": meal.date.isoformat() if meal.date else None,
            "time": meal.time.isoformat() if meal.time else None
        }  
    }), 200  
        
@meals_bp.route('/delete/<int:meal_id>', methods= ["DELETE"])
def delete_meal(meal_id):
    #1. Busca a refeição pelo ID
    # Se não existir - já devolve 404 automaticamente
    meal = Meal.query.get_or_404(meal_id)

    #2. Remove do banco (maraca para delete)
    db.session.delete(meal)

    #3.Confirma a exclusão
    db.session.commit()

    #4. Retorna a reposta de sucesso
    return jsonify({
        "message": f"Refeição '{meal.name}' (ID {meal_id}) excluída com sucesso!"
    }), 200

@meals_bp.route('/', methods=["GET"])
def get_meals():
    #começa com a query base: todas as refeições
    query = Meal.query

    # Filtro por categoria (parcial, ignora maiúsculas/minúsculas)
    category = request.args.get('category')
    if category:
        query = query.filter(Meal.category.ilike(f"%{category}"))                            

    is_on_diet_str = request.args.get('is_on_diet')
    if is_on_diet_str is not None: #  Só entra se o parâmetro foi enviado (mesmo que seja "false")
        #Converte string para booleano de forma flexível 
        is_on_diet = is_on_diet_str.lower() in ('true', '1', 'sim', 'yes')
        query = query.filter(Meal.is_on_diet == is_on_diet) #Adiciona filtro: só refeições que têm is_on_diet igual ao valor calculado.

# Filtro por período de data (start_date e end_date)
    start_date_str = request.args.get('start_date') #Pega start_date=2026-02-01 → "2026-02-01"
    if start_date_str: #Se veio valor → tenta converter.
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() #Converte string "2026-02-01" em objeto data (date).
            query = query.filter(Meal.date >= start_date) #Só refeições a partir dessa data (inclusive).
        except ValueError:
            return jsonify({"message": "Formato inválido para start_date. Use YYYY-MM-DD"}), 400

    end_date_str = request.args.get('end_date')
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(Meal.date <= end_date)
        except ValueError:
            return jsonify({"message": "Formato inválido para end_date. Use YYYY-MM-DD"}), 400
        
# Executa a query e pega os resultados
    meals = query.all()

    # Se não encontrou nada Se a lista veio vazia (nenhuma refeição atendeu os filtros).
    if not meals:
        return jsonify({
            "message": "Nenhuma refeição encontrada com os filtros aplicados",
            "meals": [],
            "total": 0
        }), 200

    # Converte para lista de dicionários
    meals_list = []
    for meal in meals: #Percorre cada refeição encontrada.
        meals_list.append({
            "id": meal.id,
            "name": meal.name,
            "description": meal.description,
            "category": meal.category,
            "calories": meal.calories,
            "is_on_diet": meal.is_on_diet,
            "date": meal.date.isoformat() if meal.date else None,
            "time": meal.time.isoformat() if meal.time else None,
            "is_favorite": meal.is_favorite
        })

    return jsonify({
        "message": "Refeições encontradas",
        "total": len(meals_list),
        "meals": meals_list
    }), 200

@meals_bp.route('/<int:meal_id>', methods=['GET'])
def get_single_meal(meal_id):
    # Busca a refeição pelo ID ou já retorna 404 automaticamente
    meal = Meal.query.get_or_404(meal_id)
    
    # Monta o dicionário da refeição 
    meal_data = {
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "category": meal.category,
        "calories": meal.calories,
        "is_on_diet": meal.is_on_diet,
        "date": meal.date.isoformat() if meal.date else None,
        "time": meal.time.isoformat() if meal.time else None,
        "is_favorite": meal.is_favorite
    }
    
    return jsonify({
        "message": "Refeição encontrada",
        "meal": meal_data
    }), 200


@meals_bp.route('/<int:meal_id>/favorite', methods=["PATCH"])
def toggle_favorite(meal_id):
    #Busca a refeição ou devolve 404 se não existir
    meal = Meal.query.get_or_404(meal_id)

    # Pega o JSON enviado (esperamos algo como {"is_fvaorite": true} ou false)
    data = request.get_json()

    # Se não enviou o JSON ou não tem o campo is_favorite
    if not data or "is_favorite" not in data: # Verifica duas coisas: se não veio json nenhum ou inválido e se veio json, mas não tem o campo "is_favorite"
        return jsonify({
            "message": "Envie um JSON com o campo 'is_favorite' (true ou false)"
        }), 400
    
    # Valida que é o booleano
    new_favorite = data["is_favorite"]
    if not isinstance(new_favorite, bool):
        return jsonify({
            "message": "O campo 'is_favorite' deve ser booleano (true ou false)"
        }), 400
    
    # Muda o valor
    meal.is_favorite = new_favorite

    # Salva no banco
    db.session.commit()

    # Mensagem com o estado atual 
    action = "favoritada" if new_favorite else "desfavoritada"
    
    return jsonify({
        "message": f"Refeição '{meal.name}' {action} com sucesso!",
        "meal_id": meal.id,
        "is_favorite": meal.is_favorite
    }), 200

@meals_bp.route('/report', methods=['GET'])
def meals_report():
    # Pega todas as refeições (pode adicionar filtros depois se quiser)
    all_meals = Meal.query.all() #Busca todas as refeições no banco de dados
    
    if not all_meals: #verifica se a lista está vazia (nenhuma refeição cadastrada ainda)
        return jsonify({
            "message": "Nenhuma refeição cadastrada ainda",
            "report": {
                "total_meals": 0,
                "total_calories": 0,
                "on_diet_count": 0,
                "on_diet_percentage": 0,
                "favorite_count": 0
            }
        }), 200
    
    # Calcula os valores

    total_meals = len(all_meals) #Conta quantas refeições tem no total (tamanho da lista)
    total_calories = sum(meal.calories for meal in all_meals) #soma as calorias de todas as refeições (é um loop interno, para cada refeição pega meal.calories e soma tudo)
    on_diet_count = sum(1 for meal in all_meals if meal.is_on_diet) #conta quantas refeições tem que está dentro da dieta
    favorite_count = sum(1 for meal in all_meals if meal.is_favorite)
    
    # Percentual de refeições dentro da dieta (evita divisão por zero)
    on_diet_percentage = (on_diet_count / total_meals * 100) if total_meals > 0 else 0 #Calcula o percentual de refeições na dieta
    
    return jsonify({
        "message": "Relatório gerado com sucesso",
        "report": {
            "total_meals": total_meals,
            "total_calories": total_calories,
            "on_diet_count": on_diet_count,
            "on_diet_percentage": round(on_diet_percentage, 1),  # 1 casa decimal
            "favorite_count": favorite_count,
            "average_calories_per_meal": round(total_calories / total_meals, 1) if total_meals > 0 else 0
        }
    }), 200
