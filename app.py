from flask import Flask, render_template

app = Flask(__name__)

olives_stock = 500  # Quantità di olive in stock

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html', stock=olives_stock)

if __name__ == '__main__':
    app.run(debug=True)
