import random
from flask import Flask, render_template, redirect, url_for
from datetime import datetime
from models import db, Stock

app = Flask(__name__)
# Configurazione del database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oil_factory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not Stock.query.first():
        db.session.add(Stock())
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    inventory = Stock.query.first()
    return render_template('status.html', inventory=inventory)

@app.route('/buy')
def buy():
    s = Stock.query.first()
    if s.money >= 105:
        s.money -= 105
        s.olives += 100
        db.session.commit()
    return redirect(url_for('status'))


@app.route('/produce')
def produce():
    # Recupera i dati attuali dal database
    s = Stock.query.first()
    # Verifica se ci sono abbastanza olive e denaro per produrre olio
    if s.olives >= 100 and s.money >= 16.5:
        # Sottrae le materie prime e il costo del servizio di molitura
        s.olives -= 100
        s.money -= 16.5
    # Generazione casuale della produzione (Requisito Traccia 15)
    # Calcola quantità variabili di olio EVO, olio vergine e sansa
        s.oil_extra += random.randint(10, 15)
        s.oil_virgin += random.randint(5, 8)
        s.sansa += random.randint(30, 45)
    # Calcolo del tempo di produzione complessivo    
        s.total_time += 120
    # Registra la data e l'ora dell'ultima operazione effettuata    
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    # Salva permanentemente tutte le modifiche nel database    
        db.session.commit()
    return redirect(url_for('status'))   

@app.route('/sell')
def sell():
    s = Stock.query.first()
    income = (s.oil_extra * 15) + (s.oil_virgin * 10)
    if income > 0:
        s.money += income
        s.oil_extra = 0
        s.oil_virgin = 0
        db.session.commit()
    return redirect(url_for('status'))



if __name__ == '__main__':
    app.run(debug=True)
