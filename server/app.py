#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
from flask_cors import CORS
import os

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database migration
migrate = Migrate(app, db)
db.init_app(app)

# Home route
@app.route('/')
def index():
    return '<h1>Welcome to the Code Challenge API</h1>'

# Heroes route - handles GET and POST requests
@app.route('/heroes', methods=['GET', 'POST'])
def heroes():
    if request.method == 'GET':
        # Retrieve all heroes from the database  
        heroes_list = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in Hero.query.all()]
        return make_response(heroes_list, 200)
    
    if request.method == 'POST':
        # Create a new hero and insert it into the database
        data = request.get_json()
        new_hero = Hero(name=data['name'], super_name=data['super_name'])
        db.session.add(new_hero)
        db.session.commit()
        return make_response({"message": "Hero created successfully", "hero": new_hero.to_dict()}, 201)

# Hero by ID route - handles GET and PATCH requests
@app.route('/heroes/<int:id>', methods=['GET', 'PATCH'])
def hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return make_response({"error": "Hero not found"}, 404)
    
    if request.method == 'GET':
        # Retrieve a single hero by ID
        hero_powers = [hp.to_dict() for hp in hero.hero_powers]
        return make_response({
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'hero_powers': hero_powers
        }, 200)
    
    if request.method == 'PATCH':
        # Update some fields of the hero
        data = request.get_json()
        for key, value in data.items():
            setattr(hero, key, value)
        
        db.session.commit()
        return make_response(hero.to_dict(), 200)

# Powers route - handles GET and POST requests
@app.route('/powers', methods=['GET', 'POST'])
def powers():
    if request.method == 'GET':
        # Retrieve all powers from the database  
        powers_list = [power.to_dict(only=('description', 'id', 'name')) for power in Power.query.all()]
        return make_response(powers_list, 200)
    
    if request.method == 'POST':
        # Create a new power and insert it into the database
        data = request.get_json()
        
        # Validate description length before creating a new power
        if len(data['description']) < 20:
            return make_response({"errors": ["validation errors"]}, 400)

        new_power = Power(name=data['name'], description=data['description'])
        db.session.add(new_power)
        db.session.commit()
        return make_response({"message": "Power created successfully", "power": new_power.to_dict()}, 201)

# Power by ID route - handles GET and PATCH requests
@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power(id):
    power = Power.query.get(id)
    if not power:
        return make_response({"error": "Power not found"}, 404)
    
    if request.method == 'GET':
        # Retrieve a single power by ID
        return make_response(power.to_dict(only=('description', 'id', 'name')), 200)

    if request.method == 'PATCH':
        # Update some fields of the power
        data = request.get_json()
        
        if 'description' in data:
            desc = data['description']
            if not isinstance(desc, str) or len(desc) < 20:
                return make_response({"errors": ["validation errors"]}, 400)

            power.description = desc
        
        db.session.commit()
        return make_response(power.to_dict(), 200)

# Hero Powers route - handles POST requests only
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    strength = request.json.get('strength')
    power_id = request.json.get('power_id')
    hero_id = request.json.get('hero_id')  


    available_strengths = {'Strong', 'Weak', 'Average'}
    if strength not in available_strengths:
        return make_response({"errors": ["validation errors"]}, 400)

    hero_power = HeroPower(
        strength=strength,
        hero_id=hero_id,
        power_id=power_id
    )

    db.session.add(hero_power)
    db.session.commit() 

    
    # Ensure this returns status code 200
    return make_response(hero_power.to_dict(), 200)  # Change from 200 to 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)