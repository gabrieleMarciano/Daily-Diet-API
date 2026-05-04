# API Diet - Gerenciador de Nutrição

Uma API completa em Flask para controle de alimentação, ingestão de água e metas nutricionais.

---

## 📋 Sobre o Projeto

A **API Diet** é um sistema backend desenvolvido para ajudar no acompanhamento nutricional diário. Permite registrar refeições, controlar o consumo de água, definir metas e visualizar relatórios e streaks de consistência.

Projeto desenvolvido como conclusão de curso de Python/Flask, com foco em boas práticas, organização modular e uso de Docker.

## ✨ Funcionalidades

### 🥗 Refeições (Meals)
- CRUD completo (Criar, Ler, Atualizar, Deletar)
- Filtros por categoria, status da dieta e período
- Marcar refeições como favoritas
- Relatório detalhado (calorias totais, percentual na dieta, média e favoritos)

### 💧 Ingestão de Água (WaterIntake)
- Registrar consumo de água
- Listar registros com filtros por data
- Visualizar total consumido e progresso em relação à meta

### 🎯 Metas Diárias (Goals)
- Criar e atualizar metas de calorias e água
- Definir período de vigência da meta
- Calcular streaks (dias consecutivos atingindo as metas)

## 🛠️ Tecnologias Utilizadas

- **Python** + **Flask**
- **SQLAlchemy** (ORM)
- **MySQL** (Banco de dados)
- **Docker** + **Docker Compose**
- **Flask-Migrate** (migrações)
- **dotenv** (variáveis de ambiente)

## 📁 Estrutura do Projeto

```bash
api_diet/
├── app.py                    # Configuração principal da aplicação
├── .env                      # Variáveis de ambiente
├── core/
│   └── database.py           # Configuração do banco
├── meals/
│   ├── models.py
│   └── routes.py
├── water/
│   ├── models.py
│   └── routes.py
├── goals/
│   ├── models.py
│   └── routes.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

#  Como Executar o Projeto

## 1. Clone o repositório

```bash
git clone [https://github.com/SEU_USUARIO/api-diet.git](https://github.com/SEU_USUARIO/api-diet.git)
cd api-diet
```

## 2. Configure o arquivo `.env`

## Crie um arquivo `.env` na raiz do projeto:

```env
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=db
## DB_PORT=3306
DB_NAME=api_diet
FLASK_ENV=development
```

## 3. Suba os containers Docker

```bash
docker-compose up --build -d
```

## 4. Execute as migrações do banco

```bash
docker-compose exec web flask db upgrade
```

## A API estará rodando em:
[http://localhost:5000](http://localhost:5000)

---

#  Principais Endpoints

## 🍽️ Meals

| Método | Endpoint                   | Descrição              |
| ------ | -------------------------- | ---------------------- |
| POST   | `/api/meals/add`           | Adicionar refeição     |
| GET    | `/api/meals`               | Listar com filtros     |
| GET    | `/api/meals/<id>`          | Buscar uma refeição    |
| PUT    | `/api/meals/update/<id>`   | Atualizar refeição     |
| DELETE | `/api/meals/delete/<id>`   | Excluir refeição       |
| PATCH  | `/api/meals/<id>/favorite` | Favoritar/Desfavoritar |
| GET    | `/api/meals/report`        | Relatório geral        |

---

## 💧 Water Intake

| Método | Endpoint                 | Descrição                  |
| ------ | ------------------------ | -------------------------- |
| POST   | `/api/water/add`         | Registrar ingestão de água |
| GET    | `/api/water`             | Listar ingestões           |
| GET    | `/api/water/total`       | Total + progresso          |
| DELETE | `/api/water/delete/<id>` | Excluir registro           |

---

## 🎯 Goals

| Método | Endpoint             | Descrição                  |
| ------ | -------------------- | -------------------------- |
| POST   | `/api/goals`         | Criar meta                 |
| PUT    | `/api/goals/<id>`    | Atualizar meta             |
| GET    | `/api/goals/streaks` | Streaks de calorias e água |

---

# 📝 Exemplos de Requisições

## 1. Adicionar Refeição

```json
{
"name": "Frango grelhado com arroz integral",
"category": "almoço",
"calories": 480,
"is_on_diet": true,
"date": "2026-02-05",
"time": "12:30"
}
```

## 2. Registrar Água

```json
{
"amount_ml": 500,
"date": "2026-02-05",
"time": "14:00"
}
```

## 3. Criar Meta

```json
{
"calories_goal": 1800,
"water_goal_ml": 2500,
"start_date": "2026-02-05",
"end_date": "2026-02-11"
}
```

---

# ✨ Autor

Feito por **Gabriele**
Projeto final do curso de Python/Flask
