import random
from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
from models import db, Stock, Plantation, HarvestHistory, User  
from services.oil_logic import calculate_yield, get_random_harvest
from utils.validators import (
    can_afford, has_resources, 
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH,
    PRICE_VIRGIN, PRICE_EVO, PRICE_SANSA
)
from flask_login import (LoginManager, UserMixin,
     login_user, login_required, 
    logout_user, current_user)

app = Flask(__name__)

login_manager = LoginManager() # inizializziamo il login manager
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configurazione del database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'la-mia-chiave-segreta-123' 

db.init_app(app)

with app.app_context():
    db.create_all()
    # Inizializzazione dati magazzino 
    if not Stock.query.first():
        db.session.add(Stock())
    # Inizializzazione piantagione
    if not Plantation.query.first():
        db.session.add(Plantation())
    
    # creare admin
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='123', role='admin')
        db.session.add(admin)
        print("--- User admin created! ---")
        
    db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('status'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        
        if user and user.password == password:
            login_user(user)
            flash(f"Benvenuto, {user.username}!", "success")
            return redirect(url_for('status'))
        else:
            
            flash("Nome utente o password non validi", "danger")
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/status')
@login_required # Solo utenti loggati possono vedere lo status
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
@login_required # Solo utenti loggati possono comprare
def buy():
    s = Stock.query.first()
    
    if can_afford(s.money, COST_BUY_OLIVES):
        s.money -= COST_BUY_OLIVES
        s.olives_bought += 100
        db.session.commit()
    return redirect(url_for('status'))


@app.route('/produce_virgin')
@login_required # Solo utenti loggati possono produrre
def produce_virgin():
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

        # la storia del raccolto
        new_event = HarvestHistory(
            date=datetime.now().strftime('%d.%m.%Y'),
            olive_type="Vergine (Propria)",
            quantity=batch_size,
            oil_produced=oil
        )
        db.session.add(new_event)
        db.session.commit()
    return redirect(url_for('status'))

@app.route('/produce_evo')
@login_required # Solo utenti loggati possono produrre
def produce_evo():
    s = Stock.query.first()
    batch_size = 100
    
    # 1. Utilizzo di validatori e costanti da utils  
    if has_resources(s.olives_bought, batch_size) and can_afford(s.money, COST_PRODUCTION_BATCH):
        # 2. Calcolo della resa petrolifera utilizzando la logica nei servizi
        oil, sansa = calculate_yield("evo", batch_size)
        
        # 3. Aggiornamento del magazzino e del denaro
        s.olives_bought -= batch_size
        s.money -= COST_PRODUCTION_BATCH
        s.oil_extra += oil
        s.sansa += sansa
        s.total_time += 120
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        # 4. salviamo nella storia
        new_event = HarvestHistory(
            date=datetime.now().strftime('%d.%m.%Y'),
            olive_type="EVO (Purchased)",
            quantity=batch_size,
            oil_produced=oil
        )
        db.session.add(new_event)
        db.session.commit()
        
    return redirect(url_for('status'))

@app.route('/sell')
@login_required # Solo utenti loggati possono vendere
def sell():
    s = Stock.query.first()
    # calcogliamo con constanti da utils
    income_oil = (s.oil_extra * PRICE_EVO) + (s.oil_virgin * PRICE_VIRGIN)
    income_sansa = (s.sansa * PRICE_SANSA)
    
    total_income = income_oil + income_sansa
    if total_income > 0:
        s.money += total_income
        s.oil_extra = 0
        s.oil_virgin = 0
        s.sansa = 0
        db.session.commit()
    return redirect(url_for('status'))

@app.route('/next_month')
@login_required
def next_month():
    p = Plantation.query.first()
    s = Stock.query.first()
    
    # 1. Aumentiamo il mese
    p.current_month += 1
    if p.current_month > 12:
        p.current_month = 1 # Torna a gennaio
        
    # 2. Logica di raccolta (Novembre = 11)
    if p.current_month == 11:
        new_olives = get_random_harvest(p.size_hectares)
        s.olives_own += new_olives
        flash(f"È novembre! Raccolti {new_olives} kg di olive proprie!", "success")
    
    # 3. Spese mensili (irrigazione)
    s.money -= p.irrigation_cost
    
    db.session.commit()
    return redirect(url_for('status'))       
    


if __name__ == '__main__':
    app.run(debug=True)
