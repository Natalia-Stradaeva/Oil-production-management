// Funzione per mostrare un avviso se la temperatura è alta
function checkTemperature(temp) {
    if (temp > 27.0) {
        console.warn("Attenzione: Temperatura elevata (" + temp + "°C). Sistema in raffreddamento.");
        
    }
}

// Esempio: conferma prima di vendere tutto
document.querySelectorAll('.btn-red').forEach(button => {
    button.addEventListener('click', function(e) {
        const confirmAction = confirm("Sei sicuro di voler vendere l'intero stock?");
        if (!confirmAction) {
            e.preventDefault();
        }
    });
});


document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('sale-form')) {
        e.preventDefault(); // Запрещаем перезагрузку страницы!
        
        const formData = new FormData(e.target);
        
        fetch(e.target.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // ВОТ ТУТ МЕСТО ДЛЯ ТВОЕГО БЛОКА:
            if (data.status === 'success') {
                console.log(data.message);
                updateDashboard(); // Обновляем цифры на дашборде
            } else {
                alert(data.message); // Показываем ошибку, если что-то пошло не так
            }
        })
        .catch(err => {
            console.error("Error:", err);
            alert("Errore di connessione al server.");
        });
    }
});

// Скрытие уведомлений через 3 секунды
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(a => a.style.display = 'none');
}, 3000);

// --- ЭТОТ БЛОК ОТВЕЧАЕТ ЗА СОХРАНЕНИЕ ПОЗИЦИИ ПРОКРУТКИ ---
window.addEventListener('beforeunload', function() {
    localStorage.setItem('scrollPosition', window.scrollY);
});

window.addEventListener('load', function() {
    const savedScroll = localStorage.getItem('scrollPosition');
    if (savedScroll) {
        window.scrollTo({
            top: parseInt(savedScroll),
            behavior: 'instant' 
        });
        localStorage.removeItem('scrollPosition');
    }
});

// --- НОВАЯ ФУНКЦИЯ ДЛЯ AJAX ОБНОВЛЕНИЯ ---
function updateDashboard() {
    fetch('/api/status_data')
        .then(response => response.json())
        .then(data => {
            const inv = data.inventory;
            
            // Обновляем показатели
            const elements = {
                'val-money': `${inv.money.toFixed(2)}`,
                'val-olives-own': `${inv.olives_own} kg`,
                'val-olives-bought': `${inv.olives_bought} kg`,
                'val-bottles': `${inv.bottles} шт.`,
                'val-corks': `${inv.corks} шт.`,
                'val-empty-bags': `${inv.empty_bags} pz`,
                'val-virgin': `${inv.oil_virgin} L`,
                'val-evo': `${inv.oil_extra} L`,
                'val-sansa': `${inv.sansa} kg`,
                'val-bottled-virgin': `${inv.bottled_virgin} unità`,
                'val-bottled-extra': `${inv.bottled_extra} unità`,
                'val-sansa-bags': `${inv.sansa_bags} unità`
            };

            for (const [id, value] of Object.entries(elements)) {
                const el = document.getElementById(id);
                if (el) el.innerText = value;
            }
        })
        .catch(error => console.error('Errore aggiornamento:', error));
}

// Запускаем обновление каждые 3 секунды
setInterval(updateDashboard, 3000);