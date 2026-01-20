// Telegram WebApp instance
const tg = window.Telegram.WebApp;

// Инициализация
tg.ready();
tg.expand();

// Пакеты звёзд
const packages = [
    { id: 1, stars: 50, price: 50, bonus: 0 },
    { id: 2, stars: 100, price: 100, bonus: 5, popular: true },
    { id: 3, stars: 250, price: 250, bonus: 15 },
    { id: 4, stars: 500, price: 500, bonus: 50, popular: true },
    { id: 5, stars: 1000, price: 1000, bonus: 150 },
    { id: 6, stars: 2500, price: 2500, bonus: 500 }
];

// Тексты политик
const privacyPolicy = `
<h4>1. Сбор данных</h4>
<p>Мы собираем только необходимые данные: Telegram ID пользователя, Username (при наличии), историю покупок.</p>

<h4>2. Использование данных</h4>
<p>Данные используются исключительно для обработки заказов, поддержки пользователей и улучшения сервиса.</p>

<h4>3. Защита данных</h4>
<p>Мы не передаём данные третьим лицам. Все данные хранятся в зашифрованном виде. Доступ имеют только администраторы.</p>

<h4>4. Удаление данных</h4>
<p>Вы можете запросить удаление ваших данных, обратившись в поддержку.</p>
`;

const termsOfService = `
<h4>1. Общие положения</h4>
<p>Используя данный сервис, вы соглашаетесь с условиями ниже.</p>

<h4>2. Услуги</h4>
<p>Мы предоставляем услуги по продаже Telegram Stars. Доставка осуществляется автоматически после оплаты.</p>

<h4>3. Оплата</h4>
<p>Оплата производится через Telegram Payments. Все платежи являются окончательными. Возврат возможен только при технических сбоях.</p>

<h4>4. Ограничения</h4>
<p>Запрещено использовать бота для мошенничества. Запрещено перепродавать приобретённые звёзды. Нарушители блокируются без возврата средств.</p>
`;

const aboutText = `
<h4>О сервисе Stars Shop</h4>
<p>Stars Shop — это удобный сервис для покупки Telegram Stars. Мы предлагаем лучшие цены и моментальную доставку.</p>

<h4>Наши преимущества</h4>
<p>• Моментальная доставка звёзд<br>
• Выгодные бонусы к пакетам<br>
• Безопасные платежи<br>
• Поддержка 24/7</p>

<h4>Контакты</h4>
<p>Если у вас есть вопросы, обращайтесь в нашу поддержку через бота.</p>
`;

// DOM элементы
const packagesGrid = document.getElementById('packagesGrid');
const userName = document.getElementById('userName');
const userStats = document.getElementById('userStats');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const modalClose = document.getElementById('modalClose');

// Навигация
const navButtons = document.querySelectorAll('.nav-btn');
const shopContent = document.querySelector('.packages-section');
const featuresSection = document.querySelector('.features-section');
const historyTab = document.getElementById('historyTab');
const supportTab = document.getElementById('supportTab');
const infoTab = document.getElementById('infoTab');
const userCard = document.querySelector('.user-card');

// Инициализация пользователя
function initUser() {
    const user = tg.initDataUnsafe?.user;
    if (user) {
        userName.textContent = user.first_name + (user.last_name ? ' ' + user.last_name : '');
        
        // Применяем тему Telegram
        document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
        document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f0f0f0');
    }
}

// Рендер пакетов
function renderPackages() {
    packagesGrid.innerHTML = packages.map(pkg => `
        <div class="package-card ${pkg.popular ? 'popular' : ''}" data-id="${pkg.id}">
            <div class="package-stars">⭐</div>
            <div class="package-amount">${pkg.stars}</div>
            ${pkg.bonus > 0 ? `<div class="package-bonus">+${pkg.bonus} бонус</div>` : '<div style="height: 28px;"></div>'}
            <div class="package-price">${pkg.price} Stars</div>
            <button class="package-btn">Купить</button>
        </div>
    `).join('');

    // Добавляем обработчики
    document.querySelectorAll('.package-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            buyPackage(id);
        });
    });
}

// Покупка пакета
function buyPackage(packageId) {
    const pkg = packages.find(p => p.id === packageId);
    if (!pkg) return;

    // Показываем подтверждение
    tg.showConfirm(
        `Купить ${pkg.stars} ⭐${pkg.bonus > 0 ? ` (+${pkg.bonus} бонус)` : ''} за ${pkg.price} Stars?`,
        (confirmed) => {
            if (confirmed) {
                // Отправляем данные боту
                tg.sendData(JSON.stringify({
                    action: 'buy',
                    package_id: packageId,
                    stars: pkg.stars,
                    bonus: pkg.bonus,
                    price: pkg.price
                }));
                
                tg.showAlert('Заказ отправлен! Перейдите в бота для оплаты.');
            }
        }
    );
}

// Навигация по табам
navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // Обновляем активную кнопку
        navButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Скрываем все табы
        shopContent.style.display = 'none';
        featuresSection.style.display = 'none';
        historyTab.style.display = 'none';
        supportTab.style.display = 'none';
        infoTab.style.display = 'none';
        userCard.style.display = 'none';
        
        // Показываем нужный таб
        switch(tab) {
            case 'shop':
                shopContent.style.display = 'block';
                featuresSection.style.display = 'block';
                userCard.style.display = 'flex';
                break;
            case 'history':
                historyTab.style.display = 'block';
                break;
            case 'support':
                supportTab.style.display = 'block';
                break;
            case 'info':
                infoTab.style.display = 'block';
                break;
        }
    });
});

// Модальное окно
function openModal(title, content) {
    modalTitle.textContent = title;
    modalBody.innerHTML = content;
    modal.classList.add('active');
}

function closeModal() {
    modal.classList.remove('active');
}

modalClose.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
});

// Info карточки
document.getElementById('privacyCard')?.addEventListener('click', () => {
    openModal('Политика конфиденциальности', privacyPolicy);
});

document.getElementById('termsCard')?.addEventListener('click', () => {
    openModal('Пользовательское соглашение', termsOfService);
});

document.getElementById('aboutCard')?.addEventListener('click', () => {
    openModal('О сервисе', aboutText);
});

// Кнопка поддержки
document.getElementById('supportBtn')?.addEventListener('click', () => {
    tg.sendData(JSON.stringify({ action: 'support' }));
    tg.close();
});

// Хаптик фидбек при нажатии
document.querySelectorAll('button, .package-card, .info-card').forEach(el => {
    el.addEventListener('click', () => {
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('light');
        }
    });
});

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initUser();
    renderPackages();
    
    // Настраиваем MainButton если нужно
    tg.MainButton.hide();
});
