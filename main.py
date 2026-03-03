import asyncio
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from aiohttp import web
import threading

# Фиктивный сервер для Render
async def handle(request):
    return web.Response(text="Олух под защитой!")

def run_web():
    app = web.Application()
    app.router.add_get('/', handle)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# Запускаем сервер в отдельном потоке
threading.Thread(target=run_web, daemon=True).start()

# Токен и настройки
TOKEN = "8660282196:AAE0-P4UUd3QLkr0eoCst4zn4wmznvoTnmU"
VOZHAK_USERNAME = "odos765" # Твой юзернейм для авто-прав
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных в памяти
user_db = {} # {user_id: {'rank': 0, 'warns': [], 'username': ''}}

HEROES = {
    "hiccup": "🐉 [Иккинг]: ",
    "astrid": "🪓 [Астрид]: ",
    "fishlegs": "📚 [Рыбьеног]: ",
    "snotlout": "🔥 [Сморкала]: ",
    "twins": "💥 [Близнецы]: "
}

def get_data(user: types.User):
    uid = user.id
    if uid not in user_db:
        # Если это ты, сразу ставим 5 ранг
        rank = 5 if user.username == VOZHAK_USERNAME else 0
        user_db[uid] = {'rank': rank, 'warns': [], 'username': user.username}
    return user_db[uid]

# --- КОМАНДЫ ИЕРАРХИИ ---

@dp.message(F.text.lower().startswith("кто админ"))
async def list_admins(message: types.Message):
    admins = [f"Ранг {d['rank']}: @{d['username']}" for uid, d in user_db.items() if d['rank'] > 0]
    admins.sort(reverse=True)
    response = "\n".join(admins) if admins else "Пока только обычные викинги."
    await message.reply(f"{HEROES['fishlegs']} Список всадников:\n{response}")

@dp.message(F.text.lower().startswith(("повысить", "понизить")))
async def change_rank(message: types.Message):
    admin = get_data(message.from_user)
    if admin['rank'] < 4: return 
    
    if not message.reply_to_message: return
    target_user = message.reply_to_message.from_user
    target = get_data(target_user)
    
    text = message.text.lower()
    step = 1
    # Проверка на "повысить 2"
    parts = text.split()
    if len(parts) > 1 and parts[1].isdigit():
        step = int(parts[1])

    if "повысить" in text:
        target['rank'] = min(5, target['rank'] + step)
        await message.reply(f"{HEROES['hiccup']} @{target_user.username}, твой ранг повышен до {target['rank']}!")
    else:
        target['rank'] = max(0, target['rank'] - step)
        await message.reply(f"{HEROES['hiccup']} @{target_user.username}, твой ранг понижен до {target['rank']}.")

# --- КАРТОЧКА ПОЛЬЗОВАТЕЛЯ ---

@dp.message(F.text.lower().in_(["кто я", "!роль", "профиль", "хто я"]))
async def who_am_i(message: types.Message):
    user = get_data(message.from_user)
    await message.reply(f"{HEROES['fishlegs']} Так-так... Твой ранг: {user['rank']}. Предупреждений: {len(user['warns'])}/5.")

@dp.message(F.text.lower() == "моя стата")
async def my_stats(message: types.Message):
    user = get_data(message.from_user)
    graph = "🟩" * user['rank'] + "⬜" * (5 - user['rank'])
    await message.reply(f"{HEROES['fishlegs']} Твой прогресс обучения:\n{graph} ({user['rank']}/5)")

# --- ПРИВЕТСТВИЕ ---

@dp.chat_member()
async def auto_welcome(event: types.ChatMemberUpdated):
    if event.new_chat_member.status == "member":
        await event.answer(f"{HEROES['snotlout']} Очередной новичок! Надеюсь, ты принес подношение Великому Сморкале?")

async def main():
    print("Бот Драконьего Края запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
