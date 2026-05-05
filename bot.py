import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

def get_perth_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -31.9505,
        "longitude": 115.8605,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "Australia/Perth",
        "wind_speed_unit": "kmh"
    }
    r = requests.get(url, params=params).json()
    c = r["current"]
    
    code = c["weather_code"]
    conditions = {
        0: "☀️ Clear sky", 1: "🌤 Mainly clear", 2: "⛅ Partly cloudy",
        3: "☁️ Overcast", 45: "🌫 Foggy", 48: "🌫 Icy fog",
        51: "🌦 Light drizzle", 53: "🌦 Drizzle", 55: "🌧 Heavy drizzle",
        61: "🌧 Light rain", 63: "🌧 Rain", 65: "🌧 Heavy rain",
        80: "🌦 Showers", 81: "🌧 Heavy showers", 82: "⛈ Violent showers",
        95: "⛈ Thunderstorm", 96: "⛈ Thunderstorm with hail"
    }
    desc = conditions.get(code, f"Code {code}")
    
    return (
        f"🌏 *Perth WA Weather*\n"
        f"{desc}\n\n"
        f"🌡 Temperature: {c['temperature_2m']}°C\n"
        f"💧 Humidity: {c['relative_humidity_2m']}%\n"
        f"🌧 Precipitation: {c['precipitation']} mm\n"
        f"💨 Wind: {c['wind_speed_10m']} km/h"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm your Perth Weather Bot.\n\nSend /weather to get the current weather in Perth, WA."
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_perth_weather(), parse_mode="Markdown")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.run_polling()
