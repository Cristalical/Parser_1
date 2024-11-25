from bs4 import BeautifulSoup
import requests

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from saving import save
from main import dp, bot

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сделать запрос")],
            [KeyboardButton(text="Посмотреть MCC")]
        ],
        resize_keyboard=True
    )
    await message.answer('''Привет!\nЭтот бот создан для быстрого получения MCC кодов.\nЧтобы перейти к поиску, нажми кнопку или напиши /s.\nДля просмотра существующих MCC напиши /p или воспользуйся кнопкой.''', reply_markup=keyboard)

'''---------------------------------------------------------------------------------------------------------------------------------------------'''

@dp.message(F.text == "Посмотреть MCC")
async def command_p(message: Message):
    await cmd_p(message)

# Обработчик команды /p
@dp.message(Command("p"))
async def cmd_p(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text="Транспорт", callback_data='transport')],
        [InlineKeyboardButton(text="Фаст Фуд", callback_data='fast_food')],
        [InlineKeyboardButton(text="Фото, Видео", callback_data='photo_video')],
        [InlineKeyboardButton(text="Цветы", callback_data='flowers')],
        [InlineKeyboardButton(text="Duty Free", callback_data='duty_free')],
    ],
        resize_keyboard=True
    )
    await message.answer('Выберите категорию', reply_markup=keyboard)

@dp.callback_query(F.data == 'transport')
async def subj_1(call: CallbackQuery):
    await call.answer()
    await call.message.answer('''4111, 4121, 4131, 4457, 4468, 4784, 4789, 5013, 5271, 5551, 5561, 5592, 5598, 5599, 7511, 7523''')

@dp.callback_query(F.data == 'fast_food')
async def subj_2(call: CallbackQuery):
    await call.answer()
    await call.message.answer('''5814''')

@dp.callback_query(F.data == 'photo_video')
async def subj_3(call: CallbackQuery):
    await call.answer()
    await call.message.answer('''5044, 5045, 5946, 7332, 7333, 7338, 7339, 7395''')

@dp.callback_query(F.data == 'flowers')
async def subj_4(call: CallbackQuery):
    await call.answer()
    await call.message.answer('''5193, 5992''')

@dp.callback_query(F.data == 'duty_free')
async def subj_5(call: CallbackQuery):
    await call.answer()
    await call.message.answer('''5309''')

'''---------------------------------------------------------------------------------------------------------------------------------------------'''

@dp.message(F.text == "Сделать запрос")
async def command_s(message: Message, state: FSMContext):
    await cmd_s(message, state)

# Состояние для FSM
class Form(StatesGroup):
    waiting_for_input = State()

# Обработчик команды /s
@dp.message(Command("s"))
async def cmd_s(message: Message, state: FSMContext):
    await message.answer('Введите ваш запрос:')
    await state.set_state(Form.waiting_for_input)

# Функция для извлечения ссылок из span элементов
def extract_links(span_elements):
    links = []
    for span in span_elements:
        a_tags = span.find_all('a')
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href:
                links.append(href)
    return links

# Обработчик ввода пользователя (парсинг)
@dp.message(Form.waiting_for_input)
async def process(message: Message, state: FSMContext):
    user_input = message.text
    await state.clear()

    # Создание состояния
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_document")

    # Формирование URL для запросов
    url_1 = f"https://mcc-codes.ru/search/?q={user_input}"
    url_2 = f"https://mcc-cod.ru/result-search-mcc.html?search={user_input}"

    # Запросы к сайтам
    response_1 = requests.get(url_1)
    response_2 = requests.get(url_2)

    # Парсинг данных с первого сайта
    soup_1 = BeautifulSoup(response_1.text, 'lxml')
    data_list_1 = parse_mcc_codes_ru(soup_1)

    # Парсинг данных со второго сайта
    soup_2 = BeautifulSoup(response_2.text, 'lxml')
    data_list_2 = parse_mcc_cod_ru(soup_2)

    # Объединение данных
    data_list = data_list_1 + data_list_2

    # Сохранение данных и отправка файла пользователю
    save(data_list)
    doc = FSInputFile("result_mcc.xlsx")
    await message.reply_document(doc)

# Парсинг данных с сайта mcc-codes.ru
def parse_mcc_codes_ru(soup):
    data_list = []
    rows = soup.find_all('tr')
    for row in rows:
        if 'td' in str(row):
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            data_list.append(row_data)
    return data_list

# Парсинг данных с сайта mcc-cod.ru
def parse_mcc_cod_ru(soup):
    data_list = []
    paging_div = soup.find_all('span', class_='simplesearch-page')
    links = extract_links(paging_div)
    links.insert(0, 'result-search-mcc.html?search=4111&simplesearch_offset=00')

    for link in links:
        url = f'https://mcc-cod.ru/{link}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        rows = soup.find_all('tr')
        for row in rows:
            if 'td' in str(row):
                cells = row.find_all('td')
                mcc_code = cells[3].find('a').text
                name = cells[0].find('a').text
                address = cells[1].text
                link = cells[2].find('a')['href']
                row_data = [mcc_code, name, address, link if link != 'http://' else '']
                data_list.append(row_data)
    return data_list


'''---------------------------------------------------------------------------------------------------------------------------------------------'''

# Регистрация всех обработчиков
def register_handlers(disp: dp):
    disp.message.register(cmd_start, Command("start"))
    disp.message.register(command_p, F.text == "Посмотреть MCC")
    disp.message.register(cmd_p, Command("p"))
    disp.callback_query.register(subj_1, F.data == 'transport')
    disp.callback_query.register(subj_2, F.data == 'fast_food')
    disp.callback_query.register(subj_3, F.data == 'photo_video')
    disp.callback_query.register(subj_4, F.data == 'flowers')
    disp.callback_query.register(subj_5, F.data == 'duty_free')
    disp.message.register(command_s, F.text == "Сделать запрос")
    disp.message.register(cmd_s, Command("s"))
    disp.message.register(process, Form.waiting_for_input)