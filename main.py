import helperJS
import json
import asyncio
import subprocess
import threading
import time
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command

TOKEN = ""
users, ipAdresses = "other/users.json", "other/ipAdresses.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if helperJS.find("id", message.from_user.id, users) != None:
        kb = [[types.KeyboardButton(text="💻 Проверка серверов"), types.KeyboardButton(text="🎥 Проверка камер")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        return await message.answer(f"🔩 Ваш ID: {message.from_user.id}\n✅ У вас имеется доступ к боту.", reply_markup=keyboard)
    await message.reply(f"🔩 Ваш ID: {message.from_user.id}\n⛔ У вас отсутствует доступ.", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.lower() == "💻 проверка серверов")
async def ping_servers(message: types.Message):
    if helperJS.find("id", message.from_user.id, users) != None:
        load = await message.reply("🔃 Соединение с серверами...")
        await message.reply(f"💻 Состояние серверов: {ping('servers')}")
        return await load.delete()
    await message.reply(f"🔩 Ваш ID: {message.from_user.id}\n⛔ У вас отсутствует доступ.", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.lower() == "🎥 проверка камер")
async def ping_cameras(message: types.Message):
    if helperJS.find("id", message.from_user.id, users) != None:
        load = await message.reply("🔃 Соединение с камерами...")
        await message.reply(f"🎥 Состояние камер: {ping('cameras')}")
        return await load.delete()
    await message.reply(f"🔩 Ваш ID: {message.from_user.id}\n⛔ У вас отсутствует доступ.", reply_markup=types.ReplyKeyboardRemove())


def notifications():
    timer = 0
    while True:
        try:
            answerServers, answerCameras = ping('servers'), ping('cameras')
            if answerServers != "\n✅ Стабильно." and timer <= 0 or answerCameras != "\n✅ Стабильно." and timer <= 0:
                timer = 16
                with open(users, "r", encoding="utf-8") as file:
                    usersfile = json.load(file)
                for user in usersfile:
                    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={user['id']}&text=❗ Уведомление ❗\n💻 Сервера:{answerServers}\n\n🎥 Камеры: {answerCameras}")
            if timer > 0: timer -= 1
            time.sleep(5)

        except Exception: time.sleep(5)

def ping(names):
    answer = ""
    with open(ipAdresses, "r", encoding="utf-8") as file:
            ipfile = json.load(file)
    for ip in ipfile[names]:
        ping1 = subprocess.run(['ping', ip['ip'], '-n', '1'], stdout=subprocess.PIPE)
        ping2 = subprocess.run(['ping', ip['ip'], '-n', '1'], stdout=subprocess.PIPE)
        if ping1.returncode == ping2.returncode != 0:
            answer += f"\n❌ {ip['ip']} [{ip['name']}] - Не работает"
    if answer == "": answer = "\n✅ Стабильно."
    return answer

async def main():
    await dp.start_polling(bot, skip_updates=True)

def starts():
    asyncio.run(main())

start = threading.Thread(target=starts)
notification = threading.Thread(target=notifications)
start.start()
notification.start()
start.join()
notification.join()