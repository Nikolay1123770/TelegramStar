// Telegram WebApp
const tg = window.Telegram?.WebApp;

// Пакеты
const packages = [
    { id: 1, stars: 50, price: 50, bonus: 0 },
    { id: 2, stars: 100, price: 100, bonus: 5, popular: true },
    { id: 3, stars: 250, price: 250, bonus: 15 },
    { id: 4, stars: 500, price: 500, bonus: 50, popular: true },
    { id: 5, stars: 1000, price: 1000, bonus: 150 }
];

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    if (tg) {
        tg.ready();
        tg.expand();
        initUser();
    }
    renderPackages();
});

function initUser() {
    const user = tg?.initDataUnsafe?.user;
    if (user) {
        document.getElementById('userName').textContent = 
            user.first_name + (user.last_name ? ' ' + user.last_name : '');
        document.getElementById('userId').textContent = 'ID: ' + user.id;
    }
}

function renderPackages() {
    const grid = document.getElementById('packagesGrid');
    if (!grid) return;
    
    grid.innerHTML = packages.map(pkg => `
        <div class="package-card ${pkg.popular ? 'popular' : ''}" onclick="buyPackage(${pkg.id})">
            <div class="package-stars">⭐</div>
            <div class="package-amount">${pkg.stars}</div>
            ${pkg.bonus > 0 ? `<div class="package-bonus">+${pkg.bonus} бонус</div>` : '<div style="height:24px"></div>'}
            <div class="package-price">${pkg.price} Stars</div>
        </div>
    `).join('');
}

function buyPackage(id) {
    const pkg = packages.find(p => p.id === id);
    if (!pkg) return;
    
    if (tg) {
        tg.showConfirm(
            `Купить ${pkg.stars} ⭐ за ${pkg.price} Stars?`,
            (ok) => {
                if (ok) {
                    tg.sendData(JSON.stringify({ action: 'buy', package_id: id }));
                }
            }
        );
    } else {
        alert(`Покупка ${pkg.stars} ⭐ за ${pkg.price} Stars`);
    }
}
