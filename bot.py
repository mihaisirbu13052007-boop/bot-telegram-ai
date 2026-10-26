from telegram.ext import Application
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from groq import Groq

# Configurare jurnalizare
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Preluare chei din variabilele de mediu
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Configurare client Groq
client = Groq(api_key=GROQ_API_KEY)

# Funcție care apelează AI-ul pentru a genera cifre și analize concrete
async def genereaza_analiza_text():
    prompt = (
        "Acționează ca un analist financiar și consultant de risc. "
        "Generează un scurt buletin de analiză în limba română care să conțină obligatoriu cifre și statistici concrete (de exemplu: un risc estimat la 78%, o limită de buget recomandată de 200 lei, un multiplicator de prudență de 1.35x). "
        "Fii foarte clar, obiectiv și atrage atenția asupra riscurilor financiare."
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-20b",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Eroare Groq API: {e}")
        return "Momentan serviciul de analiză AI nu este disponibil. Vă rugăm reveniți mai târziu."

# Comanda /start - Meniul principal cu imagine opțională
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Generează Analiză cu Cifre", callback_data="get_stats")],
        [InlineKeyboardButton("ℹ️ Despre Riscuri & Reguli", callback_data="get_risks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🤖 **Asistent Oficial de Analiză & Managementul Riscului**\n\n"
        "Acest bot generează rapoarte statistice bazate pe **cifre concrete** și indicatori de prudență.\n\n"
        "👇 Apasă pe butonul de mai jos pentru primul raport:"
    )
    
    # Poți trimite o poză de întâmpinare punând un link direct către o imagine (URL)
    photo_url = "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800" # Exemplu de imagine legată de grafice/statistici
    
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url,
            caption=welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception:
        # Dacă din nějak motiv poza nu se poate trimite, trimite textul simplu
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Comanda directă /semnal
async def semnal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Se calculează indicatorii și cifrele statistice...")
    
    ai_output = await genereaza_analiza_text()
    
    final_message = (
        f"📊 **RAPORT STATISTIC DE PRUDENȚĂ**\n\n"
        f"{ai_output}\n\n"
        f"🚨 *Notă: Respectă limitele impuse și joacă responsabil!*"
    )
    
    keyboard = [[InlineKeyboardButton("🔄 Generează Alte Cifre", callback_data="get_stats")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(final_message, reply_markup=reply_markup, parse_mode="Markdown")

# Handler pentru butoane
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_risks":
        risk_text = (
            "🛡️ **Statistici & Reguli de Siguranță Financiară**\n\n"
            "• **Risc estimat:** 80% pierdere pe termen lung în cazul jocurilor aleatorii.\n"
            "• **Buletin de prudență:** Setează un plafon maxim zilnic.\n"
            "• **Timp recomandat de pauză:** Minimum 45 de minute după fiecare sesiune."
        )
        keyboard = [[InlineKeyboardButton("🔙 Înapoi la Meniu", callback_data="back_start")]]
        await query.edit_message_text(text=risk_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if query.data == "back_start":
        keyboard = [
            [InlineKeyboardButton("📊 Generează Analiză cu Cifre", callback_data="get_stats")],
            [InlineKeyboardButton("ℹ️ Despre Riscuri & Reguli", callback_data="get_risks")]
        ]
        await query.edit_message_text(
            text="🤖 **Asistent Oficial de Analiză & Managementul Riscului**\n\nAlege o opțiune:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    if query.data == "get_stats":
        await query.edit_message_text(text="🔍 Se procesează datele statistice...")
        
        ai_output = await genereaza_analiza_text()

        final_message = (
            f"📊 **RAPORT STATISTIC DE PRUDENȚĂ**\n\n"
            f"{ai_output}\n\n"
            f"🚨 *Notă: Respectă limitele impuse și joacă responsabil!*"
        )
        
        keyboard = [[InlineKeyboardButton("🔄 Generează Alte Cifre", callback_data="get_stats")]]
        await query.edit_message_text(text=final_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("semnal", semnal_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    port = int(os.environ.get("PORT", 10000))
    render_url = os.getenv("RENDER_EXTERNAL_URL")

    print(f"Pornire server Webhook pe portul {port}...")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{render_url}/{TELEGRAM_TOKEN}" if render_url else None
    )

if __name__ == "__main__":
    main()
