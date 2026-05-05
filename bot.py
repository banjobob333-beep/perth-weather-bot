import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

CITIES = {
    "Perth 🇦🇺": (-31.9505, 115.8605, "Australia/Perth"),
    "Sydney 🇦🇺": (-33.8688, 151.2093, "Australia/Sydney"),
    "Melbourne 🇦🇺": (-37.8136, 144.9631, "Australia/Melbourne"),
    "London 🇬🇧": (51.5074, -0.1278, "Europe/London"),
    "New York 🇺🇸": (40.7128, -74.0060, "America/New_York"),
    "Tokyo 🇯🇵": (35.6762, 139.6503, "Asia/Tokyo"),
    "Dubai 🇦🇪": (25.2048, 55.2708, "Asia/Dubai"),
    "Paris 🇫🇷": (48.8566, 2.3522, "Europe/Paris"),
    "Singapore 🇸🇬": (1.3521, 103.8198, "Asia/Singapore"),
    "Los Angeles 🇺🇸": (34.0522, -118.2437, "America/Los_Angeles"),
}

WMO_CODES = {
    0: "☀️ Clear sky", 1: "🌤 Mainly clear", 2: "⛅ Partly cloudy",
    3: "☁️ Overcast", 45: "🌫 Foggy", 48: "🌫 Icy fog",
    51: "🌦 Light drizzle", 53: "🌦 Drizzle", 55: "🌧 Heavy drizzle",
    61: "🌧 Light rain", 63: "🌧 Rain", 65: "🌧 Heavy rain",
    80: "🌦 Showers", 81: "🌧 Heavy showers", 82: "⛈ Violent showers",
    95: "⛈ Thunderstorm", 96: "⛈ Thunderstorm with hail"
}

def fetch_weather(lat, lon, timezone):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": timezone,
        "wind_speed_unit": "kmh",
        "forecast_days": 7
    }
    return requests.get(url, params=params).json()

def format_current(city_name, data):
    c = data["current"]
    desc = WMO_CODES.get(c["weather_code"], f"Code {c['weather_code']}")
    return (
        f"🌏 *{city_name} — Current Weather*\n"
        f"{desc}\n\n"
        f"🌡 Temperature: {c['temperature_2m']}°C\n"
        f"💧 Humidity: {c['relative_humidity_2m']}%\n"
        f"🌧 Precipitation: {c['precipitation']} mm\n"
        f"💨 Wind: {c['wind_speed_10m']} km/h"
    )

def format_forecast(city_name, data):
    d = data["daily"]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    lines = [f"📅 *{city_name} — 7 Day Forecast*\n"]
    for i in range(7):
        from datetime import datetime
        date = datetime.strptime(d["time"][i], "%Y-%m-%d")
        day = days[date.weekday()]
        desc = WMO_CODES.get(d["weather_code"][i], "?")
        lines.append(
            f"*{day} {date.strftime('%d %b')}*\n"
            f"{desc}\n"
            f"🌡 {d['temperature_2m_min'][i]}°C – {d['temperature_2m_max'][i]}°C  "
            f"🌧 {d['precipitation_sum'][i]} mm\n"
        )
    return "\n".join(lines)

def city_keyboard():
    keyboard = []
    city_list = list(CITIES.keys())
    for i in range(0, len(city_list), 2):
        row = [InlineKeyboardButton(city_list[i], callback_data=f"city:{city_list[i]}")]
        if i + 1 < len(city_list):
            row.append(InlineKeyboardButton(city_list[i+1], callback_data=f"city:{city_list[i+1]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def weather_options_keyboard(city_name):
    keyboard = [
        [
            InlineKeyboardButton("🌡 Current", callback_data=f"current:{city_name}"),
            InlineKeyboardButton("📅 7 Day Forecast", callback_data=f"forecast:{city_name}"),
        ],
        [InlineKeyboardButton("🔙 Back to cities", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm your Weather Bot.\n\nChoose a city to get started:",
        reply_markup=city_keyboard()
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose a city:",
        reply_markup=city_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back":
        await query.edit_message_text("Choose a city:", reply_markup=city_keyboard())

    elif data.startswith("city:"):
        city_name = data[5:]
        await query.edit_message_text(
            f"*{city_name}* — what would you like to see?",
            parse_mode="Markdown",
            reply_markup=weather_options_keyboard(city_name)
        )

    elif data.startswith("current:"):
        city_name = data[8:]
        lat, lon, tz = CITIES[city_name]
        weather_data = fetch_weather(lat, lon, tz)
        text = format_current(city_name, weather_data)
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=weather_options_keyboard(city_name)
        )

    elif data.startswith("forecast:"):
        city_name = data[9:]
        lat, lon, tz = CITIES[city_name]
        weather_data = fetch_weather(lat, lon, tz)
        text = format_forecast(city_name, weather_data)
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=weather_options_keyboard(city_name)
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
