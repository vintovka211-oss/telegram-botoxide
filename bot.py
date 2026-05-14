import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID
from database import load_data, save_data

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Кнопки админа ---
def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Изменить цены", callback_data="edit_prices")],
        [InlineKeyboardButton(text="🔑 Изменить ключи", callback_data="edit_keys")],
        [InlineKeyboardButton(text="📢 Показать витрину", callback_data="show_shop")]
    ])

# --- Кнопки покупки ---
def buy_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день", callback_data="buy_1day"),
         InlineKeyboardButton(text="7 дней", callback_data="buy_7day")],
        [InlineKeyboardButton(text="30 дней", callback_data="buy_30day"),
         InlineKeyboardButton(text="Навсегда", callback_data="buy_forever")]
    ])

# --- Команда /start (для всех) ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    data = load_data()
    prices = data["prices"]
    text = (f"🎮 *Магазин читов*\n\n"
            f"💎 1 день — {prices['1day']}₽\n"
            f"🔥 7 дней — {prices['7day']}₽\n"
            f"⚡ 30 дней — {prices['30day']}₽\n"
            f"👑 Навсегда — {prices['forever']}₽\n\n"
            f"Нажми на тариф, чтобы получить ключ")
    await message.answer(text, parse_mode="Markdown", reply_markup=buy_buttons())

# --- Обработка покупки (без подписки) ---
@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_handler(callback: types.CallbackQuery):
    data = load_data()
    plan = callback.data.split("_")[1]
    key = data["keys"].get(plan, "")
    if key:
        await callback.message.answer(f"✅ Ваш ключ:\n`{key}`\n\nСпасибо за покупку!", parse_mode="Markdown")
    else:
        await callback.message.answer("⛔ Ключ временно отсутствует. Напишите админу.")
    await callback.answer()

# --- Админ-панель ---
@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа")
        return
    await message.answer("🔧 Панель управления", reply_markup=admin_panel())

# --- Админ: изменить цены ---
@dp.callback_query(lambda c: c.data == "edit_prices")
async def edit_prices(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Введите 4 цены через пробел:\n`1день 7дней 30дней навсегда`\nПример: `100 500 1500 5000`")
    await callback.answer()

@dp.message(lambda msg: msg.from_user.id == ADMIN_ID and len(msg.text.split()) == 4)
async def save_prices(message: types.Message):
    parts = message.text.split()
    data = load_data()
    data["prices"] = {
        "1day": parts[0],
        "7day": parts[1],
        "30day": parts[2],
        "forever": parts[3]
    }
    save_data(data)
    await message.answer("✅ Цены обновлены!")

# --- Админ: изменить ключи ---
@dp.callback_query(lambda c: c.data == "edit_keys")
async def edit_keys(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Введите 4 ключа через пробел (любые символы):\n`ключ1день ключ7дней ключ30дней ключнавсегда`")
    await callback.answer()

@dp.message(lambda msg: msg.from_user.id == ADMIN_ID and len(msg.text.split()) == 4)
async def save_keys(message: types.Message):
    parts = message.text.split()
    data = load_data()
    data["keys"] = {
        "1day": parts[0],
        "7day": parts[1],
        "30day": parts[2],
        "forever": parts[3]
    }
    save_data(data)
    await message.answer("✅ Ключи сохранены!")

# --- Админ: показать витрину (отправить самому себе) ---
@dp.callback_query(lambda c: c.data == "show_shop")
async def show_shop(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    data = load_data()
    prices = data["prices"]
    text = (f"🎮 *Магазин читов*\n\n"
            f"💎 1 день — {prices['1day']}₽\n"
            f"🔥 7 дней — {prices['7day']}₽\n"
            f"⚡ 30 дней — {prices['30day']}₽\n"
            f"👑 Навсегда — {prices['forever']}₽")
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=buy_buttons())
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
