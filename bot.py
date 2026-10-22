import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import google.generativeai as genai

# Configurare jurnalizare (logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Preluare chei din variabilele de mediu
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Configurare model AI gratuit (Google Gemini)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 1. Mic server web intern care ține Render mulțumit (să nu închidă serviciul)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Funcție care apelează AI-ul DOAR când este solicitată la apăsare
async def genereaza_analiza_text():
    prompt = (
        "Acționează ca un consultant responsabil de managementul riscului pentru jocuri de divertisment. "
        "Generează un scurt mesaj în limba română care să conțină: "
        "1. O perspectivă statistică ipotetică de prudență (ex: recomandare de oprire timpurie la un coeficient mic de 1.2x - 1.4x). "
        "2. Un avertisment ferm despre importanța pauzelor și a limitării bugetului. "
        "Fii concis, obiectiv și menționează clar riscul."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Momentan serviciul de analiză AI nu este disponibil. Vă rugăm reveniți mai târziu."

# Comanda /start - Meniul principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Generează Analiză / Semnal", callback_data="get_stats")],
        [InlineKeyboardButton("ℹ️ Despre Riscuri & Legitimitate", callback_data="get_risks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🤖 **Asistent Oficial de Analiză & Managementul Riscului**\n\n"
        "Acest bot generează analize de prudență **exclusiv la cererea ta**.\n\n"
        "Apasă pe butonul de mai jos sau folosește comanda **/semnal** pentru a primi o simulare statistică.\n\n"
        "⚠️ *Jocurile de noroc implică riscuri financiare majore. Nu există garanții de câștig.*"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Comanda directă /semnal
async def semnal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Se procesează cererea ta de analiză...")
    
    ai_output = await genereaza_analiza_text()
    
    final_message = (
        f"📊 **Buletin de Analiză și Prudență**\n\n"
        f"{ai_output}\n\n"
        f"⚠️ *Joacă responsabil! Limitează-ți bugetul.*"
    )
    
    keyboard = [[InlineKeyboardButton("🔄 Solicită o nouă analiză", callback_data="get_stats")]]
    await update.message.reply_text(final_message, reply_markup=reply_markup, parse_mode="Markdown")

# Handler pentru butoane
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_risks":
        risk_text = (
            "🛡️ **Informații Legale și Joc Responsabil**\n\n"
            "• Jocurile de tip Crash (cum este Aviator) funcționează pe algoritmi aleatorii (*Provably Fair*).\n"
            "• Nicio inteligență artificială nu poate ghici sau garanta multiplicatori viitori.\n"
            "• Setează-ți un buget fix și nu juca niciodată bani pe care nu îți permiți să îi pierzi."
        )
        keyboard = [[InlineKeyboardButton("🔙 Înapoi la Meniu", callback_data="back_start")]]
        await query.edit_message_text(text=risk_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "back_start":
        keyboard = [
            [InlineKeyboardButton("📊 Generează Analiză / Semnal", callback_data="get_stats")],
            [InlineKeyboardButton("ℹ️ Despre Riscuri & Legitimitate", callback_data="get_risks")]
        ]
        await query.edit_message_text(
            text="🤖 **Asistent Oficial de Analiză & Managementul Riscului**\n\nAlege o opțiune de mai jos:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    if query.data == "get_stats":
        await query.edit_message_text(text="🔍 Se generează analiza cu AI...")
        
        ai_output = await genereaza_analiza_text()

        final_message = (
            f"📊 **Buletin de Analiză și Prudență**\n\n"
            f"{ai_output}\n\n"
            f"⚠️ *Joacă responsabil! Limitează-ți bugetul.*"
        )
        
        keyboard = [[InlineKeyboardButton("🔄 Solicită o nouă analiză", callback_data="get_stats")]]
        await query.edit_message_text(text=final_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    # Pornim serverul web intern într-un fir separat (thread) pentru a ura Render fericit
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # Pornim botul de Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("semnal", semnal_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Botul este pornit și rulează corect pe server!")
    app.run_polling()

if __name__ == "__main__":
    application = Application.builder().token("TOKEN_UL_TAU").build()
    
    # Adaugi handlerele aici...
    
    # Pornirea corectă:
    application.run_polling()
