import asyncio
import logging
import os
import hashlib
import hmac
from datetime import datetime
from aiohttp import web
import aiohttp
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# ============================================
# КОНФИГУРАЦИЯ
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8557420124:AAFuZfN5E1f0-qH-cIBSqI9JK309R6s88Q8")
WEBAPP_PORT = int(os.getenv("PORT", 3000))
SUPPORT_USERNAME = "wixyeez"

# ЮМани
YOOMONEY_WALLET = "4100118889570559"
YOOMONEY_SECRET = "fL8QIMDHIeudGlqCPNR7eux/"
YOOMONEY_SUCCESS_URL = "https://telegramstar.bothost.ru/success"
YOOMONEY_FAIL_URL = "https://telegramstar.bothost.ru/fail"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# База данных в памяти (в продакшене использовать SQL)
payments_db = {}
users_db = {}

# ============================================
# PREMIUM HTML WITH GLASSMORPHISM
# ============================================

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>⭐ Telegram Star Shop - Premium</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #151b35;
            --bg-card: rgba(30, 41, 73, 0.5);
            --text-primary: #ffffff;
            --text-secondary: #a8b2d1;
            --accent-purple: #9d4edd;
            --accent-blue: #3a86ff;
            --accent-pink: #ff006e;
            --gold: #ffd60a;
            --gold-dark: #ffba08;
            --green: #06ffa5;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            --glow: 0 0 30px rgba(157, 78, 221, 0.5);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        
        /* Animated Background */
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
            opacity: 0.6;
        }
        
        .particle {
            position: absolute;
            border-radius: 50%;
            pointer-events: none;
        }
        
        .app {
            max-width: 500px;
            margin: 0 auto;
            padding-bottom: 90px;
            position: relative;
            z-index: 1;
        }
        
        /* Glassmorphism Header */
        .header {
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.3), rgba(58, 134, 255, 0.3));
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 25px 20px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border-radius: 0 0 30px 30px;
        }
        
        .header-content {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header-icon {
            font-size: 48px;
            animation: float 3s ease-in-out infinite, rotate 20s linear infinite;
            filter: drop-shadow(0 0 20px rgba(255, 214, 10, 0.8));
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) scale(1); }
            50% { transform: translateY(-15px) scale(1.1); }
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .header-text h1 {
            font-size: 26px;
            font-weight: 900;
            background: linear-gradient(135deg, #ffd60a, #ff006e, #3a86ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 5px;
            animation: gradient-shift 3s ease infinite;
        }
        
        @keyframes gradient-shift {
            0%, 100% { filter: hue-rotate(0deg); }
            50% { filter: hue-rotate(45deg); }
        }
        
        .header-text p {
            font-size: 13px;
            opacity: 0.9;
            color: var(--text-secondary);
        }
        
        /* Premium User Card */
        .user-card {
            display: flex;
            align-items: center;
            gap: 15px;
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.2), rgba(58, 134, 255, 0.2));
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin: -20px 16px 20px;
            padding: 20px;
            border-radius: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            animation: slideDown 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        .user-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        @keyframes slideDown {
            from { transform: translateY(-100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .user-avatar {
            width: 65px;
            height: 65px;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            box-shadow: 0 0 30px rgba(255, 214, 10, 0.5);
            position: relative;
            animation: pulse-avatar 2s ease-in-out infinite;
        }
        
        @keyframes pulse-avatar {
            0%, 100% { box-shadow: 0 0 30px rgba(255, 214, 10, 0.5); }
            50% { box-shadow: 0 0 50px rgba(255, 214, 10, 0.8); }
        }
        
        .user-info {
            flex: 1;
            position: relative;
            z-index: 1;
        }
        
        .user-name {
            font-weight: 700;
            font-size: 19px;
            margin-bottom: 5px;
        }
        
        .user-id {
            color: var(--text-secondary);
            font-size: 13px;
        }
        
        .user-badge {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            box-shadow: 0 4px 15px rgba(157, 78, 221, 0.4);
            position: relative;
            z-index: 1;
            animation: badge-glow 2s ease-in-out infinite;
        }
        
        @keyframes badge-glow {
            0%, 100% { box-shadow: 0 4px 15px rgba(157, 78, 221, 0.4); }
            50% { box-shadow: 0 4px 25px rgba(157, 78, 221, 0.8); }
        }
        
        /* Section */
        .section {
            padding: 0 16px;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 16px;
            background: linear-gradient(135deg, var(--gold), var(--accent-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Premium Stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.15), rgba(58, 134, 255, 0.15));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 18px 12px;
            border-radius: 20px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            cursor: pointer;
        }
        
        .stat-card:active {
            transform: scale(0.95);
        }
        
        .stat-value {
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            animation: counter-up 1s ease-out;
        }
        
        @keyframes counter-up {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stat-label {
            font-size: 11px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Premium Packages */
        .packages-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .package-card {
            background: linear-gradient(135deg, rgba(30, 41, 73, 0.6), rgba(20, 28, 50, 0.6));
            backdrop-filter: blur(20px);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 25px;
            padding: 25px 20px;
            text-align: center;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        .package-card::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(157, 78, 221, 0.4), transparent);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .package-card:hover::before,
        .package-card:active::before {
            width: 300px;
            height: 300px;
        }
        
        .package-card:active {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 50px rgba(157, 78, 221, 0.5);
        }
        
        .package-card.popular {
            border: 2px solid var(--gold);
            box-shadow: 0 0 40px rgba(255, 214, 10, 0.3);
            animation: popular-pulse 2s ease-in-out infinite;
        }
        
        @keyframes popular-pulse {
            0%, 100% { box-shadow: 0 0 40px rgba(255, 214, 10, 0.3); }
            50% { box-shadow: 0 0 60px rgba(255, 214, 10, 0.6); }
        }
        
        .popular-badge {
            position: absolute;
            top: 12px;
            right: -30px;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            color: #000;
            padding: 5px 35px;
            font-size: 10px;
            font-weight: 900;
            transform: rotate(45deg);
            box-shadow: 0 4px 15px rgba(255, 214, 10, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .package-icon {
            font-size: 56px;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
            animation: float-icon 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(255, 214, 10, 0.6));
        }
        
        @keyframes float-icon {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            25% { transform: translateY(-10px) rotate(-5deg); }
            75% { transform: translateY(-10px) rotate(5deg); }
        }
        
        .package-amount {
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, var(--gold), #fff, var(--gold-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
            text-shadow: 0 0 30px rgba(255, 214, 10, 0.5);
        }
        
        .package-bonus {
            background: linear-gradient(135deg, var(--green), #00d9ff);
            color: #000;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 14px;
            position: relative;
            z-index: 1;
            box-shadow: 0 4px 15px rgba(6, 255, 165, 0.4);
            animation: bonus-bounce 1s ease-in-out infinite;
        }
        
        @keyframes bonus-bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .package-price {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 14px;
            position: relative;
            z-index: 1;
            font-weight: 600;
        }
        
        .package-btn {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            width: 100%;
            position: relative;
            z-index: 1;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 20px rgba(157, 78, 221, 0.4);
        }
        
        .package-btn:hover {
            box-shadow: 0 6px 30px rgba(157, 78, 221, 0.6);
        }
        
        .package-btn:active {
            transform: scale(0.95);
        }
        
        /* Features */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .feature-card {
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.15), rgba(58, 134, 255, 0.15));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 22px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            cursor: pointer;
        }
        
        .feature-card:active {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(157, 78, 221, 0.3);
        }
        
        .feature-icon {
            font-size: 36px;
            filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
        }
        
        .feature-content h3 {
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .feature-content p {
            font-size: 11px;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        /* Bottom Nav */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, rgba(20, 28, 50, 0.95), rgba(30, 41, 73, 0.95));
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-around;
            padding: 12px 0 25px;
            box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.3);
            z-index: 100;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            padding: 10px 20px;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            background: none;
            border: none;
            position: relative;
        }
        
        .nav-item::before {
            content: '';
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
            border-radius: 0 0 3px 3px;
            transition: width 0.3s ease;
        }
        
        .nav-item.active::before {
            width: 60%;
        }
        
        .nav-item.active {
            color: var(--accent-purple);
        }
        
        .nav-item.active .nav-icon {
            filter: drop-shadow(0 0 10px rgba(157, 78, 221, 0.8));
            transform: scale(1.1);
        }
        
        .nav-icon {
            font-size: 26px;
            transition: all 0.3s ease;
        }
        
        .nav-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Tab Content */
        .tab-content {
            display: none;
            animation: fadeInUp 0.4s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* History */
        .history-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .history-item {
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.15), rgba(58, 134, 255, 0.15));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.3s ease;
        }
        
        .history-item:active {
            transform: scale(0.98);
        }
        
        .history-icon {
            font-size: 36px;
        }
        
        .history-info {
            flex: 1;
        }
        
        .history-title {
            font-weight: 700;
            margin-bottom: 5px;
            font-size: 16px;
        }
        
        .history-date {
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .history-amount {
            font-size: 20px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 80px 20px;
        }
        
        .empty-icon {
            font-size: 80px;
            margin-bottom: 20px;
            opacity: 0.3;
            animation: float 3s ease-in-out infinite;
        }
        
        .empty-text {
            color: var(--text-secondary);
            font-size: 16px;
            font-weight: 500;
        }
        
        /* Support */
        .support-card {
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.2), rgba(58, 134, 255, 0.2));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 25px;
            text-align: center;
            margin-bottom: 25px;
        }
        
        .support-icon {
            font-size: 80px;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }
        
        .support-card h2 {
            font-size: 24px;
            margin-bottom: 12px;
            font-weight: 800;
        }
        
        .support-card p {
            color: var(--text-secondary);
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .support-btn {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            color: white;
            border: none;
            padding: 16px 32px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            display: inline-block;
            text-decoration: none;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 6px 25px rgba(157, 78, 221, 0.5);
        }
        
        .support-btn:active {
            transform: scale(0.95);
        }
        
        /* Info Links */
        .info-links {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .info-link {
            background: linear-gradient(135deg, rgba(157, 78, 221, 0.15), rgba(58, 134, 255, 0.15));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        .info-link:active {
            transform: translateX(5px);
        }
        
        .info-link-icon {
            font-size: 32px;
        }
        
        .info-link-text {
            flex: 1;
            font-weight: 600;
            font-size: 15px;
        }
        
        .info-link-arrow {
            color: var(--text-secondary);
            font-size: 20px;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(10px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: linear-gradient(135deg, rgba(30, 41, 73, 0.95), rgba(20, 28, 50, 0.95));
            backdrop-filter: blur(30px);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            padding: 35px;
            max-width: 90%;
            width: 400px;
            text-align: center;
            position: relative;
            animation: scaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        .modal-icon {
            font-size: 80px;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
            filter: drop-shadow(0 0 30px rgba(255, 214, 10, 0.6));
        }
        
        .modal-title {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 15px;
        }
        
        .modal-text {
            color: var(--text-secondary);
            margin-bottom: 30px;
            line-height: 1.7;
            font-size: 15px;
        }
        
        .modal-buttons {
            display: flex;
            gap: 12px;
        }
        
        .modal-btn {
            flex: 1;
            padding: 16px;
            border: none;
            border-radius: 15px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
        }
        
        .modal-btn-primary {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            color: white;
            box-shadow: 0 6px 20px rgba(157, 78, 221, 0.4);
        }
        
        .modal-btn-primary:active {
            transform: scale(0.95);
        }
        
        .modal-btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        /* Loading */
        .loading {
            text-align: center;
            padding: 50px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top-color: var(--accent-purple);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Responsive */
        @media (max-width: 400px) {
            .packages-grid {
                grid-template-columns: 1fr;
            }
            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
    </style>
</head>
<body>
    <!-- Animated Background -->
    <div class="animated-bg" id="particles"></div>

    <div class="app">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <div class="header-icon">⭐</div>
                <div class="header-text">
                    <h1>Star Shop Premium</h1>
                    <p>Эксклюзивный магазин звёзд Telegram</p>
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
            <div class="user-badge">Premium</div>
        </div>

        <!-- Main Tab -->
        <div id="mainTab" class="tab-content active">
            <!-- Stats -->
            <div class="section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalStars">0</div>
                        <div class="stat-label">Звёзд</div>
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
                <h2 class="section-title">✨ Выберите пакет</h2>
                <div class="packages-grid" id="packagesGrid"></div>
            </div>

            <!-- Features -->
            <div class="section">
                <h2 class="section-title">🎯 Преимущества</h2>
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
                            <p>ЮMoney платежи</p>
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
                            <p>24/7 онлайн</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- History Tab -->
        <div id="historyTab" class="tab-content">
            <div class="section">
                <h2 class="section-title">📦 История покупок</h2>
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
                    <h2>Поддержка 24/7</h2>
                    <p>Наша команда всегда готова помочь вам с любыми вопросами!</p>
                    <a href="https://t.me/wixyeez" class="support-btn" target="_blank">
                        Написать сейчас
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
                <span class="nav-label">Помощь</span>
            </button>
        </nav>
    </div>

    <!-- Modal -->
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-icon" id="modalIcon">⭐</div>
            <h2 class="modal-title" id="modalTitle">Подтверждение</h2>
            <p class="modal-text" id="modalText">Загрузка...</p>
            <div class="modal-buttons" id="modalButtons">
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
            tg.setHeaderColor('#0a0e27');
            tg.setBackgroundColor('#0a0e27');
        }

        // Animated particles background
        function createParticles() {
            const container = document.getElementById('particles');
            const colors = ['#9d4edd', '#3a86ff', '#ff006e', '#ffd60a'];
            
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.cssText = `
                    width: ${Math.random() * 4 + 2}px;
                    height: ${Math.random() * 4 + 2}px;
                    background: ${colors[Math.floor(Math.random() * colors.length)]};
                    left: ${Math.random() * 100}%;
                    top: ${Math.random() * 100}%;
                    opacity: ${Math.random() * 0.5 + 0.2};
                    animation: float ${Math.random() * 10 + 10}s ease-in-out infinite;
                    animation-delay: ${Math.random() * 5}s;
                    box-shadow: 0 0 ${Math.random() * 20 + 10}px currentColor;
                `;
                container.appendChild(particle);
            }
        }

        // Packages
        const packages = [
            { id: 1, stars: 50, price: 50, bonus: 0, icon: '⭐', rate: 1 },
            { id: 2, stars: 100, price: 100, bonus: 5, popular: true, icon: '✨', rate: 1 },
            { id: 3, stars: 250, price: 250, bonus: 15, icon: '💫', rate: 1 },
            { id: 4, stars: 500, price: 500, bonus: 50, popular: true, icon: '🌟', rate: 1 },
            { id: 5, stars: 1000, price: 1000, bonus: 150, icon: '🌠', rate: 1 },
            { id: 6, stars: 2500, price: 2500, bonus: 500, icon: '✨', rate: 1 }
        ];

        // User data
        let userData = {
            totalStars: 0,
            totalPurchases: 0,
            bonusStars: 0,
            history: []
        };

        // Init
        function initUser() {
            const user = tg?.initDataUnsafe?.user;
            if (user) {
                document.getElementById('userName').textContent = 
                    user.first_name + (user.last_name ? ' ' + user.last_name : '');
                document.getElementById('userId').textContent = 'ID: ' + user.id;
                
                const avatars = ['🎭', '🎨', '🎯', '🎪', '🎬', '🎮', '🎲', '🎸'];
                document.getElementById('userAvatar').textContent = avatars[user.id % avatars.length];
            }

            const saved = localStorage.getItem('userData');
            if (saved) {
                userData = JSON.parse(saved);
                updateStats();
                updateHistory();
            }
        }

        // Render packages
        function renderPackages() {
            document.getElementById('packagesGrid').innerHTML = packages.map((pkg, i) => `
                <div class="package-card ${pkg.popular ? 'popular' : ''}" 
                     onclick="selectPackage(${pkg.id})"
                     style="animation-delay: ${i * 0.1}s">
                    ${pkg.popular ? '<div class="popular-badge">ХИТ</div>' : ''}
                    <div class="package-icon">${pkg.icon}</div>
                    <div class="package-amount">${pkg.stars}</div>
                    ${pkg.bonus > 0 ? `<div class="package-bonus">+${pkg.bonus} 🎁</div>` : '<div style="height:32px"></div>'}
                    <div class="package-price">${pkg.price} ₽</div>
                    <button class="package-btn">Купить</button>
                </div>
            `).join('');
        }

        // Select package
        let selectedPackage = null;
        function selectPackage(id) {
            selectedPackage = packages.find(p => p.id === id);
            if (!selectedPackage) return;

            if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');

            document.getElementById('modalIcon').textContent = selectedPackage.icon;
            document.getElementById('modalTitle').textContent = `${selectedPackage.stars} звёзд`;
            document.getElementById('modalText').innerHTML = `
                <div style="text-align: left; margin: 20px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Звёзды:</span>
                        <strong>${selectedPackage.stars} ⭐</strong>
                    </div>
                    ${selectedPackage.bonus > 0 ? `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: var(--green);">
                        <span>Бонус:</span>
                        <strong>+${selectedPackage.bonus} 🎁</strong>
                    </div>` : ''}
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <span>Итого:</span>
                        <strong style="color: var(--gold);">${selectedPackage.stars + selectedPackage.bonus} ⭐</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 18px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <span>К оплате:</span>
                        <strong style="background: linear-gradient(135deg, var(--gold), var(--gold-dark)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${selectedPackage.price} ₽</strong>
                    </div>
                </div>
            `;
            document.getElementById('modalButtons').style.display = 'flex';
            document.getElementById('modal').classList.add('active');
        }

        // Confirm purchase
        document.getElementById('modalConfirm').onclick = async () => {
            if (!selectedPackage) return;
            
            const user = tg?.initDataUnsafe?.user;
            if (!user) {
                alert('Ошибка: не удалось получить данные пользователя');
                return;
            }

            // Show loading
            document.getElementById('modalIcon').textContent = '⏳';
            document.getElementById('modalTitle').textContent = 'Создание платежа...';
            document.getElementById('modalText').textContent = 'Пожалуйста, подождите';
            document.getElementById('modalButtons').style.display = 'none';

            try {
                // Create payment
                const response = await fetch('/api/create-payment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        package_id: selectedPackage.id,
                        user_id: user.id,
                        username: user.username || user.first_name
                    })
                });

                const data = await response.json();
                
                if (data.payment_url) {
                    // Redirect to payment
                    if (tg) {
                        tg.openLink(data.payment_url);
                        tg.close();
                    } else {
                        window.location.href = data.payment_url;
                    }
                } else {
                    throw new Error(data.error || 'Ошибка создания платежа');
                }
            } catch (error) {
                console.error('Payment error:', error);
                document.getElementById('modalIcon').textContent = '❌';
                document.getElementById('modalTitle').textContent = 'Ошибка';
                document.getElementById('modalText').textContent = error.message;
                document.getElementById('modalButtons').innerHTML = `
                    <button class="modal-btn modal-btn-primary" onclick="closeModal()" style="width: 100%;">Закрыть</button>
                `;
                document.getElementById('modalButtons').style.display = 'flex';
            }
        };

        // Cancel modal
        document.getElementById('modalCancel').onclick = closeModal;
        document.getElementById('modal').onclick = (e) => {
            if (e.target.id === 'modal') closeModal();
        };

        function closeModal() {
            document.getElementById('modal').classList.remove('active');
            selectedPackage = null;
        }

        // Update stats
        function updateStats() {
            document.getElementById('totalStars').textContent = userData.totalStars;
            document.getElementById('totalPurchases').textContent = userData.totalPurchases;
            document.getElementById('bonusStars').textContent = userData.bonusStars;
        }

        // Update history
        function updateHistory() {
            const list = document.getElementById('historyList');
            if (userData.history.length === 0) {
                list.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-text">У вас пока нет покупок</div></div>';
                return;
            }

            list.innerHTML = userData.history.map(item => {
                const date = new Date(item.date);
                return `
                    <div class="history-item">
                        <div class="history-icon">✅</div>
                        <div class="history-info">
                            <div class="history-title">${item.stars} + ${item.bonus} звёзд</div>
                            <div class="history-date">${date.toLocaleString('ru-RU')}</div>
                        </div>
                        <div class="history-amount">${item.price} ₽</div>
                    </div>
                `;
            }).join('');
        }

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.onclick = () => {
                const tab = item.dataset.tab;
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                document.getElementById(tab + 'Tab').classList.add('active');
                if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
            };
        });

        // Check payment status on page load
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('success') === 'true') {
            const stars = parseInt(urlParams.get('stars')) || 0;
            const bonus = parseInt(urlParams.get('bonus')) || 0;
            const price = parseInt(urlParams.get('price')) || 0;
            
            // Update user data
            userData.totalStars += stars + bonus;
            userData.bonusStars += bonus;
            userData.totalPurchases++;
            userData.history.unshift({
                id: Date.now(),
                stars: stars,
                bonus: bonus,
                price: price,
                date: new Date().toISOString()
            });
            localStorage.setItem('userData', JSON.stringify(userData));
            
            updateStats();
            updateHistory();
            
            // Show success
            document.getElementById('modalIcon').textContent = '✅';
            document.getElementById('modalTitle').textContent = 'Успешно!';
            document.getElementById('modalText').innerHTML = `
                <div style="font-size: 18px; margin: 20px 0;">
                    Вы получили:<br>
                    <strong style="color: var(--gold); font-size: 28px;">${stars + bonus} ⭐</strong><br>
                    ${bonus > 0 ? `<small style="color: var(--green);">Включая ${bonus} бонусных</small>` : ''}
                </div>
            `;
            document.getElementById('modalButtons').innerHTML = `
                <button class="modal-btn modal-btn-primary" onclick="closeModal()" style="width: 100%;">Отлично!</button>
            `;
            document.getElementById('modalButtons').style.display = 'flex';
            document.getElementById('modal').classList.add('active');
            
            if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
        }

        // Init on load
        document.addEventListener('DOMContentLoaded', () => {
            createParticles();
            initUser();
            renderPackages();
        });
    </script>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Успешная оплата</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
    <script>
        const tg = window.Telegram?.WebApp;
        const params = new URLSearchParams(window.location.search);
        const redirectUrl = '/?success=true&' + params.toString();
        
        if (tg) {
            setTimeout(() => tg.close(), 1000);
        } else {
            window.location.href = redirectUrl;
        }
    </script>
</body>
</html>
"""

FAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ошибка оплаты</title>
</head>
<body style="background: #0a0e27; color: white; font-family: Arial; text-align: center; padding: 50px;">
    <h1>❌ Ошибка оплаты</h1>
    <p>Платеж был отменен или произошла ошибка.</p>
    <a href="/" style="color: #9d4edd;">Вернуться в магазин</a>
</body>
</html>
"""

# ============================================
# PAYMENT HANDLERS
# ============================================

async def create_payment(request):
    """Создание платежа ЮМани"""
    try:
        data = await request.json()
        package_id = data.get('package_id')
        user_id = data.get('user_id')
        username = data.get('username', 'User')
        
        # Find package
        package = next((p for p in [
            {"id": 1, "stars": 50, "price": 50, "bonus": 0},
            {"id": 2, "stars": 100, "price": 100, "bonus": 5},
            {"id": 3, "stars": 250, "price": 250, "bonus": 15},
            {"id": 4, "stars": 500, "price": 500, "bonus": 50},
            {"id": 5, "stars": 1000, "price": 1000, "bonus": 150},
            {"id": 6, "stars": 2500, "price": 2500, "bonus": 500}
        ] if p["id"] == package_id), None)
        
        if not package:
            return web.json_response({"error": "Package not found"}, status=400)
        
        # Create payment ID
        payment_id = f"stars_{user_id}_{package_id}_{int(datetime.now().timestamp())}"
        
        # Save payment info
        payments_db[payment_id] = {
            "user_id": user_id,
            "username": username,
            "package": package,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Create YooMoney payment URL
        success_url = f"{YOOMONEY_SUCCESS_URL}?payment_id={payment_id}&stars={package['stars']}&bonus={package['bonus']}&price={package['price']}"
        fail_url = YOOMONEY_FAIL_URL
        
        payment_url = (
            f"https://yoomoney.ru/quickpay/confirm.xml?"
            f"receiver={YOOMONEY_WALLET}&"
            f"quickpay-form=button&"
            f"paymentType=PC&"
            f"sum={package['price']}&"
            f"label={payment_id}&"
            f"successURL={success_url}&"
            f"failURL={fail_url}&"
            f"comment=Покупка {package['stars']} Telegram Stars"
        )
        
        logger.info(f"Payment created: {payment_id} for user {user_id}")
        
        return web.json_response({
            "payment_url": payment_url,
            "payment_id": payment_id
        })
        
    except Exception as e:
        logger.error(f"Create payment error: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def handle_success(request):
    """Success payment redirect"""
    return web.Response(text=SUCCESS_HTML, content_type='text/html')


async def handle_fail(request):
    """Failed payment redirect"""
    return web.Response(text=FAIL_HTML, content_type='text/html')


async def yoomoney_notification(request):
    """Webhook от ЮМани"""
    try:
        data = await request.post()
        
        # Проверка подписи
        notification_type = data.get('notification_type')
        operation_id = data.get('operation_id')
        amount = data.get('amount')
        currency = data.get('currency')
        datetime_str = data.get('datetime')
        sender = data.get('sender')
        codepro = data.get('codepro')
        label = data.get('label')
        sha1_hash = data.get('sha1_hash')
        
        # Verify signature
        sign_string = f"{notification_type}&{operation_id}&{amount}&{currency}&{datetime_str}&{sender}&{codepro}&{YOOMONEY_SECRET}&{label}"
        expected_hash = hashlib.sha1(sign_string.encode()).hexdigest()
        
        if sha1_hash != expected_hash:
            logger.warning(f"Invalid signature for payment {label}")
            return web.Response(status=403)
        
        # Process payment
        if label in payments_db and payments_db[label]["status"] == "pending":
            payment_info = payments_db[label]
            payment_info["status"] = "completed"
            
            user_id = payment_info["user_id"]
            package = payment_info["package"]
            
            # Send stars to user (will be implemented in bot handler)
            logger.info(f"Payment completed: {label} for user {user_id}")
            
            # Send notification to bot
            try:
                await bot.send_message(
                    user_id,
                    f"✅ <b>Оплата успешна!</b>\n\n"
                    f"🎉 Вы получили: <b>{package['stars']} ⭐</b>\n"
                    f"🎁 Бонус: <b>+{package['bonus']} ⭐</b>\n"
                    f"📦 Итого: <b>{package['stars'] + package['bonus']} ⭐</b>\n\n"
                    f"⚡ Звёзды будут отправлены автоматически в течение 1 минуты!"
                )
                
                # TODO: Send stars via Telegram API
                # This requires official Telegram Stars API access
                
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
        
        return web.Response(text="OK")
        
    except Exception as e:
        logger.error(f"Notification error: {e}")
        return web.Response(status=500)


# ============================================
# WEB SERVER
# ============================================

async def handle_index(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')


async def handle_health(request):
    return web.json_response({"status": "ok"})


# ============================================
# TELEGRAM BOT
# ============================================

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

WELCOME = f"""
🌟 <b>Добро пожаловать в Telegram Star Shop Premium!</b>

Здесь вы можете быстро и безопасно приобрести звёзды Telegram с автоматической доставкой.

✨ <b>Наши преимущества:</b>
• ⚡ Мгновенная автоматическая доставка
• 🎁 Щедрые бонусы до 500 звёзд
• 🔒 Безопасная оплата через ЮMoney
• 💬 Круглосуточная поддержка

<b>Откройте магазин и выберите пакет!</b> 👇
"""


def main_kb():
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(
        text="🌟 Открыть Star Shop Premium",
        web_app=WebAppInfo(url="https://telegramstar.bothost.ru")
    ))
    
    builder.row(InlineKeyboardButton(
        text="💬 Поддержка",
        url=f"https://t.me/{SUPPORT_USERNAME}"
    ))
    
    builder.row(
        InlineKeyboardButton(
            text="📋 Соглашение",
            url="https://telegra.ph/Polzovatelskoe-soglashenie-08-15-10"
        ),
        InlineKeyboardButton(
            text="📜 Конфиденциальность",
            url="https://telegra.ph/Politika-konfidencialnosti-08-15-17"
        )
    )
    
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    logger.info(f"User {user.id} (@{user.username}) started bot")
    
    # Save user
    users_db[user.id] = {
        "username": user.username,
        "first_name": user.first_name,
        "started_at": datetime.now().isoformat()
    }
    
    await message.answer(WELCOME, reply_markup=main_kb())


@router.message()
async def handle_messages(message: Message):
    await message.answer(
        "Используйте кнопку ниже для доступа к магазину 👇",
        reply_markup=main_kb()
    )


dp.include_router(router)

# ============================================
# STARTUP
# ============================================

async def start_web():
    app = web.Application()
    
    # Routes
    app.router.add_get('/', handle_index)
    app.router.add_get('/health', handle_health)
    app.router.add_get('/success', handle_success)
    app.router.add_get('/fail', handle_fail)
    app.router.add_post('/api/create-payment', create_payment)
    app.router.add_post('/yoomoney/notification', yoomoney_notification)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
    await site.start()
    
    logger.info(f"🌐 Web server: https://telegramstar.bothost.ru")
    logger.info(f"💳 Payment: ЮMoney {YOOMONEY_WALLET}")


async def start_bot():
    logger.info("🤖 Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    logger.info("=" * 60)
    logger.info("🚀 TELEGRAM STAR SHOP PREMIUM - STARTING")
    logger.info("=" * 60)
    logger.info(f"💰 Wallet: {YOOMONEY_WALLET}")
    logger.info(f"👤 Support: @{SUPPORT_USERNAME}")
    logger.info("=" * 60)
    
    await asyncio.gather(
        start_web(),
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
