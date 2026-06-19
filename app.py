import random
from flask import Flask, render_template, redirect, url_for, jsonify, flash, request
from datetime import datetime
from models import db, Stock, Plantation, HarvestHistory, User, SalesHistory, ProductionLog  
from services.oil_logic import calculate_yield, get_random_harvest
from utils.validators import (
    can_afford, has_resources, 
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH,
    PRICE_VIRGIN, PRICE_EVO, PRICE_SANSA,
    COST_BOTTLE, COST_CORK,              
    COST_BAG, BAGS_PER_PACKAGE, PRODUCTION_CAPACITY, BATCH_SIZE, PACKAGING_BATCH_SIZE,     
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
    # Recuperiamo i dati da tutte le tabelle per la visualizzazione
    inventory = Stock.query.first()
    factory_land = Plantation.query.first()
    history = HarvestHistory.query.all() # Elenco di tutti i passati raccolti
    sales_history = SalesHistory.query.all() # Elenco di tutte le vendite
    production_logs = ProductionLog.query.all() 
    # Trasmettiamo tutto questo in HTML
    return render_template('status.html', 
                           inventory=inventory, 
                           land=factory_land, 
                           history=history,
                           sales_history=sales_history,
                           production_logs=production_logs)


@app.route('/buy', methods=['POST'])
@login_required # Solo utenti loggati possono comprare
def buy():
    s = Stock.query.first()
    if can_afford(s.money, COST_BUY_OLIVES):
        s.money -= COST_BUY_OLIVES
        s.olives_bought += 100
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Acquistati 100 kg di olive!'})
    else:
        return jsonify({'status': 'error', 'message': 'Soldi insufficienti!'}), 400
    


@app.route('/produce_virgin', methods=['POST'])
@login_required 
def produce_virgin():
    # Recuperiamo il record dello stock dal database
    s = Stock.query.first()
    
    # Verifichiamo se le risorse (olive proprie) e il budget sono sufficienti
    res = has_resources(s.olives_own, BATCH_SIZE) 
    afford = can_afford(s.money, COST_PRODUCTION_BATCH)
    
    # Se le risorse mancano, blocchiamo l'esecuzione e restituiamo un errore
    if not res or not afford:
        return jsonify({'status': 'error', 'message': 'Risorse o soldi insufficienti!'}), 400
    
    # Calcoliamo i risultati della spremitura (olio, sansa, tempo)
    risultati = calculate_yield("premium", BATCH_SIZE, PRODUCTION_CAPACITY)
    
    # Assegniamo i valori estratti alle variabili locali
    oil = risultati["oil"]
    sansa = risultati["sansa"]
    process_time = risultati["time"]
    
    # Aggiorniamo i dati dello stock nel magazzino
    s.olives_own -= BATCH_SIZE
    s.money -= COST_PRODUCTION_BATCH
    s.oil_virgin += oil
    s.sansa += sansa
    s.total_time += process_time
    
    # Registriamo l'evento nella cronologia del raccolto (HarvestHistory)
    new_event = HarvestHistory(
        date=datetime.now().strftime('%d.%m.%Y'),
        olive_type="Vergine (Propria)",
        quantity=BATCH_SIZE,
        oil_produced=oil,
        sansa_produced=sansa 
    )
    
    # Registriamo il log tecnico della produzione (ProductionLog)
    log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation="Spremitura + Filtrazione",
        oil_type="Virgin",
        quantity=oil,
        time_spent=process_time
    )
    
    # Salviamo le modifiche nel database
    db.session.add(new_event)
    db.session.add(log)
    db.session.commit()
    
    # Inviamo conferma di successo al frontend
    return jsonify({'status': 'success', 'message': 'Produzione Virgin completata!'})

@app.route('/produce_evo', methods=['POST'])
@login_required 
def produce_evo():
    # Recuperiamo i dati globali (Stock e Plantation)
    s = Stock.query.first()
    p = Plantation.query.first()
    
    # Controlli di sicurezza (Guard Clause)
    if not has_resources(s.olives_bought, BATCH_SIZE) or not can_afford(s.money, COST_PRODUCTION_BATCH):
        return jsonify({'status': 'error', 'message': 'Risorse o soldi insufficienti!'}), 400
    
    # Calcolo della resa
    result = calculate_yield("evo", BATCH_SIZE, p.extraction_capacity)
    
    # Aggiornamento magazzino
    s.olives_bought -= BATCH_SIZE
    s.money -= COST_PRODUCTION_BATCH
    s.oil_extra += result['oil']
    s.sansa += result['sansa']
    s.total_time += result['time']
    s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    # Registrazione nella cronologia
    new_event = HarvestHistory(
        date=datetime.now().strftime('%d.%m.%Y'),
        olive_type="EVO (Acquistate)",
        quantity=BATCH_SIZE,
        oil_produced=result['oil'],
        sansa_produced=result['sansa']
    )
    
    # Log tecnico
    log = ProductionLog(
        date=s.last_production,
        operation="Estrazione a Freddo (EVO)",
        oil_type="EVO",
        quantity=result['oil'],
        time_spent=result['time'],
        temperature=result['temp'],
        waste_loss=result['waste']
    )
    
    db.session.add(new_event)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Produzione EVO completata!'})

@app.route('/sell_product', methods=['POST'])
@login_required
def sell_product():
    product = request.form.get('product_type')
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Inserisci un numero valido!'}), 400

    s = Stock.query.first()
    
    # Конфигурация: упрощаем логику через словари (это профессиональный стиль)
    config = {
        'Virgin': {'price': PRICE_VIRGIN, 'attr': 'oil_virgin'},
        'EVO': {'price': PRICE_EVO, 'attr': 'oil_extra'},
        'Sansa': {'price': PRICE_SANSA, 'attr': 'sansa_bags'}
    }
    
    if product not in config:
        return jsonify({'status': 'error', 'message': 'Prodotto non valido!'}), 400

    stock_attr = config[product]['attr']
    price = config[product]['price']
    current_stock = getattr(s, stock_attr)

    if amount <= 0 or current_stock < amount:
        return jsonify({'status': 'error', 'message': f'Quantità insufficiente di {product}!'}), 400

    # Выполнение транзакции
    revenue = amount * price
    setattr(s, stock_attr, current_stock - amount)
    s.money += revenue
    
    new_sale = SalesHistory(
        date=datetime.now().strftime('%d.%m.%Y %H:%M'),
        product_type=product,
        quantity=amount,
        price_unit=price,
        total_revenue=revenue
    )
    db.session.add(new_sale)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f'Vendita di {amount} {product} completata per {revenue:.2f}€!'
    })

@app.route('/sell', methods=['POST'])
@login_required
def sell():
    # Recupero l'unico record dello stock; se non esiste, il sistema crasha, gestiscilo
    s = Stock.query.first()
    
    # Calcolo dei ricavi totali moltiplicando giacenza per prezzo unitario
    # Nota: il ricarico del 20% sulle bottiglie è una logica di business, tienila a mente
    revenue_virgin = s.oil_virgin * PRICE_VIRGIN
    revenue_evo = s.oil_extra * PRICE_EVO
    revenue_sansa = s.sansa * PRICE_SANSA
    revenue_bottled_v = s.bottled_virgin * (PRICE_VIRGIN * 1.2)
    revenue_bottled_e = s.bottled_extra * (PRICE_EVO * 1.2)
    
    total_revenue = revenue_virgin + revenue_evo + revenue_sansa + revenue_bottled_v + revenue_bottled_e
    
    # Controllo di integrità: non puoi vendere il nulla
    if total_revenue <= 0:
        return jsonify({'status': 'error', 'message': 'Il magazzino è vuoto!'}), 400
    
    # Aggiornamento del capitale aziendale
    s.money += total_revenue
    
    # Svuotamento fisico del magazzino: reset delle quantità dopo la vendita
    s.oil_virgin = 0
    s.oil_extra = 0
    s.sansa = 0
    s.bottled_virgin = 0
    s.bottled_extra = 0
    
    # Registrazione della transazione nella storia delle vendite
    new_sale = SalesHistory(
        date=datetime.now().strftime('%d.%m.%Y %H:%M'),
        product_type="VENDITA TOTALE",
        quantity=0, # Quantità aggregata non significativa in questo contesto
        price_unit=0,
        total_revenue=total_revenue
    )
    
    db.session.add(new_sale)
    db.session.commit()
    
    # Risposta corretta per il client AJAX
    return jsonify({
        'status': 'success', 
        'message': f'Vendita totale conclusa: {total_revenue:.2f}€ incassati!'
    })

@app.route('/next_month', methods=['POST'])
@login_required
def next_month():
    # Recupero i record di base: se mancano, solleva un'eccezione
    p = Plantation.query.first()
    s = Stock.query.first()
    
    # 1. Avanzamento del ciclo temporale
    p.current_month += 1
    if p.current_month > 12:
        p.current_month = 1 # Ciclo annuale: dopo dicembre si riparte da gennaio
        
    # 2. Logica di raccolta automatizzata (Novembre = 11)
    # Nota: la logica di calcolo è delegata al servizio esterno, come dovrebbe essere
    message = "Mese avanzato con successo."
    
    if p.current_month == 11:
        # Recupero i dati meteorologici e di raccolto
        weather = get_weather_impact()
        base_harvest = get_random_harvest(p.size_hectares)
        final_harvest = round(base_harvest * weather['impact'], 2)
        
        # Aggiornamento stock olive
        s.olives_own += final_harvest
        message = f"Novembre: {weather['type']}. {weather['msg']} Raccolti {final_harvest} kg."
    
    # 3. Addebito costi fissi di gestione (irrigazione)
    s.money -= p.irrigation_cost
    
    # Commit unico per garantire l'atomicità dell'operazione
    db.session.commit()
    
    # Risposta in formato JSON
    return jsonify({
        'status': 'success', 
        'message': message,
        'new_month': p.current_month
    })

# Acquisto di materiali di imballaggio (bottiglie e tappi) 
@app.route('/buy_packaging', methods=['POST'])
@login_required
def buy_packaging():
    # Recupero lo stato del magazzino dal database
    s = Stock.query.first()
    
    # Calcolo del costo totale (bottiglia + tappo * quantità)
    total_cost = PACKAGING_BATCH_SIZE * (COST_BOTTLE + COST_CORK)
    
    # Verifica della disponibilità economica (Guard Clause)
    if not can_afford(s.money, total_cost):
        return jsonify({'status': 'error', 'message': "Fondi insufficienti per l'imballaggio!"}), 400
    
    # Aggiornamento dei saldi e delle scorte
    s.money -= total_cost
    s.bottles += PACKAGING_BATCH_SIZE
    s.corks += PACKAGING_BATCH_SIZE 
    
    # Salvataggio persistente dei dati
    db.session.commit()
    
    # Conferma dell'operazione al client in formato JSON
    return jsonify({
        'status': 'success', 
        'message': f'Acquistati {PACKAGING_BATCH_SIZE} kit di imballaggio!'
    })

# imbottigliamento dell'olio in bottiglie
@app.route('/bottling/<oil_type>', methods=['POST'])
@login_required
def bottling(oil_type):
    # Recupero l'unico record dello stock
    s = Stock.query.first()
    
    # Mappatura dei tipi di olio per evitare catene di if/elif inutili
    # Definisco i nomi degli attributi nel database associati a ogni tipo di olio
    mapping = {
        'virgin': {'oil': 'oil_virgin', 'bottled': 'bottled_virgin'},
        'extra': {'oil': 'oil_extra', 'bottled': 'bottled_extra'}
    }
    
    # Validazione input: se il tipo non esiste nella mappa, errore 400
    if oil_type not in mapping:
        return jsonify({'status': 'error', 'message': 'Tipo olio non valido!'}), 400
    
    # Estrazione dei dati dallo stock usando getattr
    attr_oil = mapping[oil_type]['oil']
    attr_bottled = mapping[oil_type]['bottled']
    oil_amount = getattr(s, attr_oil)
    
    # Controllo disponibilità materia prima
    if oil_amount < 1:
        return jsonify({'status': 'error', 'message': "Non c'è abbastanza olio!"}), 400

    # Calcolo delle bottiglie ottenibili tramite il servizio esterno
    num_bottles, remaining_oil = calculate_bottling(oil_amount, s.bottles, s.corks)

    # Verifica se l'operazione ha prodotto risultati concreti
    if num_bottles <= 0:
        return jsonify({'status': 'error', 'message': "Mancano bottiglie o tappi!"}), 400
    
    # Aggiornamento dello stato del magazzino
    setattr(s, attr_oil, remaining_oil)
    setattr(s, attr_bottled, getattr(s, attr_bottled) + num_bottles)
    s.bottles -= num_bottles
    s.corks -= num_bottles
    
    # Persistenza nel database
    db.session.commit()
    
    # Risposta JSON di conferma
    return jsonify({
        'status': 'success', 
        'message': f"Imbottigliati {num_bottles} litri di olio {oil_type}!"
    })

@app.route('/buy_bags', methods=['POST'])
@login_required
def buy_bags():
    """Acquisto di sacchi per il confezionamento della sansa (500 pezzi)"""
    # Recupero l'unico record dello stock
    s = Stock.query.first()
    
    # Calcolo il costo totale in base alle costanti definite nel modulo validators
    total_cost = BAGS_PER_PACKAGE * COST_BAG
    
    # Verifica immediata delle risorse finanziarie (Guard Clause)
    if not can_afford(s.money, total_cost):
        return jsonify({'status': 'error', 'message': "Fondi insufficienti per acquistare i sacchi!"}), 400
    
    # Aggiornamento dello stato: deduzione dei costi e incremento giacenza
    s.money -= total_cost
    s.empty_bags += BAGS_PER_PACKAGE
    
    # Persistenza dei dati
    db.session.commit()
    
    # Risposta JSON per il client: niente redirect, gestisci la conferma lato frontend
    return jsonify({
        'status': 'success', 
        'message': f"Acquistati {BAGS_PER_PACKAGE} sacchi per la sansa!"
    })

@app.route('/package_sansa', methods=['POST'])
@login_required
def package_sansa():
    """Confezionamento della sansa in sacchi da 10kg"""
    # Recupero lo stato del magazzino dal database
    s = Stock.query.first()
    
    # Verifica preventiva: se la quantità di sansa è inferiore al minimo, errore
    if s.sansa < 10:
        return jsonify({'status': 'error', 'message': "Non c'è abbastanza sansa (min 10kg)!"}), 400
        
    # Calcolo dei sacchi confezionabili (importa la funzione in alto nel file, non qui!)
    num_bags, rest = calculate_sansa_packaging(s.sansa, s.empty_bags)
    
    # Verifica disponibilità di sacchi vuoti
    if num_bags <= 0:
        return jsonify({'status': 'error', 'message': "Mancano i sacchi vuoti!"}), 400
    
    # Aggiornamento dello stato del magazzino
    s.sansa = rest
    s.empty_bags -= num_bags
    s.sansa_bags += num_bags
    
    # Persistenza dei dati
    db.session.commit()
    
    # Risposta JSON di successo
    return jsonify({
        'status': 'success', 
        'message': f"Confezionati {num_bags} sacchi di sansa!"
    })

@app.route('/refill_money', methods=['POST'])
@login_required
def refill_money():
    """
    Funzione riservata all'amministratore per il rifinanziamento del budget aziendale.
    """
    # Verifica dei privilegi: solo l'admin ha diritto a questa operazione
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': "Accesso negato: solo l'amministratore può richiedere un sussidio!"}), 403
    
    # Recupero il record del magazzino
    s = Stock.query.first()
    
    # Erogazione del sussidio
    s.money += 5000.0
    
    # Persistenza dell'operazione
    db.session.commit()
    
    # Risposta JSON corretta
    return jsonify({
        'status': 'success', 
        'message': "La banca ha erogato un sussidio di 5000€ per l'oleificio!"
    })
    
@app.route('/api/status_data', methods=['GET'])
@login_required
def get_status_data():
    """
    Endpoint API per la sincronizzazione del frontend.
    Restituisce lo stato attuale del magazzino e i log recenti.
    """
    inventory = Stock.query.first()
    
    # Controllo di integrità: se il database è vuoto, solleva un'eccezione
    if not inventory:
        return jsonify({'status': 'error', 'message': 'Stato del magazzino non inizializzato'}), 500

    # Recupero i log filtrati: limitare a 10 elementi è una buona pratica di performance
    logs = ProductionLog.query.order_by(ProductionLog.id.desc()).limit(10).all()
    
    # Serializzazione dei dati: conversione esplicita dei tipi per il JSON
    data = {
        'inventory': {
            'money': float(inventory.money),
            'olives_own': float(inventory.olives_own),
            'olives_bought': float(inventory.olives_bought),
            'oil_extra': float(inventory.oil_extra),
            'oil_virgin': float(inventory.oil_virgin),
            'sansa': float(inventory.sansa),
            'bottles': int(inventory.bottles),
            'corks': int(inventory.corks),
            'empty_bags': int(inventory.empty_bags),
            'bottled_extra': int(inventory.bottled_extra),
            'bottled_virgin': int(inventory.bottled_virgin),
            'sansa_bags': int(inventory.sansa_bags)
        },
        'logs': [
            {
                'date': log.date.split(' ')[1] if ' ' in log.date else log.date, 
                'temperature': getattr(log, 'temperature', 0) # Uso getattr per sicurezza
            } 
            for log in reversed(logs)
        ]
    }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
