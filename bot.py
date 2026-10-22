from telegram.ext import Application
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from groq import Groq

# Configurare jurnalizare
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Preluare chei din variabilele de mediu
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8896679145:AAH3NmHLeL0GGPPJGWWcKWT1X_5Bhtn6jaw")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Configurare client Groq
client = Groq(api_key=GROQ_API_KEY)

# Funcție care apelează AI-ul de la Groq (Llama 3)
async def genereaza_analiza_text():
    prompt = (
        "Acționează ca un consultant responsabil de managementul riscului pentru jocuri de divertisment. "
        "Generează un scurt mesaj în limba română care să conțină: "
        "1. O perspectivă statistică ipotetică de prudență (ex: recomandare de oprire timpurie la un coeficient mic de 1.2x - 1.4x). "
        "2. Un avertisment ferm despre importanța pauzelor și a limitării bugetului. "
        "Fii concis, obiectiv și menționează clar riscul."
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Unul dintre cele mai bune și rapide modele de pe Groq
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Eroare Groq API: {e}")
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(final_message, reply_markup=reply_markup, parse_mode="Markdown")

# Handler pentru butoane
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_risks":
        risk_text = (
            "🛡️ **Informații Legale și Joc Responsabil**\n\n"
            "• Jocurile de tip Crash funcționează pe algoritmi aleatorii (*Provably Fair*).\n"
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
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("semnal", semnal_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    port = int(os.environ.get("PORT", 10000))
    render_url = os.getenv("RENDER_EXTERNAL_URL")

    print(f"Pornire server Webhook pe portul {port} (cu Groq AI)...")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{render_url}/{TELEGRAM_TOKEN}" if render_url else None
    )

if __name__ == "__main__":
    main()
