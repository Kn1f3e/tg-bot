from aiogram import Bot, Dispatcher, executor, types
import sqlite3

# Инициализация бота
API_TOKEN = '7374634507:AAH2FNI47HjtMGJTrKK1PAeTd52b-te2ai4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Инициализация базы данных
conn = sqlite3.connect('users1.db')
cursor = conn.cursor()

# Создание таблицы для хранения состояния пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        step INTEGER,
        fio TEXT,
        city TEXT,
        department TEXT
    )
''')
conn.commit()


cursor.execute('''
    DROP TABLE thank_you;
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS thank_you (
        user_id INTEGER,
        step INTEGER,
        data TEXT
    )
''')
conn.commit()

# Функция для сохранения состояния пользователя
def save_user_state(user_id, step, fio=None, city=None, department=None):
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, step, fio, city, department)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, step, fio, city, department))
    conn.commit()

# Функция для получения состояния пользователя
def get_user_state(user_id):
    cursor.execute('SELECT step FROM users WHERE user_id = ?', (user_id,))
    ids = cursor.fetchone()
    if not (ids is None):
        ids = ids[0] 
    print(ids)
    return ids


@dp.message_handler(commands=['start'])
async def add_user_to_list(message: types.Message):
    print("start")
    save_user_state(message.from_user.id, None)


# Хэндлер для всех сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_state = get_user_state(user_id)
    print(message.text)
    if user_state is None:
        # Новый пользователь, начало регистрации
        save_user_state(user_id, 0)
        await message.answer('Привет, ты попал в робота, с которым наше день рождение пройдет еще ярче!\n\nТут ты сможешь:\n- Пройти викторину "И такое у нас"\n- Сказать "Спасибо" своим любимым коллегам\n- Собрать Фото-мозаику со своими\n\nНо сначала давайте пройдем регистрацию, чтобы мы могли подводить итоги!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Пройти регистрацию')
        await message.answer('Нажми на кнопку, чтобы начать регистрацию', reply_markup=markup)
    elif user_state == 0:
        # Пользователь нажал на кнопку "Пройти регистрацию"
        if message.text == 'Пройти регистрацию':
            save_user_state(user_id, 1)
            await message.answer('Введите ваше ФИО:')
            photo = types.InputFile('fio_photo.jpg')
            await message.answer_photo(photo)
        else:
            await message.answer('Нажми на кнопку "Пройти регистрацию", чтобы продолжить')
    elif user_state == 1:
        # Пользователь ввел ФИО
        save_user_state(user_id, 2, fio=message.text)
        await message.answer('Введите ваш город:')
        photo = types.InputFile('city_photo.jpg')
        await message.answer_photo(photo)
    elif user_state == 2:
        # Пользователь ввел город
        save_user_state(user_id, 3, city=message.text)
        await message.answer('Введите ваше подразделение:')
        photo = types.InputFile('department_photo.jpg')
        await message.answer_photo(photo)
    elif user_state == 3:
        # Пользователь ввел подразделение
        save_user_state(user_id, 4, department=message.text)
        await message.answer('Регистрация успешно завершена!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Викторина "И такое у нас есть"')
        markup.add('Сказать "Спасибо" коллегам')
        markup.add('Собрать фото-мозаику')
        await message.answer('Выберите действие:', reply_markup=markup)
    elif message.text == 'Викторина "И такое у нас есть"':
         save_user_state(user_id, 5)
    elif message.text == 'Сказать "Спасибо" коллегам':
         save_user_state(user_id, 50)
    elif user_state == 4:
        await menu(message)

    elif user_state >= 5 and user_state <= 35:
        # Пользователь отвечает на вопросы викторины
        step = user_state
        question = questions[step - 5]
        print(question)
        if step <= 25:
            print(questions[step - 6]['answer'], message.text, questions[step - 6]['answer'] == message.text)
            # Вопросы с выбором варианта ответа
            if message.text == questions[step - 6]['answer']:
                await message.answer('Верно!')
            else:
                await message.answer('Неверно.')
        else:
            # Вопросы с вводом ответа
            if message.text.lower() == questions[step - 6]['answer'].lower():
                await message.answer('Верно!')
            else:
                await message.answer('Неверно.')
        if step < 34:
            await ask_question(message)
        else:
            await message.answer('Вау, вы очень круто справились с викториной.')
            save_user_state(user_id, 4)
            await menu(message)
    
    elif user_state == 50:
        # Пользователь ввел сообщение для коллеги
        save_user_state(user_id, 51)
        await message.answer('Введите ФИО коллеги:')
        photo = types.InputFile('fio_photo.jpg')
        await message.answer_photo(photo)
        save_thank_you_step(user_id, 51, message.text )
    elif user_state == 51:
        # Пользователь ввел ФИО коллеги
        save_user_state(user_id, 52)
        await message.answer('Введите подразделение коллеги:')
        photo = types.InputFile('department_photo.jpg')
        await message.answer_photo(photo)
        save_thank_you_step(user_id, 52, message.text )
    elif user_state == 52:
        # Пользователь ввел подразделение коллеги
        save_user_state(user_id, 53)
        await message.answer('Введите электронную почту коллеги:')
        photo = types.InputFile('email_photo.jpg')
        await message.answer_photo(photo)
        save_thank_you_step(user_id, 53, message.text )
    elif user_state == 53:
        # Пользователь ввел электронную почту коллеги
        email = message.text
        await message.answer('Спасибо успешно отправлено!')
        save_user_state(user_id, 4)
        await menu(message)
        save_thank_you_step(user_id, 54, message.text )


def save_thank_you_step(user_id, step, data):
    cursor.execute('''
        INSERT INTO thank_you (user_id, step, data)
        VALUES (?, ?, ?)
    ''', (user_id, step, data))
    conn.commit()


# Хэндлер для меню
@dp.message_handler(lambda message: get_user_state(message.from_user.id) == 4)
async def menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Викторина "И такое у нас есть"')
    markup.add('Сказать "Спасибо" коллегам')
    markup.add('Собрать фото-мозаику')
    await message.answer('Выберите действие:', reply_markup=markup)

async def ask_question(message):
    user_id = message.from_user.id
    step = get_user_state(user_id)
    question = questions[step - 5]
    if step <= 25:
        # Вопросы с выбором варианта ответа
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for option in question['options']:
            markup.add(option)
        await message.answer(question['text'], reply_markup=markup)
    elif step <= 35:
        # Вопросы с вводом ответа
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Введите ответ")
        await message.answer(question['text'], reply_markup=markup)
    else:
        # Викторина закончилась
        await message.answer('Вау, вы очень круто справились с викториной.')
        save_user_state(user_id, 4)
        await menu(message)
    save_user_state(user_id, step + 1)



questions = [
    {
        'text': 'Какова ваша основная цель в жизни?',
        'options': ['Карьера', 'Семья', 'Здоровье', 'Финансовая стабильность'],
        'answer': 'Карьера'
    },
    {
        'text': 'Почему вы хотите достичь этой цели?',
        'options': ['Для себя', 'Для семьи', 'Для карьеры', 'Для здоровья'],
        'answer': 'Для себя'
    },
    {
        'text': 'Какова ваша основная ценность?',
        'options': ['Команда', 'Клиент', 'Инновации', 'Качество'],
        'answer': 'Команда'
    },
    {
        'text': 'Какие ресурсы вам необходимы для достижения целей?',
        'options': ['Финансовые', 'Человеческие', 'Материальные', 'Информационные'],
        'answer': 'Финансовые'
    },
    {
        'text': 'Как вы будете измерять свой прогресс?',
        'options': ['Критерии успеха', 'Показатели эффективности', 'Отзывы клиентов', 'Самооценка'],
        'answer': 'Критерии успеха'
    },
    {
        'text': 'Какова ваша основная стратегия для достижения успеха в жизни?',
        'options': ['Планомерность', 'Адаптивность', 'Креативность', 'Рискованность'],
        'answer': 'Планомерность'
    },
    {
        'text': 'Какова ваша основная мотивация?',
        'options': ['Деньги', 'Признание', 'Самореализация', 'Удовлетворение'],
        'answer': 'Самореализация'
    },
    {
        'text': 'Какова ваша основная ценность в жизни?',
        'options': ['Семья', 'Друзья', 'Карьера', 'Здоровье'],
        'answer': 'Семья'
    },
    {
        'text': 'Какова ваша основная стратегия для достижения целей?',
        'options': ['Планомерность', 'Адаптивность', 'Креативность', 'Рискованность'],
        'answer': 'Планомерность'
    },
    {
        'text': 'Какова ваша основная характеристика как командного игрока?',
        'options': ['Коммуникабельность', 'Тeamwork', 'Лидерство', 'Креативность'],
        'answer': 'Коммуникабельность'
    },
    {
        'text': 'Какова ваша основная роль в команде?',
        'options': ['Лидер', 'Член команды', 'Эксперт', 'Новичок'],
        'answer': 'Член команды'
    },
    {
        'text': 'Какова ваша основная ценность в жизни?',
        'options': ['Семья', 'Друзья', 'Карьера', 'Здоровье'],
        'answer': 'Семья'
    },
    {
        'text': 'Какова ваша основная ценность в работе?',
        'options': ['Качество', 'Клиент', 'Команда', 'Инновации'],
        'answer': 'Качество'
    },
    {
        'text': 'Какова ваша основная мотивация в работе?',
        'options': ['Деньги', 'Признание', 'Самореализация', 'Удовлетворение'],
        'answer': 'Самореализация'
    },
        {
        'text': 'Какова ваша основная ценность в жизни?',
        'options': ['Семья', 'Друзья', 'Карьера', 'Здоровье'],
        'answer': 'Семья'
    },
    {
        'text': 'Какова ваша основная стратегия для достижения целей?',
        'options': ['Планомерность', 'Адаптивность', 'Креативность', 'Рискованность'],
        'answer': 'Планомерность'
    },
    {
        'text': 'Какова ваша основная характеристика как командного игрока?',
        'options': ['Коммуникабельность', 'Тeamwork', 'Лидерство', 'Креативность'],
        'answer': 'Коммуникабельность'
    },
    {
        'text': 'Какова ваша основная роль в команде?',
        'options': ['Лидер', 'Член команды', 'Эксперт', 'Новичок'],
        'answer': 'Член команды'
    },
    {
        'text': 'Какова ваша основная ценность в жизни?',
        'options': ['Семья', 'Друзья', 'Карьера', 'Здоровье'],
        'answer': 'Семья'
    },
    {
        'text': 'Какова ваша основная ценность в работе?',
        'options': ['Качество', 'Клиент', 'Команда', 'Инновации'],
        'answer': 'Качество'
    },
    {
        'text': 'Какова ваша основная мотивация в работе?',
        'options': ['Деньги', 'Признание', 'Самореализация', 'Удовлетворение'],
        'answer': 'Самореализация'
    },
    {
        'text': 'Как вы планируете достичь своих целей?',
        'answer': 'Разработка плана действий'
    },
    {
        'text': 'Какова ваша основная проблема в достижении целей?',
        'answer': 'Отсутствие мотивации'
    },
    {
        'text': 'Как вы планируете преодолевать эту проблему?',
        'answer': 'Разработка плана мотивации'
    },
    {
        'text': 'Как вы будете поддерживать свою мотивацию?',
        'answer': 'Разработка плана мотивации'
    },
    {
        'text': 'Как вы планируете использовать свои сильные стороны для достижения целей?',
        'answer': 'Разработка плана использования сильных сторон'
    },
    {
        'text': 'Как вы будете преодолевать свои слабые стороны?',
        'answer': 'Разработка плана преодоления слабых сторон'
    },
    {
        'text': 'Как вы планируете работать с другими людьми?',
        'answer': 'Разработка плана взаимодействия'
    },
    {
        'text': 'Как вы планируете преодолевать конфликты в команде?',
        'answer': 'Разработка плана конфликтного управления'
    },
    
    {
        'text': 'Как вы планируете адаптироваться к изменениям?',
        'answer': 'Разработка плана адаптации'
    }
]



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)