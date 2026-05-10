import asyncio
import json
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand

TOKEN = "8483524979:AAFvtZq-2cYqp-IZl8GRsrn0T-vqBDirdcY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

with open(r'.venv\games.json',encoding='utf-8') as f:
    GAMES = json.load(f)

user_data = {}
user_history = {}

async def set_commands():
    commands = [
        BotCommand(command="start", description="Запустить бота 🚀"),
        BotCommand(command="random", description="Случайная игра 🎲")
    ]
    await bot.set_my_commands(commands)

async def main():
    await set_commands()  
    await dp.start_polling()

genre_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Экшен 💥"),KeyboardButton(text="RPG ⚔️")],
        [KeyboardButton(text="Приключения 🗺️"),KeyboardButton(text="Инди 🕹️")],
        [KeyboardButton(text="Стратегия 🧩"),KeyboardButton(text="Хоррор 👻")]
    ],
    resize_keyboard=True
)

mode_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Одиночный "),KeyboardButton(text="Мультиплеер/Кооператив")],
    ],
    resize_keyboard=True
)

platform_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="PC"),KeyboardButton(text="Playstation")],
        [KeyboardButton(text="Xbox"),KeyboardButton(text="Mobile")],
        [KeyboardButton(text="Nintendo")],
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    user_history[user_id] = []
    await message.answer("Привет, я помогу тебе выбрать игру по твоим предпочтениям, но для начала ответь на пару вопросов "),
    await message.answer("Какой жанр игры предпочитаешь?",reply_markup=genre_kb)

@dp.message(F.text.in_(["Экшен 💥","RPG ⚔️","Приключения 🗺️","Инди 🕹️","Стратегия 🧩","Хоррор 👻"]))
async def get_genre(message: Message):
    user_id = message.from_user.id
    user_data[user_id]['genre'] = message.text
    await message.answer("Какой режим игры тебе больше подходит?", reply_markup=mode_kb)

@dp.message(F.text.in_(["Одиночный", "Мультиплеер/Кооператив"]))
async def get_mode(message: Message):
    user_id = message.from_user.id
    user_data[user_id]['mode'] = message.text
    await message.answer("На какой платформе собираешься играть?", reply_markup=platform_kb)

@dp.message(F.text.in_(["PC", "Playstation", "Xbox", "Mobile", "Nintendo"]))
async def get_platform(message: Message):
    user_id = message.from_user.id
    user_data[user_id]['platform'] = message.text
    await send_game(user_id, message)

async def send_game(user_id, message):
    genre = user_data[user_id]['genre']
    mode = user_data[user_id]['mode']
    platform = user_data[user_id]['platform']
    games_list = GAMES[genre][mode][platform]
    
    available = [i for i in games_list if i['name'] not in user_history[user_id]]
    
    if not available:
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="🔄 Новый поиск", callback_data="new"),
        )
        await message.answer("В базе данных больше нет игр такой категории(",parse_mode="Markdown",reply_markup=builder.as_markup())
        return
    
    game = random.choice(available)
    user_history[user_id].append(game['name'])
    
    text = f"🎮 *{game['name']}*\n\n📝 {game['desc']}"
    
    media_group = []
    for i, img_url in enumerate(game['img']):
        if i == 0:
            media_group.append(InputMediaPhoto(media=img_url, caption=text, parse_mode="Markdown"))
        else:
            media_group.append(InputMediaPhoto(media=img_url))
        
    await message.answer_media_group(media=media_group)
    await message.answer("Что дальше?", reply_markup=get_game_keyboard())

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    all_games = []
    for genre in GAMES:
        for mode in GAMES[genre]:
            for platform in GAMES[genre][mode]:
                for game in GAMES[genre][mode][platform]:
                    game_copy = game.copy()
                    game_copy['genre'] = genre
                    game_copy['mode'] = mode
                    game_copy['platform'] = platform
                    all_games.append(game_copy)
    
    game = random.choice(all_games)
    
    text = f"🎲 *Случайная игра*\n\n"
    text += f"🎮 *{game['name']}*\n\n"
    text += f"📝 {game['desc']}\n\n"
    text += f"🎭 *Жанр:* {game['genre']}\n"
    text += f"👥 *Режим:* {game['mode']}\n"
    text += f"🖥️ *Платформа:* {game['platform']}"
    
    media_group = []
    for i, img_url in enumerate(game['img']):
        if i == 0:
            media_group.append(InputMediaPhoto(media=img_url, caption=text, parse_mode="Markdown"))
        else:
            media_group.append(InputMediaPhoto(media=img_url))
        

    await message.answer_media_group(media=media_group) 

def get_game_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎲 Другой вариант", callback_data="another"))
    builder.add(InlineKeyboardButton(text="🔄 Новый поиск", callback_data="new"))
    return builder.as_markup()

@dp.callback_query(F.data == "another")
async def another_game(callback):
    await send_game(callback.from_user.id, callback.message)
    await callback.answer()
@dp.callback_query(F.data == "new")

async def new_search(callback):
    user_id = callback.from_user.id
    user_data[user_id] = {}
    user_history[user_id] = []
    await callback.message.answer("Выбери жанр:", reply_markup=genre_kb)
    await callback.answer()
    await callback.message.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())