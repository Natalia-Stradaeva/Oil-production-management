from flask import Flask, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)

olives_stock = {'olives': 500,'oil':0,'money':1000,'last_production':None}  # Inventario del magazzino (materie prime, prodotti, denaro)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html', inventory=olives_stock)

@app.route('/buy')
def buy():
 if olives_stock['money'] >= 105:
    olives_stock['money'] -= 105
    olives_stock['olives'] += 100
 return redirect(url_for('status'))


@app.route('/produce')
def produce():
    cost_molitura = 16.5
    if olives_stock['olives'] >= 100 and olives_stock['money'] >= cost_molitura:
        olives_stock['olives'] -= 100
        olives_stock['money'] -= cost_molitura
        olives_stock['oil'] += 20
        olives_stock['last_production'] = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    return redirect(url_for('status'))

@app.route('/sell')
def sell():
# Vendiamo tutto l'olio accumulato
 if olives_stock['oil'] > 0:
    price_per_liter = 12  # Prezzo per litro di olio
    income = olives_stock['oil'] * price_per_liter
    olives_stock['money'] += income
    olives_stock['oil'] = 0  # Lo stock di olio si svuota
 return redirect(url_for('status'))



if __name__ == '__main__':
    app.run(debug=True)
