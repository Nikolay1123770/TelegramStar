import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# ============================================
# КОНФИГУРАЦИЯ
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
WEBAPP_PORT = int(os.getenv("PORT", 3000))
SUPPORT_USERNAME = "wixyeez"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================
# ВСТРОЕННЫЙ HTML
# ============================================

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Telegram Star Shop</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-card: #252525;
            --text-primary: #ffffff;
            --text-secondary: #888888;
            --accent: #7c3aed;
            --accent-hover: #6d28d9;
            --gold: #ffd700;
            --gold-dark: #b8860b;
            --green: #10b981;
            --red: #ef4444;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }
        
        .app {
            max-width: 500px;
            margin: 0 auto;
            padding-bottom: 80px;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
        }
        
        .header-content {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header-icon {
            font-size: 40px;
            animation: float 3s ease-in-out infinite;
        }
        
        .header-text h1 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        
        .header-text p {
            font-size: 13px;
            opacity: 0.9;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        /* User Card */
        .user-card {
            display: flex;
            align-items: center;
            gap: 15px;
            background: var(--bg-card);
            margin: -20px 16px 20px;
            padding: 20px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            position: relative;
            z-index: 10;
            animation: slideDown 0.5s ease;
        }
        
        @keyframes slideDown {
            from { transform: translateY(-100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .user-avatar {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }
        
        .user-info {
            flex: 1;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 4px;
        }
        
        .user-id {
            color: var(--text-secondary);
            font-size: 13px;
        }
        
        .user-badge {
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            white-space: nowrap;
        }
        
        /* Section */
        .section {
            padding: 0 16px;
            margin-bottom: 30px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 700;
        }
        
        .section-link {
            color: var(--accent);
            font-size: 14px;
            text-decoration: none;
            font-weight: 500;
        }
        
        /* Packages Grid */
        .packages-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .package-card {
            background: var(--bg-card);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 2px solid transparent;
        }
        
        .package-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, var(--accent), var(--gold));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .package-card:hover::before,
        .package-card:active::before {
            opacity: 0.1;
        }
        
        .package-card:active {
            transform: scale(0.95);
        }
        
        .package-card.popular {
            border-color: var(--gold);
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
        }
        
        .popular-badge {
            position: absolute;
            top: 10px;
            right: -25px;
            background: var(--gold);
            color: #000;
            padding: 4px 30px;
            font-size: 10px;
            font-weight: 700;
            transform: rotate(45deg);
            box-shadow: 0 2px 10px rgba(255, 215, 0, 0.5);
        }
        
        .package-icon {
            font-size: 48px;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .package-amount {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            position: relative;
            z-index: 1;
        }
        
        .package-bonus {
            background: linear-gradient(135deg, var(--green), #059669);
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
        }
        
        .package-price {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
        }
        
        .package-btn {
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            width: 100%;
            position: relative;
            z-index: 1;
            transition: transform 0.2s;
        }
        
        .package-btn:active {
            transform: scale(0.95);
        }
        
        /* Stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: var(--bg-card);
            padding: 16px;
            border-radius: 16px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--gold);
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 11px;
            color: var(--text-secondary);
        }
        
        /* Features */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .feature-card {
            background: var(--bg-card);
            padding: 20px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: transform 0.2s;
        }
        
        .feature-card:active {
            transform: scale(0.98);
        }
        
        .feature-icon {
            font-size: 32px;
        }
        
        .feature-content h3 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .feature-content p {
            font-size: 11px;
            color: var(--text-secondary);
        }
        
        /* Bottom Nav */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-secondary);
            display: flex;
            justify-content: space-around;
            padding: 10px 0 20px;
            box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.3);
            z-index: 100;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 8px 16px;
            cursor: pointer;
            color: var(--text-secondary);
            transition: color 0.2s;
            background: none;
            border: none;
        }
        
        .nav-item.active {
            color: var(--accent);
        }
        
        .nav-icon {
            font-size: 24px;
        }
        
        .nav-label {
            font-size: 11px;
            font-weight: 500;
        }
        
        /* Tab Content */
        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* History */
        .history-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .history-item {
            background: var(--bg-card);
            padding: 16px;
            border-radius: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .history-icon {
            font-size: 32px;
            margin-right: 12px;
        }
        
        .history-info {
            flex: 1;
        }
        
        .history-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .history-date {
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .history-amount {
            font-size: 18px;
            font-weight: 700;
            color: var(--gold);
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
        }
        
        .empty-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.3;
        }
        
        .empty-text {
            color: var(--text-secondary);
            font-size: 16px;
        }
        
        /* Support */
        .support-card {
            background: var(--bg-card);
            padding: 24px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .support-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }
        
        .support-card h2 {
            font-size: 20px;
            margin-bottom: 12px;
        }
        
        .support-card p {
            color: var(--text-secondary);
            margin-bottom: 20px;
        }
        
        .support-btn {
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            display: inline-block;
            text-decoration: none;
            transition: transform 0.2s;
        }
        
        .support-btn:active {
            transform: scale(0.95);
        }
        
        /* Info Links */
        .info-links {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .info-link {
            background: var(--bg-card);
            padding: 18px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 15px;
            text-decoration: none;
            color: var(--text-primary);
            transition: transform 0.2s;
        }
        
        .info-link:active {
            transform: scale(0.98);
        }
        
        .info-link-icon {
            font-size: 28px;
        }
        
        .info-link-text {
            flex: 1;
            font-weight: 500;
        }
        
        .info-link-arrow {
            color: var(--text-secondary);
        }
        
        /* Loading */
        .loading {
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid var(--bg-card);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.2s ease;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: var(--bg-secondary);
            border-radius: 24px;
            padding: 30px;
            max-width: 90%;
            width: 400px;
            text-align: center;
            position: relative;
            animation: scaleIn 0.3s ease;
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.9); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        .modal-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }
        
        .modal-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .modal-text {
            color: var(--text-secondary);
            margin-bottom: 24px;
            line-height: 1.5;
        }
        
        .modal-buttons {
            display: flex;
            gap: 12px;
        }
        
        .modal-btn {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
        }
        
        .modal-btn-primary {
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: white;
        }
        
        .modal-btn-secondary {
            background: var(--bg-card);
            color: var(--text-primary);
        }
        
        /* Animations */
        .fade-in { animation: fadeIn 0.3s ease; }
        .slide-up { animation: slideUp 0.3s ease; }
        
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="app">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <div class="header-icon">⭐</div>
                <div class="header-text">
                    <h1>Telegram Star Shop</h1>
                    <p>Покупайте звёзды выгодно и безопасно</p>
                </div>
            </div>
        </header>

        <!-- User Card -->
        <div class="user-card">
            <div class="user-avatar" id="userAvatar">👤</div>
            <div class="user-info">
                <div class="user-name" id="userName">Загрузка...</div>
                <div class="user-id" id="userId">ID: —</div>
            </div>
            <div class="user-badge">VIP</div>
        </div>

        <!-- Main Tab -->
        <div id="mainTab" class="tab-content active">
            <!-- Stats -->
            <div class="section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalStars">0</div>
                        <div class="stat-label">Куплено</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="totalPurchases">0</div>
                        <div class="stat-label">Покупок</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="bonusStars">0</div>
                        <div class="stat-label">Бонусов</div>
                    </div>
                </div>
            </div>

            <!-- Packages -->
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">🛒 Выберите пакет</h2>
                </div>
                <div class="packages-grid" id="packagesGrid"></div>
            </div>

            <!-- Features -->
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">✨ Почему мы?</h2>
                </div>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-content">
                            <h3>Мгновенно</h3>
                            <p>Доставка за секунды</p>
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <div class="feature-content">
                            <h3>Безопасно</h3>
                            <p>Официальные платежи</p>
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎁</div>
                        <div class="feature-content">
                            <h3>Бонусы</h3>
                            <p>До 500 звёзд</p>
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💬</div>
                        <div class="feature-content">
                            <h3>Поддержка</h3>
                            <p>Всегда на связи</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- History Tab -->
        <div id="historyTab" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">📦 История покупок</h2>
                </div>
                <div class="history-list" id="historyList">
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <div class="empty-text">У вас пока нет покупок</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Support Tab -->
        <div id="supportTab" class="tab-content">
            <div class="section">
                <div class="support-card">
                    <div class="support-icon">💬</div>
                    <h2>Служба поддержки</h2>
                    <p>Мы всегда готовы помочь вам с любыми вопросами!</p>
                    <a href="https://t.me/wixyeez" class="support-btn" target="_blank">
                        Написать в поддержку
                    </a>
                </div>

                <div class="info-links">
                    <a href="https://telegra.ph/Polzovatelskoe-soglashenie-08-15-10" class="info-link" target="_blank">
                        <div class="info-link-icon">📋</div>
                        <div class="info-link-text">Пользовательское соглашение</div>
                        <div class="info-link-arrow">→</div>
                    </a>
                    <a href="https://telegra.ph/Politika-konfidencialnosti-08-15-17" class="info-link" target="_blank">
                        <div class="info-link-icon">📜</div>
                        <div class="info-link-text">Политика конфиденциальности</div>
                        <div class="info-link-arrow">→</div>
                    </a>
                </div>
            </div>
        </div>

        <!-- Bottom Navigation -->
        <nav class="bottom-nav">
            <button class="nav-item active" data-tab="main">
                <span class="nav-icon">🏠</span>
                <span class="nav-label">Главная</span>
            </button>
            <button class="nav-item" data-tab="history">
                <span class="nav-icon">📦</span>
                <span class="nav-label">Покупки</span>
            </button>
            <button class="nav-item" data-tab="support">
                <span class="nav-icon">💬</span>
                <span class="nav-label">Поддержка</span>
            </button>
        </nav>
    </div>

    <!-- Modal -->
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-icon" id="modalIcon">⭐</div>
            <h2 class="modal-title" id="modalTitle">Подтверждение покупки</h2>
            <p class="modal-text" id="modalText">Вы уверены?</p>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-secondary" id="modalCancel">Отмена</button>
                <button class="modal-btn modal-btn-primary" id="modalConfirm">Купить</button>
            </div>
        </div>
    </div>

    <script>
        // Telegram WebApp
        const tg = window.Telegram?.WebApp;
        if (tg) {
            tg.ready();
            tg.expand();
            tg.enableClosingConfirmation();
        }

        // Packages data
        const packages = [
            { id: 1, stars: 50, price: 50, bonus: 0, icon: '⭐' },
            { id: 2, stars: 100, price: 100, bonus: 5, popular: true, icon: '✨' },
            { id: 3, stars: 250, price: 250, bonus: 15, icon: '💫' },
            { id: 4, stars: 500, price: 500, bonus: 50, popular: true, icon: '🌟' },
            { id: 5, stars: 1000, price: 1000, bonus: 150, icon: '⭐' },
            { id: 6, stars: 2500, price: 2500, bonus: 500, icon: '✨' }
        ];

        // User data (simulated)
        let userData = {
            totalStars: 0,
            totalPurchases: 0,
            bonusStars: 0,
            history: []
        };

        // Elements
        const packagesGrid = document.getElementById('packagesGrid');
        const historyList = document.getElementById('historyList');
        const modal = document.getElementById('modal');
        const modalIcon = document.getElementById('modalIcon');
        const modalTitle = document.getElementById('modalTitle');
        const modalText = document.getElementById('modalText');
        const modalConfirm = document.getElementById('modalConfirm');
        const modalCancel = document.getElementById('modalCancel');

        // Init user
        function initUser() {
            const user = tg?.initDataUnsafe?.user;
            if (user) {
                const fullName = user.first_name + (user.last_name ? ' ' + user.last_name : '');
                document.getElementById('userName').textContent = fullName;
                document.getElementById('userId').textContent = 'ID: ' + user.id;
                
                // Set avatar emoji based on user ID
                const avatars = ['👨', '👩', '🧑', '👤', '😊', '🎭', '🎨', '🎯'];
                document.getElementById('userAvatar').textContent = avatars[user.id % avatars.length];
            }

            // Apply Telegram theme
            if (tg?.themeParams) {
                const root = document.documentElement;
                if (tg.themeParams.bg_color) root.style.setProperty('--bg-primary', tg.themeParams.bg_color);
                if (tg.themeParams.text_color) root.style.setProperty('--text-primary', tg.themeParams.text_color);
                if (tg.themeParams.hint_color) root.style.setProperty('--text-secondary', tg.themeParams.hint_color);
                if (tg.themeParams.button_color) root.style.setProperty('--accent', tg.themeParams.button_color);
            }

            // Load user data from localStorage
            const saved = localStorage.getItem('userData');
            if (saved) {
                userData = JSON.parse(saved);
                updateStats();
                updateHistory();
            }
        }

        // Render packages
        function renderPackages() {
            packagesGrid.innerHTML = packages.map((pkg, index) => `
                <div class="package-card ${pkg.popular ? 'popular' : ''}" 
                     onclick="selectPackage(${pkg.id})"
                     style="animation-delay: ${index * 0.1}s">
                    ${pkg.popular ? '<div class="popular-badge">ХИТ</div>' : ''}
                    <div class="package-icon">${pkg.icon}</div>
                    <div class="package-amount">${pkg.stars}</div>
                    ${pkg.bonus > 0 ? `<div class="package-bonus">+${pkg.bonus} 🎁</div>` : '<div style="height: 28px"></div>'}
                    <div class="package-price">${pkg.price} Stars</div>
                    <button class="package-btn">Купить</button>
                </div>
            `).join('');
        }

        // Select package
        let selectedPackage = null;
        function selectPackage(id) {
            selectedPackage = packages.find(p => p.id === id);
            if (!selectedPackage) return;

            // Haptic feedback
            if (tg?.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('medium');
            }

            // Show modal
            modalIcon.textContent = selectedPackage.icon;
            modalTitle.textContent = `Покупка ${selectedPackage.stars} ⭐`;
            modalText.innerHTML = `
                Пакет: <b>${selectedPackage.stars} звёзд</b><br>
                ${selectedPackage.bonus > 0 ? `Бонус: <b>+${selectedPackage.bonus} звёзд</b><br>` : ''}
                Цена: <b>${selectedPackage.price} Stars</b><br><br>
                Подтвердите покупку
            `;
            modal.classList.add('active');
        }

        // Confirm purchase
        modalConfirm.onclick = () => {
            if (!selectedPackage) return;
            
            modal.classList.remove('active');

            // In real app, send to bot for payment
            if (tg) {
                tg.sendData(JSON.stringify({
                    action: 'buy',
                    package_id: selectedPackage.id,
                    stars: selectedPackage.stars,
                    bonus: selectedPackage.bonus,
                    price: selectedPackage.price
                }));

                // Show success (simulated)
                setTimeout(() => {
                    showSuccess(selectedPackage);
                }, 500);
            } else {
                // Demo mode - simulate purchase
                showSuccess(selectedPackage);
            }
        };

        // Cancel modal
        modalCancel.onclick = () => {
            modal.classList.remove('active');
            selectedPackage = null;
        };

        // Close modal on background click
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                selectedPackage = null;
            }
        };

        // Show success
        function showSuccess(pkg) {
            // Update user data
            userData.totalStars += pkg.stars + pkg.bonus;
            userData.bonusStars += pkg.bonus;
            userData.totalPurchases++;
            userData.history.unshift({
                id: Date.now(),
                stars: pkg.stars,
                bonus: pkg.bonus,
                price: pkg.price,
                date: new Date().toISOString()
            });

            // Save to localStorage
            localStorage.setItem('userData', JSON.stringify(userData));

            // Update UI
            updateStats();
            updateHistory();

            // Show success modal
            modalIcon.textContent = '✅';
            modalTitle.textContent = 'Успешно!';
            modalText.innerHTML = `
                Вы получили:<br>
                <b style="color: var(--gold)">${pkg.stars + pkg.bonus} ⭐</b><br>
                ${pkg.bonus > 0 ? `<small style="color: var(--green)">Включая ${pkg.bonus} бонусных</small>` : ''}
            `;
            modalConfirm.style.display = 'none';
            modalCancel.textContent = 'Отлично!';
            modal.classList.add('active');

            setTimeout(() => {
                modalConfirm.style.display = 'block';
                modalCancel.textContent = 'Отмена';
            }, 3000);

            // Haptic
            if (tg?.HapticFeedback) {
                tg.HapticFeedback.notificationOccurred('success');
            }
        }

        // Update stats
        function updateStats() {
            document.getElementById('totalStars').textContent = userData.totalStars;
            document.getElementById('totalPurchases').textContent = userData.totalPurchases;
            document.getElementById('bonusStars').textContent = userData.bonusStars;
        }

        // Update history
        function updateHistory() {
            if (userData.history.length === 0) {
                historyList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <div class="empty-text">У вас пока нет покупок</div>
                    </div>
                `;
                return;
            }

            historyList.innerHTML = userData.history.map(item => {
                const date = new Date(item.date);
                const dateStr = date.toLocaleDateString('ru-RU');
                const timeStr = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                
                return `
                    <div class="history-item">
                        <div class="history-icon">✅</div>
                        <div class="history-info">
                            <div class="history-title">${item.stars} + ${item.bonus} звёзд</div>
                            <div class="history-date">${dateStr} в ${timeStr}</div>
                        </div>
                        <div class="history-amount">${item.price} ⭐</div>
                    </div>
                `;
            }).join('');
        }

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.onclick = () => {
                const tab = item.dataset.tab;
                
                // Update nav
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                // Update tabs
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                document.getElementById(tab + 'Tab').classList.add('active');
                
                // Haptic
                if (tg?.HapticFeedback) {
                    tg.HapticFeedback.impactOccurred('light');
                }
            };
        });

        // Init
        document.addEventListener('DOMContentLoaded', () => {
            initUser();
            renderPackages();
        });
    </script>
</body>
</html>
"""

# ============================================
# ВЕБ-СЕРВЕР
# ============================================

async def handle_index(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')

async def handle_health(request):
    return web.json_response({"status": "ok", "service": "telegram-stars-shop"})

# ============================================
# TELEGRAM BOT
# ============================================

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

WELCOME = f"""
🌟 <b>Добро пожаловать в Telegram Star Shop!</b>

Здесь вы можете быстро и безопасно приобрести звёзды Telegram.

⭐ <b>Наши преимущества:</b>
• Моментальная доставка
• Выгодные бонусы до 500 звёзд
• Безопасные платежи через Telegram
• Круглосуточная поддержка

Выберите действие ниже 👇
"""


def main_kb():
    builder = InlineKeyboardBuilder()
    
    # Кнопка открытия MiniApp
    builder.row(InlineKeyboardButton(
        text="🌟 Открыть Telegram Star Shop",
        web_app=WebAppInfo(url="https://telegramstar.bothost.ru")
    ))
    
    # Поддержка
    builder.row(InlineKeyboardButton(
        text="💬 Поддержка",
        url=f"https://t.me/{SUPPORT_USERNAME}"
    ))
    
    # Политики
    builder.row(InlineKeyboardButton(
        text="📋 Пользовательское соглашение",
        url="https://telegra.ph/Polzovatelskoe-soglashenie-08-15-10"
    ))
    
    builder.row(InlineKeyboardButton(
        text="📜 Политика конфиденциальности",
        url="https://telegra.ph/Politika-konfidencialnosti-08-15-17"
    ))
    
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    logger.info(f"User {user.id} (@{user.username}) started bot")
    
    await message.answer(
        text=WELCOME,
        reply_markup=main_kb()
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Обработка данных из MiniApp"""
    import json
    
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        
        if action == 'buy':
            package_id = data.get('package_id')
            stars = data.get('stars')
            bonus = data.get('bonus')
            price = data.get('price')
            
            # Здесь должна быть логика создания инвойса для оплаты
            # Пока просто подтверждаем получение
            await message.answer(
                f"✅ Заказ получен!\n\n"
                f"📦 Пакет: {stars} + {bonus} звёзд\n"
                f"💰 Цена: {price} Stars\n\n"
                f"💳 Функция оплаты в разработке.\n"
                f"Скоро вы сможете оплачивать покупки прямо в боте!"
            )
            
    except Exception as e:
        logger.error(f"Error processing web app data: {e}")
        await message.answer("❌ Произошла ошибка при обработке заказа")


@router.message()
async def handle_any_message(message: Message):
    """Обработка любых других сообщений"""
    await message.answer(
        "Используйте кнопку меню ниже для доступа к магазину 👇",
        reply_markup=main_kb()
    )


dp.include_router(router)

# ============================================
# ЗАПУСК
# ============================================

async def start_web():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/health', handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
    await site.start()
    logger.info(f"🌐 Web server started on port {WEBAPP_PORT}")
    logger.info(f"🔗 MiniApp URL: https://telegramstar.bothost.ru")


async def start_bot():
    logger.info("🤖 Starting Telegram bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    logger.info("=" * 50)
    logger.info("🚀 TELEGRAM STAR SHOP")
    logger.info("=" * 50)
    
    await asyncio.gather(
        start_web(),
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
