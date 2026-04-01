import random
from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
from models import db, Stock, Plantation, HarvestHistory, User, SalesHistory  
from services.oil_logic import calculate_yield, get_random_harvest
from utils.validators import (
    can_afford, has_resources, 
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH,
    PRICE_VIRGIN, PRICE_EVO, PRICE_SANSA,
    COST_BOTTLE, COST_CORK,              
    TIME_SPREMITURA, TIME_FILTRAZIONE    
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
    from models import ProductionLog # import model logs 
    # prendiamo dati da tutte e tre le tabelle per la visualizzazione
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

@app.route('/buy')
@login_required # Solo utenti loggati possono comprare
def buy():
    s = Stock.query.first()
    if can_afford(s.money, COST_BUY_OLIVES):
        s.money -= COST_BUY_OLIVES
        s.olives_bought += 100
        db.session.commit()
        flash(f"Acquistati con successo 100 kg di olive!", "success") # feedback positivo
    else:
        flash("Non ci sono abbastanza soldi per acquistare olive!", "danger") # feedback negativo
    return redirect(url_for('status'))
    


@app.route('/produce_virgin')
@login_required 
def produce_virgin():
    from models import ProductionLog, HarvestHistory 
    s = Stock.query.first()
    batch_size = 100
    res = has_resources(s.olives_own, batch_size) 
    afford = can_afford(s.money, COST_PRODUCTION_BATCH)
    
    if res and afford:
        oil, sansa = calculate_yield("premium", batch_size)
        process_time = TIME_SPREMITURA + TIME_FILTRAZIONE
        
        s.olives_own -= batch_size
        s.money -= COST_PRODUCTION_BATCH
        s.oil_virgin += oil
        s.sansa += sansa
        s.total_time += process_time
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        # ИСПРАВЛЕНО: Добавлен параметр sansa_produced
        new_event = HarvestHistory(
            date=datetime.now().strftime('%d.%m.%Y'),
            olive_type="Vergine (Propria)",
            quantity=batch_size,
            oil_produced=oil,
            sansa_produced=sansa 
        )
        
        log = ProductionLog(
            date=s.last_production,
            operation="Spremitura + Filtrazione",
            oil_type="Virgin",
            quantity=oil,
            time_spent=process_time
        )
        
        db.session.add(new_event)
        db.session.add(log)
        db.session.commit()
        flash(f"Successo! Prodotti {oil}L di Virgin e {sansa}kg di Sansa", "success")
    else:
        if not res: flash("Non ci sono abbastanza olive proprie!", "danger")
        if not afford: flash("Soldi insufficienti!", "danger")
    return redirect(url_for('status'))

@app.route('/produce_evo')
@login_required 
def produce_evo():
    from models import ProductionLog, HarvestHistory 
    s = Stock.query.first()
    batch_size = 100
    res = has_resources(s.olives_bought, batch_size) 
    afford = can_afford(s.money, COST_PRODUCTION_BATCH)
    
    if res and afford:
        oil, sansa = calculate_yield("evo", batch_size)
        process_time = TIME_SPREMITURA + TIME_FILTRAZIONE
        
        s.olives_bought -= batch_size
        s.money -= COST_PRODUCTION_BATCH
        s.oil_extra += oil  
        s.sansa += sansa
        s.total_time += process_time
        s.last_production = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        # ИСПРАВЛЕНО: Добавлен параметр sansa_produced
        new_event = HarvestHistory(
            date=datetime.now().strftime('%d.%m.%Y'),
            olive_type="EVO (Purchased)",
            quantity=batch_size,
            oil_produced=oil,
            sansa_produced=sansa
        )
        
        log = ProductionLog(
            date=s.last_production,
            operation="Spremitura + Filtrazione (EVO)",
            oil_type="EVO",
            quantity=oil,
            time_spent=process_time
        )
        
        db.session.add(new_event)
        db.session.add(log)
        db.session.commit()
        flash(f"Successo! Prodotti {oil}L di EVO e {sansa}kg di Sansa", "success")
    return redirect(url_for('status'))

@app.route('/sell_product', methods=['POST'])
@login_required
def sell_product():
    product = request.form.get('product_type')
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash("Inserisci un numero valido!", "danger")
        return redirect(url_for('status'))

    s = Stock.query.first()
    price = 0
    
    # Determiniamo il prezzo e verifichiamo la disponibilità del prodotto
    if product == 'Virgin':
        price = PRICE_VIRGIN
        stock_attr = 'oil_virgin'
    elif product == 'EVO':
        price = PRICE_EVO
        stock_attr = 'oil_extra'
    elif product == 'Sansa':
        price = PRICE_SANSA
        stock_attr = 'sansa'
    else:
        flash("Prodotto non valido!", "danger")
        return redirect(url_for('status'))

    current_stock = getattr(s, stock_attr)

    if amount > 0 and current_stock >= amount:
        revenue = amount * price
        setattr(s, stock_attr, current_stock - amount)
        s.money += revenue
        
        # Salviamo nella storia delle vendite
        new_sale = SalesHistory(
            date=datetime.now().strftime('%d.%m.%Y %H:%M'),
            product_type=product,
            quantity=amount,
            price_unit=price,
            total_revenue=revenue
        )
        db.session.add(new_sale)
        db.session.commit()
        flash(f"Venduti {amount} unità di {product} per {revenue:.2f}€!", "success")
    else:
        flash(f"Quantità insufficiente di {product}!", "danger")
        
    return redirect(url_for('status'))

@app.route('/sell')
@login_required
def sell():
    s = Stock.query.first()
    total_revenue = 0
    
    # 1. Считаем и обнуляем разливное масло
    revenue_virgin = s.oil_virgin * PRICE_VIRGIN
    revenue_evo = s.oil_extra * PRICE_EVO
    revenue_sansa = s.sansa * PRICE_SANSA
    
    # 2. Считаем и обнуляем БУТЫЛКИ (пусть они будут на 20% дороже)
    revenue_bottled_v = s.bottled_virgin * (PRICE_VIRGIN * 1.2)
    revenue_bottled_e = s.bottled_extra * (PRICE_EVO * 1.2)
    
    total_revenue = revenue_virgin + revenue_evo + revenue_sansa + revenue_bottled_v + revenue_bottled_e
    
    if total_revenue > 0:
        s.money += total_revenue
        
        # Обнуляем склады
        s.oil_virgin = 0
        s.oil_extra = 0
        s.sansa = 0
        s.bottled_virgin = 0
        s.bottled_extra = 0
        
        # Записываем в историю общую продажу
        new_sale = SalesHistory(
            date=datetime.now().strftime('%d.%m.%Y %H:%M'),
            product_type="VENDITA TOTALE",
            quantity=0, # Для общей продажи поставим 0 или сумму единиц
            price_unit=0,
            total_revenue=total_revenue
        )
        db.session.add(new_sale)
        db.session.commit()
        flash(f"Grande affare! Hai venduto tutto lo stock per {total_revenue:.2f}€!", "success")
    else:
        flash("Il magazzino è già vuoto!", "warning")
        
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
        from services.oil_logic import get_weather_impact, get_random_harvest
        weather = get_weather_impact()
        base_harvest = get_random_harvest(p.size_hectares)
        final_harvest = round(base_harvest * weather['impact'], 2)
        
        s.olives_own += final_harvest
        flash(f"Novembre: {weather['type']}. {weather['msg']} Raccolti {final_harvest} kg.", "info")
    
    s.money -= p.irrigation_cost
    db.session.commit()
    return redirect(url_for('status'))

# Acquisto di materiali di imballaggio (bottiglie e tappi) 
@app.route('/buy_packaging')
@login_required
def buy_packaging():
    s = Stock.query.first()
    batch_size = 50 # Acquistiamo in confezioni da 50 pezzi.
    total_cost = batch_size * (COST_BOTTLE + COST_CORK) # 50 euro
    
    if can_afford(s.money, total_cost):
        s.money -= total_cost
        s.bottles += batch_size
        s.corks += batch_size
        db.session.commit()
        flash(f"Acquistati {batch_size} kit di imballaggio (1.00€/cad)!", "success")
    else:
        flash("Non hai abbastanza soldi per l'imballaggio!", "danger")
    return redirect(url_for('status'))

# imbottigliamento dell'olio in bottiglie
@app.route('/bottling/<oil_type>')
@login_required
def bottling(oil_type):
    from services.oil_logic import calculate_bottling
    s = Stock.query.first()
    
    if oil_type == 'virgin':
        oil_amount = s.oil_virgin
        attr_oil = 'oil_virgin'
        attr_bottled = 'bottled_virgin'
    else:
        oil_amount = s.oil_extra
        attr_oil = 'oil_extra'
        attr_bottled = 'bottled_extra'

    if oil_amount < 1:
        flash("Non c'è abbastanza olio da imbottigliare (minimo 1L)!", "warning")
        return redirect(url_for('status'))

    num_bottles, remaining_oil = calculate_bottling(oil_amount, s.bottles, s.corks)

    if num_bottles > 0:
        setattr(s, attr_oil, remaining_oil)
        setattr(s, attr_bottled, getattr(s, attr_bottled) + num_bottles)
        s.bottles -= num_bottles
        s.corks -= num_bottles
        db.session.commit()
        flash(f"Imbottigliati {num_bottles} litri di olio {oil_type}!", "success")
    else:
        flash("Mancano bottiglie o tappi!", "danger")
        
    return redirect(url_for('status'))

@app.route('/refill_money')
@login_required
def refill_money():
    if current_user.role == 'admin':
        s = Stock.query.first()
        s.money += 5000.0
        db.session.commit()
        flash("La banca ha erogato un sussidio di 5000€ per Oleificio Natalia!", "success")
    else:
        flash("Solo l'amministratore può richiedere un sussidio!", "danger")
    return redirect(url_for('status'))     
    


if __name__ == '__main__':
    app.run(debug=True)
