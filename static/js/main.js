window.addEventListener('load', function() {
    const savedScroll = localStorage.getItem('scrollPosition');
    if (savedScroll) {
        window.scrollTo(0, parseInt(savedScroll));
        localStorage.removeItem('scrollPosition');
    }
});

window.addEventListener('beforeunload', function() {
    localStorage.setItem('scrollPosition', window.scrollY);
});

document.addEventListener('submit', function() {
    
    const activeBtn = document.activeElement;
    if (activeBtn && activeBtn.tagName === 'BUTTON') {
        activeBtn.style.opacity = '0.5';
        activeBtn.innerText = 'Elaborazione...';
    }
});


setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(a => a.style.display = 'none');
}, 3000);