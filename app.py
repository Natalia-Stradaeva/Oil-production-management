import random
from flask import Flask, render_template, redirect, url_for
from datetime import datetime
from models import db, Stock, Plantation, HarvestHistory
from services.oil_logic import calculate_yield
from utils.validators import (
    can_afford, has_resources, 
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH,
    PRICE_VIRGIN, PRICE_EXTRA, PRICE_SANSA
)
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

login_manager = LoginManager() # inizializziamo il login manager
login_manager.init_app(app)
login_manager.login_view = 'login' 

# Configurazione del database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not Stock.query.first():
        db.session.add(Stock())
    if not Plantation.query.first():
        db.session.add(Plantation())
    db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    # prendiamo dati da tutte e tre le tabelle per la visualizzazione
    inventory = Stock.query.first()
    factory_land = Plantation.query.first()
    history = HarvestHistory.query.all() # Elenco di tutti i passati raccolti
    
    # Trasmettiamo tutto questo in HTML
    return render_template('status.html', 
                           inventory=inventory, 
                           land=factory_land, 
                           history=history)

@app.route('/buy')
def buy():
    s = Stock.query.first()
    
    if can_afford(s.money, COST_BUY_OLIVES):
        s.money -= COST_BUY_OLIVES
        s.olives_bought += 100
        db.session.commit()
    return redirect(url_for('status'))


@app.route('/produce_premium')
def produce_premium():
    s = Stock.query.first()
    batch_size = 100
    if has_resources(s.olives_own, batch_size) and can_afford(s.money, COST_PRODUCTION_BATCH):
        oil, sansa = calculate_yield("premium", batch_size)
        
        s.olives_own -= batch_size
        s.money -= COST_PRODUCTION_BATCH
        s.oil_virgin += oil
        s.sansa += sansa
        s.total_time += 150
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        # --- ДОБАВЛЯЕМ ЗАПИСЬ В ИСТОРИЮ ---
        new_event = HarvestHistory(
            date=datetime.now().strftime('%d.%m.%Y'),
            olive_type="Premium (Own)",
            quantity=batch_size,
            oil_produced=oil
        )
        db.session.add(new_event)
        # ----------------------------------
        
        db.session.commit()
    return redirect(url_for('status'))

@app.route('/produce_evo')
def produce_evo():
    s = Stock.query.first()
    batch_size = 100
    
    # 1. Используем красивые валидаторы и константы из utils
    if has_resources(s.olives_bought, batch_size) and can_afford(s.money, COST_PRODUCTION_BATCH):
        # 2. Рассчитываем выход масла через логику в services
        oil, sansa = calculate_yield("evo", batch_size)
        
        # 3. Обновляем склад и деньги
        s.olives_bought -= batch_size
        s.money -= COST_PRODUCTION_BATCH
        s.oil_extra += oil
        s.sansa += sansa
        s.total_time += 120
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        # 4. СОХРАНЯЕМ В ИСТОРИЮ (Это топливо для твоих будущих графиков!)
        new_event = HarvestHistory(
            date=datetime.now().strftime('%d.%m.%Y'),
            olive_type="EVO (Purchased)",
            quantity=batch_size,
            oil_produced=oil
        )
        db.session.add(new_event)
        
        # 5. Фиксируем изменения в базе
        db.session.commit()
        
    return redirect(url_for('status'))

@app.route('/sell')
def sell():
    s = Stock.query.first()
    # Расчет через константы — теперь всё прозрачно!
    income_oil = (s.oil_extra * PRICE_EXTRA) + (s.oil_virgin * PRICE_VIRGIN)
    income_sansa = (s.sansa * PRICE_SANSA)
    
    total_income = income_oil + income_sansa
    if total_income > 0:
        s.money += total_income
        s.oil_extra = 0
        s.oil_virgin = 0
        s.sansa = 0
        db.session.commit()
    return redirect(url_for('status'))
        
    


if __name__ == '__main__':
    app.run(debug=True)
