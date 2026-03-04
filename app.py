from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>NS PureOil Production</h1><p>Sistema avviato!</p>'

if __name__ == '__main__':
    app.run(debug=True)
