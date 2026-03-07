import random
from flask import Flask, render_template, redirect, url_for
from datetime import datetime
from models import db, Stock, Plantation, HarvestHistory

app = Flask(__name__)
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
    cost = 105
    if s.money >= cost:
        s.money -= cost
        s.olives_bought += 100
        db.session.commit()
    return redirect(url_for('status'))


@app.route('/produce_premium') # soltanto con le proprie olive
def produce_premium():
    s = Stock.query.first()
    if s.olives_own >= 100 and s.money >= 16.5:
        s.olives_own -= 100
        s.money -= 16.5
        s.oil_virgin += random.randint(14, 18) # Il nostro olio d'élite
        # Prendiamo random.randint(35, 50) kg di sansa per ogni 100 kg di olive.
        s.sansa += random.randint(35, 50)    # Sansa nel calderone generale
        s.total_time += 150 # Lavoro manuale più lungo
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        db.session.commit()
    return redirect(url_for('status'))

@app.route('/produce_evo')
def produce_evo():
    s = Stock.query.first()
    # Solo olive acquistate!
    if s.olives_bought >= 100 and s.money >= 16.5:
        s.olives_bought -= 100
        s.money -= 16.5
        s.oil_extra += random.randint(12, 16)
        s.sansa += random.randint(35, 50)  # Sansa nel calderone generale
        s.total_time += 120
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        db.session.commit()
    return redirect(url_for('status'))

@app.route('/sell')
def sell():
    s = Stock.query.first()
    # Calcoliamo il reddito
    # Premium (Virgin) * 25, Extra * 15, Sansa  * 0.20
    income_oil = (s.oil_extra * 15) + (s.oil_virgin * 25)
    income_sansa = (s.sansa * 0.20)
    
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
