"""
Oleificio Simulation - Controller Module

Architettura: MVC (Model-View-Controller)
Framework: Flask
Database: SQLAlchemy (SQLite)

Modulo dedicato alla gestione della logica di business, del routing,
della persistenza dei dati e del flusso delle operazioni produttive.
"""

from flask import Flask, render_template, redirect, url_for, jsonify, flash, request
from datetime import datetime
from models import db, Stock, Plantation, HarvestHistory, User, SalesHistory, ProductionLog  
from services.oil_logic import calculate_yield, get_random_harvest, get_weather_impact, calculate_bottling, calculate_sansa_packaging
from utils.validators import (
    can_afford, has_resources, 
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH,
    PRICE_VIRGIN, PRICE_EVO, PRICE_SANSA,
    COST_BOTTLE, COST_CORK, MARKUP_BOTTLED_OIL, SANSA_BAG_CAPACITY, GOVERNMENT_SUBSIDY,             
    COST_BAG, BAGS_PER_PACKAGE, PRODUCTION_CAPACITY, BATCH_SIZE, PACKAGING_BATCH_SIZE,    
)
from flask_login import (LoginManager, 
   login_user, login_required, 
   logout_user, current_user)

app = Flask(__name__)

# =============================================================================
# INITIALIZZAZIONE E CONFIGURAZIONE APPLICAZIONE
# =============================================================================

# Configurazione del sistema di autenticazione
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    """Caricamento dell'utente dal database per la sessione corrente."""
    return User.query.get(int(user_id))


# Configurazione del database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'la-mia-chiave-segreta-123' 

db.init_app(app)

with app.app_context():
    db.create_all()
    # Inizializzazione entità di base per il funzionamento della simulazione 
    if not Stock.query.first():
        db.session.add(Stock())
    if not Plantation.query.first():
        db.session.add(Plantation())
    
    # Creazione utente amministratore di default
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='123', role='admin')
        db.session.add(admin)
        print("--- User admin created! ---")
        
    db.session.commit()

# =============================================================================
# GESTIONE AUTENTICAZIONE E ACCESSO
# =============================================================================

@app.route('/')
def home():
    """
    Redirezione automatica alla dashboard principale.
    
    Returns:
        Response: Redirezione verso l'endpoint 'status'.
    """
    return redirect(url_for('status'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gestisce il processo di autenticazione dell'utente.

    Verifica le credenziali nel database e, in caso di successo, inizializza 
    la sessione Flask-Login. Gestisce anche il feedback visivo tramite flash messages.

    Returns:
        Response: Pagina di login o redirezione alla dashboard in caso di autenticazione riuscita.
    """
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
    """
    Termina la sessione corrente dell'utente e invalida il login.

    Returns:
        Response: Redirezione alla pagina di login.
    """
    logout_user()
    return redirect(url_for('login'))

# =============================================================================
# CORE LOGIC: PRODUZIONE E MAGAZZINO
# =============================================================================

@app.route('/status')
@login_required 
def status():
    """
    Dashboard principale: recupera lo stato attuale delle scorte e dei terreni.

    Aggrega i dati storici provenienti da diverse tabelle (Harvest, Sales, ProductionLog)
    per fornire una visione d'insieme dei KPI dell'oleificio.

    Returns:
        Response: Rendering del template 'status.html' con i dati aggregati.
    """
    inventory = Stock.query.first()
    factory_land = Plantation.query.first()
    production_logs = ProductionLog.query.all()
    
    
    all_logs = []
    
    # Normalizzazione dei dati storici: unifichiamo formati eterogenei (raccolti, vendite, log tecnici)
    # per permettere una visualizzazione cronologica coerente nella tabella della dashboard.
    for h in HarvestHistory.query.all():
        all_logs.append({
            'date': h.date, 
            'type': 'Produzione', 
            'desc': h.olive_type, 
            'val': f"{h.oil_produced} L" 
        })
        
    for s in SalesHistory.query.all():
        all_logs.append({
            'date': s.date, 
            'type': 'Vendita', 
            'desc': s.product_type, 
            'val': f"{s.total_revenue:.2f} €" 
        })
        
    for p in ProductionLog.query.all():
    # Logica di business: distinzione tra unità di misura (Litri vs Pezzi/Kit)
        unit = "pz" if "Sacchi" in p.operation or "Kit" in p.operation else "L"

        all_logs.append({
                'date': p.date.split(' ')[0], 
                'type': 'Produzione', 
                'desc': p.operation, 
                'val': f"{p.quantity} {unit}"
            })

    # Ordinamento decrescente (cronologia recente in alto) e slicing sui 20 elementi
    all_logs = sorted(all_logs, key=lambda x: x['date'], reverse=True)[:20]

    return render_template('status.html', 
                           inventory=inventory, 
                           land=factory_land, 
                           all_logs=all_logs,
                           production_logs=production_logs)

@app.route('/buy', methods=['POST'])
@login_required 
def buy():
    """
    Gestisce l'acquisto di materia prima (olive) dal mercato.
    
    Verifica la sostenibilità economica tramite Guard Clause e aggiorna 
    il capitale aziendale e lo stock in caso di esito positivo.

    Returns:
        JSON: Conferma dell'acquisto o errore in caso di fondi insufficienti.
    """
    s = Stock.query.first()
    
    # Esecuzione del pattern 'Guard Clause': verifichiamo la disponibilità di budget 
    # prima di procedere con la transazione commerciale.
    if can_afford(s.money, COST_BUY_OLIVES):
        s.money -= COST_BUY_OLIVES
        s.olives_bought += 100
        new_log = ProductionLog(
            date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            operation="Acquisto Olive",
            quantity=100
        )

        # Persistenza atomica delle operazioni nel database.
        db.session.add(new_log)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Acquistati 100 kg di olive!'})
    else:
        return jsonify({'status': 'error', 'message': 'Soldi insufficienti!'}), 400
    
# =============================================================================
# OPERAZIONI DI PRODUZIONE E TRASFORMAZIONE
# =============================================================================

@app.route('/produce_virgin', methods=['POST'])
@login_required 
def produce_virgin():
    """
    Simula il processo di spremitura per le olive di produzione propria (Virgin).

    Esegue le verifiche di sostenibilità economica e operativa, calcola la resa 
    produttiva tramite il modulo di business logic dedicato, aggiorna le giacenze 
    di magazzino e archivia i dati tecnici e storici dell'operazione.

    Returns:
        JSON: Risposta standardizzata con esito dell'operazione e feedback per l'utente.
    """
    s = Stock.query.first()
    
    # Esecuzione del pattern 'Guard Clause': verifica preventiva per evitare stati inconsistenti.
    res = has_resources(s.olives_own, BATCH_SIZE) 
    afford = can_afford(s.money, COST_PRODUCTION_BATCH)
    
    if not res or not afford:
        return jsonify({'status': 'error', 'message': 'Risorse o soldi insufficienti!'}), 400
    
    # Calcolo dei parametri di rendimento basato su logica esterna;
    # utilizziamo il tipo 'premium' per identificare la qualità Virgin.
    risultati = calculate_yield("premium", BATCH_SIZE, PRODUCTION_CAPACITY)
    
    oil = risultati["oil"]
    sansa = risultati["sansa"]
    process_time = risultati["time"]
    
    # Aggiornamento contabile e fisico: scarichiamo materia prima e carichiamo prodotti finiti.
    s.olives_own -= BATCH_SIZE
    s.money -= COST_PRODUCTION_BATCH
    s.oil_virgin += oil
    s.sansa += sansa
    s.total_time += process_time
    
   # Istanza record storico: tracciamento produzione per statistiche di rendimento.
    new_event = HarvestHistory(
        date=datetime.now().strftime('%d.%m.%Y'),
        olive_type="Vergine (Propria)",
        quantity=BATCH_SIZE,
        oil_produced=oil,
        sansa_produced=sansa 
    )
    
    # Istanza del log tecnico: utile per il monitoraggio dei tempi di processo e ottimizzazione della linea.
    log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation="Spremitura + Filtrazione",
        oil_type="Virgin",
        quantity=oil,
        time_spent=process_time
    )
    
    # Persistenza atomica delle operazioni nel database.
    db.session.add(new_event)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Produzione Virgin completata!'})

@app.route('/produce_evo', methods=['POST'])
@login_required 
def produce_evo():

    """
    Simula la trasformazione delle olive acquistate in olio EVO.

    La funzione esegue il calcolo della resa basandosi sulle capacità estrattive 
    dell'impianto, aggiorna le giacenze di magazzino e registra l'evento 
    nel database storico per analisi future.

    Returns:
        JSON: Risposta con esito operazione ('success' o 'error') e messaggio di feedback.
    """
    s = Stock.query.first()
    p = Plantation.query.first()
    
    # Validazione preventiva: garantisce che l'oleificio disponga di materia prima e budget sufficienti
    if not has_resources(s.olives_bought, BATCH_SIZE) or not can_afford(s.money, COST_PRODUCTION_BATCH):
        return jsonify({'status': 'error', 'message': 'Risorse o soldi insufficienti!'}), 400
    
    # Calcolo resa estrazione
    result = calculate_yield("evo", BATCH_SIZE, p.extraction_capacity)
    
    # Sincronizzazione delle scorte e aggiornamento dei parametri operativi dopo l'estrazione.
    s.olives_bought -= BATCH_SIZE
    s.money -= COST_PRODUCTION_BATCH
    s.oil_extra += result['oil']
    s.sansa += result['sansa']
    s.total_time += result['time']
    s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    # Registrazione storica eventi
    new_event = HarvestHistory(
        date=datetime.now().strftime('%d.%m.%Y'),
        olive_type="EVO (Acquistate)",
        quantity=BATCH_SIZE,
        oil_produced=result['oil'],
        sansa_produced=result['sansa']
    )
    
    
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

# =============================================================================
# OPERAZIONI DI VENDITA E LIQUIDAZIONE MAGAZZINO
# =============================================================================

@app.route('/sell_product', methods=['POST'])
@login_required
def sell_product():

    """
    Gestisce la vendita selettiva di una specifica tipologia di prodotto.

    Verifica la disponibilità a magazzino, calcola il ricavo basato sul prezzo
    unitario di mercato e registra la transazione nello storico vendite.

    Returns:
        JSON: Conferma dell'operazione o messaggio di errore in caso di quantità non valida.
    """

    product = request.form.get('product_type')
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Inserisci un numero valido!'}), 400

    s = Stock.query.first()
    
    # Mappatura dinamica per associare il prodotto al suo attributo nel database e prezzo di mercato.
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

    # Validazione quantità prima della transazione
    if amount <= 0 or current_stock < amount:
        return jsonify({'status': 'error', 'message': f'Quantità insufficiente di {product}!'}), 400

    # Calcolo dei ricavi e aggiornamento delle giacenze tramite riflessione (setattr).
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
    """
    Esegue la liquidazione totale del magazzino.

    Calcola il valore complessivo di tutte le giacenze (inclusi prodotti imbottigliati 
    con relativo markup) e azzera il magazzino post-vendita.

    Returns:
        JSON: Riepilogo finanziario della liquidazione.
    """
    s = Stock.query.first()
    
    # Calcolo dei ricavi totali moltiplicando giacenza per prezzo unitarioCalcolo ricavi totali per ogni categoria 
    # inclusi prodotti imbottigliati con ricarico    
    revenue_virgin = s.oil_virgin * PRICE_VIRGIN
    revenue_evo = s.oil_extra * PRICE_EVO
    revenue_sansa = s.sansa * PRICE_SANSA
    revenue_bottled_v = s.bottled_virgin * (PRICE_VIRGIN * MARKUP_BOTTLED_OIL)
    revenue_bottled_e = s.bottled_extra * (PRICE_EVO * MARKUP_BOTTLED_OIL)
    
    total_revenue = revenue_virgin + revenue_evo + revenue_sansa + revenue_bottled_v + revenue_bottled_e
    
    # Verifica che il magazzino contenga merci vendibili
    if total_revenue <= 0:
        return jsonify({'status': 'error', 'message': 'Il magazzino è vuoto!'}), 400
    
   # Aggiornamento contabile e reset giacenze
    s.money += total_revenue
    s.oil_virgin = 0
    s.oil_extra = 0
    s.sansa = 0
    s.bottled_virgin = 0
    s.bottled_extra = 0
    
    # Registrazione della transazione nella storia delle vendite
    new_sale = SalesHistory(
        date=datetime.now().strftime('%d.%m.%Y %H:%M'),
        product_type="VENDITA TOTALE",
        quantity=0,  
        price_unit=0,
        total_revenue=total_revenue
    )
    
    db.session.add(new_sale)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f'Vendita totale conclusa: {total_revenue:.2f}€ incassati!'
    })

@app.route('/sell_bottled', methods=['POST'])
@login_required
def sell_bottled():

    """
    Gestisce la vendita specifica di prodotti imbottigliati con ricarico.

    Verifica la disponibilità di stock per il tipo di olio richiesto, 
    applica il markup di vendita e registra la transazione.

    Returns:
        JSON: Conferma della vendita o errore in caso di giacenze insufficienti.
    """

    product = request.form.get('product_type')
    try:
        amount = int(request.form.get('amount', 0))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Quantità non valida!'}), 400

    s = Stock.query.first()
    
    # Selezione logica basata sul tipo di olio imbottigliato
    if product == 'Virgin':
        if s.bottled_virgin < amount:
            return jsonify({'status': 'error', 'message': 'Quantità non disponibile!'}), 400
        s.bottled_virgin -= amount
        revenue = amount * (PRICE_VIRGIN * MARKUP_BOTTLED_OIL)
    elif product == 'Bottled_EVO':
        if s.bottled_extra < amount:
            return jsonify({'status': 'error', 'message': 'Quantità non disponibile!'}), 400
        s.bottled_extra -= amount
        revenue = amount * (PRICE_EVO * MARKUP_BOTTLED_OIL)
    else:
        return jsonify({'status': 'error', 'message': 'Prodotto non riconosciuto!'}), 400

    s.money += revenue
    
    new_sale = SalesHistory(
        date=datetime.now().strftime('%d.%m.%Y %H:%M'),
        product_type=product,
        quantity=amount,
        price_unit=(PRICE_VIRGIN * 1.2 if product == 'Virgin' else PRICE_EVO * 1.2),
        total_revenue=revenue
    )
    db.session.add(new_sale)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'Vendita di {amount} bottiglie completata!'})

# =============================================================================
# OPERAZIONI DI GESTIONE CICLO TEMPORALE 
# =============================================================================

@app.route('/next_month', methods=['POST'])
@login_required
def next_month():
    """
    Gestisce l'avanzamento del ciclo temporale della simulazione.

    Gestisce il rollover dell'anno solare, applica eventi stagionali (raccolta a Novembre)
    influenzati dalle condizioni meteorologiche e addebita i costi fissi operativi.

    Returns:
        Response: Redirezione alla dashboard con feedback dell'operazione.
    """
    p = Plantation.query.first()
    s = Stock.query.first()
    
    # Incremementazione mese con ciclo annuale
    p.current_month += 1
    if p.current_month > 12:
        p.current_month = 1 
        
    # Logica specifica per la raccolta a Novembre (Mese 11)
    message = "Mese avanzato con successo."
    
    if p.current_month == 11:
        # Recupero i dati meteorologici e di raccolto
        weather = get_weather_impact()
        base_harvest = get_random_harvest(p.size_hectares)
        final_harvest = round(base_harvest * weather['impact'], 2)
        
        # Aggiornamento stock olive
        s.olives_own += final_harvest
        message = f"Novembre: {weather['type']}. {weather['msg']} Raccolti {final_harvest} kg."
    
    # Applicazione costi operativi fissi
    s.money -= p.irrigation_cost
    
    db.session.commit()
    
    flash(message, 'success') 
    return redirect(url_for('status')) 

# =============================================================================
# OPERAZIONI DI IMBOTTIGLIAMENTO E CONFEZIONAMENTO
# =============================================================================
 
@app.route('/buy_packaging', methods=['POST'])
@login_required
def buy_packaging():
    """
    Gestisce l'acquisto di kit di imballaggio (bottiglie e tappi) dal mercato.

    Verifica la disponibilità di budget (Guard Clause) prima di procedere con 
    l'aggiornamento delle scorte di materiale.

    Returns:
        JSON: Conferma dell'acquisto o errore in caso di fondi insufficienti.
    """
    s = Stock.query.first()
    
    # Calcolo del costo totale (bottiglia + tappo * quantità)
    total_cost = PACKAGING_BATCH_SIZE * (COST_BOTTLE + COST_CORK)
    
    # Verifica della disponibilità economica 
    if not can_afford(s.money, total_cost):
        return jsonify({'status': 'error', 'message': "Fondi insufficienti per l'imballaggio!"}), 400
    
    # Aggiornamento contabile e magazzino materiali
    s.money -= total_cost
    s.bottles += PACKAGING_BATCH_SIZE
    s.corks += PACKAGING_BATCH_SIZE 
    
    new_log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation="Acquisto Kit Imballaggio",
        quantity=PACKAGING_BATCH_SIZE
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f'Acquistati {PACKAGING_BATCH_SIZE} kit di imballaggio!'
    })

@app.route('/bottling/<oil_type>', methods=['POST'])
@login_required
def bottling(oil_type):
    """
    Procedura di imbottigliamento per una tipologia specifica di olio.

    Utilizza mappature dinamiche per gestire oli diversi e calcola la resa 
    in bottiglie finali basandosi sulla disponibilità di materiali di imballaggio.

    Returns:
        JSON: Conferma dell'imbottigliamento o messaggio di errore in caso di mancanze.
    """
    s = Stock.query.first()
    
    # Mappatura attributi DB per astrazione codice: permette di scalare la logica su diversi tipi di olio.  
    mapping = {
        'virgin': {'oil': 'oil_virgin', 'bottled': 'bottled_virgin'},
        'extra': {'oil': 'oil_extra', 'bottled': 'bottled_extra'}
    }
    
    if oil_type not in mapping:
        return jsonify({'status': 'error', 'message': 'Tipo olio non valido!'}), 400
    
    # Recupero dati tramite dinamismo (getattr)
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
    
    new_log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation=f"Imbottigliamento {oil_type.capitalize()}",
        quantity=num_bottles
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f"Imbottigliati {num_bottles} litri di olio {oil_type}!"
    })

@app.route('/buy_bags', methods=['POST'])
@login_required
def buy_bags():
    """
    Gestisce l'acquisto di sacchi necessari per lo stoccaggio e la vendita della sansa.

    Verifica la disponibilità economica e aggiorna le scorte di materiali di imballaggio.

    Returns:
        JSON: Conferma dell'acquisto o messaggio di errore per fondi insufficienti.
    """
    s = Stock.query.first()
    
    # Calcolo costo basato su lotti standard definiti nelle configurazioni di sistema.
    total_cost = BAGS_PER_PACKAGE * COST_BAG
    
    # Verifica budget: il sistema impedisce l'acquisto se il capitale aziendale è insufficiente. 
    if not can_afford(s.money, total_cost):
        return jsonify({'status': 'error', 'message': "Fondi insufficienti per acquistare i sacchi!"}), 400
    
    # Aggiornamento dello stato: deduzione dei costi e incremento giacenza
    s.money -= total_cost
    s.empty_bags += BAGS_PER_PACKAGE
    
    new_log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation="Acquisto Sacchi Sansa",
        quantity=BAGS_PER_PACKAGE
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f"Acquistati {BAGS_PER_PACKAGE} sacchi per la sansa!"
    })

@app.route('/package_sansa', methods=['POST'])
@login_required
def package_sansa():
    """
    Gestisce il confezionamento della sansa in sacchi standardizzati per la vendita.

    Verifica la disponibilità tecnica della materia prima e dei materiali di 
    imballaggio prima di finalizzare l'operazione.

    Returns:
        JSON: Feedback sull'esito del confezionamento o segnalazione di carenze tecniche.
    """
    s = Stock.query.first()
    
    # Controllo minimo tecnico
    if s.sansa < SANSA_BAG_CAPACITY:
        return jsonify({'status': 'error', 'message': f"Non c'è abbastanza sansa (min {SANSA_BAG_CAPACITY}kg)!"}), 400
        
    # Calcolo quantità insaccabile e residuo
    num_bags, rest = calculate_sansa_packaging(s.sansa, s.empty_bags)
    
    # Verifica disponibilità di sacchi vuoti
    if num_bags <= 0:
        return jsonify({'status': 'error', 'message': "Mancano i sacchi vuoti!"}), 400
    
    # Aggiornamento dello stato del magazzino: riduzione materia prima e incremento prodotto finito.
    s.sansa = rest
    s.empty_bags -= num_bags
    s.sansa_bags += num_bags

    new_log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation="Confezionamento Sansa",
        quantity=num_bags
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f"Confezionati {num_bags} sacchi di sansa!"
    })

# =============================================================================
# OPERAZIONI DI GESTIONE FINANZIARIA E REPORTING
# =============================================================================

@app.route('/refill_money', methods=['POST'])
@login_required
def refill_money():
    """
    Eroga un finanziamento straordinario (sussidio governativo).

    Operazione riservata esclusivamente agli utenti con ruolo di amministratore 
    per supportare la sostenibilità finanziaria in casi critici.

    Returns:
        JSON: Conferma dell'erogazione o errore di accesso.
    """
    # Controllo di sicurezza basato sui privilegi dell'utente autenticato.
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': "Accesso negato: solo l'amministratore può richiedere un sussidio!"}), 403
    
    s = Stock.query.first()
    
    # Erogazione del sussidio
    s.money += GOVERNMENT_SUBSIDY
    
    new_log = ProductionLog(
        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        operation="Sussidio Governativo",
        quantity=GOVERNMENT_SUBSIDY
    )
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': f"La banca ha erogato un sussidio di {int(GOVERNMENT_SUBSIDY)}€ per l'oleificio!"
    })

# =============================================================================
# API ENDPOINTS (ASINCRONI / INTERFACCIA)
# =============================================================================  
#   
@app.route('/api/status_data', methods=['GET'])
@login_required
def get_status_data():
    """
    Endpoint API per l'aggiornamento dinamico della dashboard tramite AJAX.

    Serializza lo stato corrente dell'inventario, le ultime vendite e i dati 
    di produzione per supportare l'interattività dell'interfaccia utente.

    Returns:
        JSON: Set completo di dati aggiornati per il frontend.
    """
    inventory = Stock.query.first()
    if not inventory:
        return jsonify({'status': 'error'}), 500

    # Recupero storico vendite recenti per il refresh della tabella (limite 20 record).
    sales = SalesHistory.query.order_by(SalesHistory.id.desc()).limit(20).all()
    sales_logs = [
        {'date': s.date, 'type': 'Vendita', 'desc': s.product_type, 'val': f"{s.total_revenue:.2f} €"}
        for s in sales
    ]
    
    # Recupero log temperatura per l'aggiornamento dinamico dei grafici (limite 10 record).
    temp_logs = ProductionLog.query.order_by(ProductionLog.id.desc()).limit(10).all()
    temp_data = [
        {'date': log.date.split(' ')[1] if ' ' in log.date else log.date, 'temperature': getattr(log, 'temperature', 0)}
        for log in reversed(temp_logs)
    ]
    
    # Serializzazione dati in formato JSON
    return jsonify({
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
        'logs': sales_logs,    
        'temp_data': temp_data 
    })

if __name__ == '__main__':
    # Avvio applicazione Flask in modalità debug
    app.run(debug=True)
