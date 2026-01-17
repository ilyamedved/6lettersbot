from PIL import Image, ImageDraw, ImageFont
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery, InputFile 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import default_state, State, StatesGroup
import random
import os
from dotenv import load_dotenv

def getword(numbr):
    fin = open("words-russian-nouns.sql","r", encoding="UTF-8")
    for i in range(numbr):
        str = fin.readline()
    w = str.split()
    while len(w[1]) != 9:
        str = fin.readline()
        w = str.split()
    rt = w[1].replace(",","")
    rt = rt.replace("'","")
    print(rt)
    fin.close
    return rt

dotenv_path = os.path.join(os.path.dirname(__file__), '6lettersbot.env')
#print("this is dotenv_path=",dotenv_path)
load_dotenv(dotenv_path)
BT = os.getenv('BOT_TOKEN')

class play(StatesGroup):
    lang = State()
    in_game = State()
    mode = State()
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Инициализация
bot = Bot(token=BT)
dp = Dispatcher(storage=storage)
# Создание клавиатуры
def get_rus_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Играть"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚙️ Настройки")] ],
        resize_keyboard=True,  # Подгоняет размер кнопок
        input_field_placeholder="Выберите действие..."  # Подсказка в поле ввода
    )
    return keyboard
def get_eng_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Play"), KeyboardButton(text="ℹ️ Help")],
            [KeyboardButton(text="📊 Statistics"), KeyboardButton(text="⚙️ Settings")] ],
        resize_keyboard=True,  # Подгоняет размер кнопок
        input_field_placeholder="Choose option..."  # Подсказка в поле ввода
    )
    return keyboard
    
def get_lang_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")] ],
        resize_keyboard=True,  # Подгоняет размер кнопок
        input_field_placeholder="Choose your language : Выберите язык"  # Подсказка в поле ввода
    )
    return keyboard
# Обработчик команды /start
#@dp.message(Command("start"), ~StateFilter(play.in_game))
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    uname = message.from_user.id
    print(uname)
    await state.set_state(play.lang)
    await message.answer("Добро пожаловать! Welcome!\nChoose your language : Выберите язык", reply_markup=get_lang_keyboard())

@dp.message(Command('help'))
async def help_command(message: Message): 
    #await message.reply("Команды бота:\n/start - Начать работу\n/help - Получить помощь")
    await message.answer("Команды бота:\n/start - Начать работу\n/help - Получить помощь")

# Обработчик текстовых сообщений
@dp.message(F.text =="🇷🇺 Русский", StateFilter(play.lang))
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(default_state)
    await state.update_data(lang="rus")
    await message.answer(f"Отличный выбор!", reply_markup=get_rus_keyboard())

@dp.message(F.text =="🇬🇧 English", StateFilter(play.lang))
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(default_state)
    await state.update_data(lang="eng")
    await message.answer(f"Great choice!", reply_markup=get_eng_keyboard())

@dp.message(F.text =="ℹ️ Help")
async def echo_message(message: types.Message):
    await message.answer(f"Player attempts to guess a 6-letters word within ten tries. After each guess, the letters are color-coded to indicate their accuracy: green means the letter is correct and in the right position, yellow means it is in the word but in the wrong position, and gray means it is not in the word at all. If a guessed word contains multiple instances of the same letter—such as the 'o's in 'robot'—those letters will be marked green or yellow only if the answer also contains them multiple times; otherwise, extra occurrences will be marked gray. Words are given in the American spelling.", reply_markup=get_eng_keyboard())

@dp.message(F.text =="🚀 Play")
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(play.in_game)
    await state.update_data(tr = 1) # номер попытки текущей.
    await message.answer(f"Ok, let's begin!", reply_markup=types.ReplyKeyboardRemove())
    #await bot.send_photo(chat_id=message.chat.id, photo=types.FSInputFile("matrix.jpg"))

@dp.message(F.text =="🚀 Играть")
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(play.in_game)
    await state.update_data(word = getword(random.randint(10, 65627)))
    await state.update_data(tr = 1) # номер попытки текущей.
    await state.update_data(usedlt = []) # использованные буковки.
    #await state.update_data(pict_path = r'C:\Users\ilya_\Desktop\nonogram\matrix_rus')
    await state.update_data(pict_path = 'matrix_rus')
    #user_data = await state.get_data()
    #await message.answer(text=f"Вы выбрали {user_data['lang']}.")
    #print(await state.get_data())
    await message.answer(f"Отлично, стартуем!\nЖду слово из 6 букв", reply_markup=types.ReplyKeyboardRemove())
    #await bot.send_photo(chat_id=message.chat.id, photo=types.FSInputFile("matrix_rus.jpg"))

@dp.message(F.text =="ℹ️ Помощь")
async def echo_message(message: types.Message):
    await message.answer(f"Угадываем загаданное 6-буквенное слово. Если буква на своем месте - это отмечено зелёным, если не на своём - жёлтым, ну а если буквы нет вовсе - фон белый.")

@dp.message(F.text =="⚙️ Settings")
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(play.mode)
    await message.answer(
        f"Choose your mode to play",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Hard mode"),
                    KeyboardButton(text="Normal mode"),
                ]
            ], resize_keyboard=True,
        ),
    )
@dp.message(F.text =="Посложнее",  StateFilter(play.mode))
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(default_state)
    await message.answer(f"Сложный режим включён!\nУдачи!", reply_markup=get_rus_keyboard())
@dp.message(F.text =="Hard mode",  StateFilter(play.mode))
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(default_state)
    await message.answer(f"My respect!\nHard mode is ON", reply_markup=get_eng_keyboard())
@dp.message(F.text =="Обычная",  StateFilter(play.mode))
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(default_state)
    await message.answer(f"Обычный режим включён!\nУдачи!", reply_markup=get_rus_keyboard())
@dp.message(F.text =="Normal mode",  StateFilter(play.mode))
async def echo_message(message: types.Message, state: FSMContext):
    await state.set_state(default_state)
    await message.answer(f"Normal mode is ON", reply_markup=get_eng_keyboard())
@dp.message(F.text =="⚙️ Настройки")
async def echo_message(message: types.Message, state: FSMContext):
        await state.set_state(play.mode)
        await message.answer(
        f"Режим сложности игры",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Обычная"),
                    KeyboardButton(text="Посложнее"),
                ]
            ], resize_keyboard=True,
        ),
    )

# Обработчик текстовых сообщений
@dp.message(F.text, StateFilter(play.in_game))
async def echo_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    usedletters = user_data['usedlt']
    #await message.answer(text=f"Вы выбрали {user_data['lang']}.")
    if len(message.text) != 6:
        #await message.answer(f"В в!", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"В слове должно быть 6 буков!", reply_markup=types.ReplyKeyboardRemove())
        #await message.answer(f"Enter 6-letter word!", reply_markup=types.ReplyKeyboardRemove())
    else:
        #обработка 6-буквенного слова.
        #print(usedletters)
        tr = message.text.lower()
        # Let's insert used letters into the array to store them.
        for l in tr:
            if l not in usedletters:
                usedletters.append(l)
        await state.update_data(usedlt = usedletters)
        #print(usedletters)
        ans = user_data['word']
        #await message.answer(f"Загадано {user_data['word']}", reply_markup=types.ReplyKeyboardRemove())
        fl = False
        t = user_data['tr'] # номер попытки текущей.
        if t > 5:
            t -= 5 # нужно чтобы рисовать на новом листе. При этом в user_data['tr'] надо хранить правильный номер.
        pict_path = user_data['pict_path'] + str(t)+".jpg"
        new_img = Image.open(pict_path)
        font = ImageFont.truetype("arial.ttf", 65)
        pencil = ImageDraw.Draw(new_img)
        used = [0,0,0,0,0,0]
        for ch in range(6):
            if tr[ch] == ans[ch]:
                pencil.rectangle([30+ch*95,30+(t-1)*95,110+ch*95,110+95*(t-1)],fill = (150, 255, 150, 0), outline = 'black', width = 1)
                pencil.text((50+ch*95,35+95*(t-1)),tr[ch], font=font, fill='gray')
                used[ch] = 1
        for ch in range(6):    
            if tr[ch] != ans[ch]:
                fl = True
                b = False
                for k in range(6):
                    if (tr[ch] == ans[k]) and (used[k] == 0) and not b:
                        b = True
                        used[k] = 1
                if b:
                    pencil.rectangle([30+ch*95,30+(t-1)*95,110+ch*95,110+95*(t-1)],fill = (255, 255, 150, 0), outline = 'black', width = 1)
                    pencil.text((50+ch*95,35+95*(t-1)),tr[ch], font=font, fill='gray')
                else:
                    pencil.rectangle([30+ch*95,30+(t-1)*95,110+ch*95,110+95*(t-1)],fill = (255, 255, 255, 0), outline = 'black', width = 1)
                    pencil.text((50+ch*95,35+95*(t-1)),tr[ch], font=font, fill='gray')
        pencil.rectangle([220,570,245,600],fill = (255, 255, 255, 0), outline = 'white', width = 1)
        font = ImageFont.truetype("arial.ttf", 28)
        pencil.text((230,570),str(user_data['tr']), font=font, fill='black')
        # Let's color out used letters.
        font = ImageFont.truetype("arial.ttf", 35)
        for l in usedletters:
            if l == "а":      
                pencil.rectangle([20,630,65,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30,635),"A", font=font, fill='black')
            if l == "б":      
                pencil.rectangle([20+53,630,65+53,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53,635),"Б", font=font, fill='black')
            if l == "в":      
                pencil.rectangle([20+53*2,630,65+53*2,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*2,635),"В", font=font, fill='black')
            if l == "г":      
                pencil.rectangle([20+53*3,630,65+53*3,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*3,635),"Г", font=font, fill='black')
            if l == "д":      
                pencil.rectangle([20+53*4,630,65+53*4,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*4,635),"Д", font=font, fill='black')
            if l == "е":      
                pencil.rectangle([20+53*5,630,65+53*5,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*5,635),"Е", font=font, fill='black')
            if l == "ё":      
                pencil.rectangle([20+53*6,630,65+53*6,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*6,635),"Ё", font=font, fill='black')
            if l == "ж":      
                pencil.rectangle([20+53*7,630,65+53*7,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*7,635),"Ж", font=font, fill='black')
            if l == "з":      
                pencil.rectangle([20+53*8,630,65+53*8,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*8,635),"З", font=font, fill='black')
            if l == "и":      
                pencil.rectangle([20+53*9,630,65+53*9,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*9,635),"и", font=font, fill='black')
            if l == "й":      
                pencil.rectangle([20+53*10,630,65+53*10,675],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*10,635),"Й", font=font, fill='black')
            #######################
            if l == "к":      
                pencil.rectangle([20,630+53*1,65,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30,635+53*1),"К", font=font, fill='black')
            if l == "л":      
                pencil.rectangle([20+53,630+53*1,65+53,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53,635+53*1),"Л", font=font, fill='black')
            if l == "м":      
                pencil.rectangle([20+53*2,630+53*1,65+53*2,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*2,635+53*1),"М", font=font, fill='black')
            if l == "н":      
                pencil.rectangle([20+53*3,630+53*1,65+53*3,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*3,635+53*1),"Н", font=font, fill='black')
            if l == "о":      
                pencil.rectangle([20+53*4,630+53*1,65+53*4,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*4,635+53*1),"О", font=font, fill='black')
            if l == "п":      
                pencil.rectangle([20+53*5,630+53*1,65+53*5,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*5,635+53*1),"П", font=font, fill='black')
            if l == "р":      
                pencil.rectangle([20+53*6,630+53*1,65+53*6,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*6,635+53*1),"Р", font=font, fill='black')
            if l == "с":      
                pencil.rectangle([20+53*7,630+53*1,65+53*7,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*7,635+53*1),"С", font=font, fill='black')
            if l == "т":      
                pencil.rectangle([20+53*8,630+53*1,65+53*8,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*8,635+53*1),"Т", font=font, fill='black')
            if l == "у":      
                pencil.rectangle([20+53*9,630+53*1,65+53*9,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*9,635+53*1),"У", font=font, fill='black')
            if l == "ф":      
                pencil.rectangle([20+53*10,630+53*1,65+53*10,675+53*1],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*10,635+53*1),"Ф", font=font, fill='black')
            ######################
            if l == "х":      
                pencil.rectangle([20,630+53*2,65,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30,635+53*2),"Х", font=font, fill='black')
            if l == "ц":      
                pencil.rectangle([20+53,630+53*2,65+53,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53,635+53*2),"Ц", font=font, fill='black')
            if l == "ч":      
                pencil.rectangle([20+53*2,630+53*2,65+53*2,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*2,635+53*2),"Ч", font=font, fill='black')
            if l == "ш":      
                pencil.rectangle([20+53*3,630+53*2,65+53*3,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*3,635+53*2),"Ш", font=font, fill='black')
            if l == "щ":      
                pencil.rectangle([20+53*4,630+53*2,65+53*4,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*4,635+53*2),"Щ", font=font, fill='black')
            if l == "ъ":      
                pencil.rectangle([20+53*5,630+53*2,65+53*5,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*5,635+53*2),"Ъ", font=font, fill='black')
            if l == "ы":      
                pencil.rectangle([20+53*6,630+53*2,65+53*6,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*6,635+53*2),"Ы", font=font, fill='black')
            if l == "ь":      
                pencil.rectangle([20+53*7,630+53*2,65+53*7,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*7,635+53*2),"Ь", font=font, fill='black')
            if l == "э":      
                pencil.rectangle([20+53*8,630+53*2,65+53*8,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*8,635+53*2),"Э", font=font, fill='black')
            if l == "ю":      
                pencil.rectangle([20+53*9,630+53*2,65+53*9,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*9,635+53*2),"Ю", font=font, fill='black')
            if l == "я":      
                pencil.rectangle([20+53*10,630+53*2,65+53*10,675+53*2],fill = (140, 140, 140, 0), outline = 'black', width = 1)
                pencil.text((30+53*10,635+53*2),"Я", font=font, fill='black')
        # Let's return font to the normal mode.
        font = ImageFont.truetype("arial.ttf", 65)
        pict_path = user_data['pict_path'] + str(t+1)+".jpg"
        new_img.save(pict_path)
        await bot.send_photo(chat_id=message.chat.id, photo=types.FSInputFile(pict_path))
        t = user_data['tr']
        await state.update_data(tr = t + 1)
        if not fl:
            # слово угадано!
            await message.answer(f"Да, это оно!\nПоздравления победителю!🌟🎉", reply_markup=get_rus_keyboard())
            await state.set_state(default_state)
        else:
            if t == 11:
                # угадать не удалось...
                await message.answer(f"Загадано {user_data['word']}", reply_markup=types.ReplyKeyboardRemove())
                await message.answer(f"Что ж, было непросто...", reply_markup=get_rus_keyboard())
                await state.set_state(default_state)
            else:
                await message.answer(f"Продолжайте угадывать!", reply_markup=types.ReplyKeyboardRemove())

# Запуск бота
async def main():
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())