from flask import Flask

app = Flask(__name__)

olives_stock = 500  # Quantità di olive in stock

@app.route('/')
def home():
    return '<h1>NS PureOil Production</h1><p>Sistema avviato!</p><a href="/status">Controlla lo stock</a>'

@app.route('/status')
def status():
    return f'''<h1>Stock di Olive</h1><p>Attualmente abbiamo {olives_stock} olive in stock.</p>
    <a href="/">Torna alla home</a>'''

if __name__ == '__main__':
    app.run(debug=True)
