from telebot import TeleBot, types
import datetime

bot = TeleBot('6017270704:AAH9MTfQELdHSXbbCAwfPQXL-47Xnuhf0p8')

# Словари с опциями и ценами
levels = {'1 уровень': 400, '2 уровня': 750, '3 уровня': 1100}
shapes = {'Квадрат': 600, 'Круг': 400, 'Прямоугольник': 1000}
toppings = {'Без топпинга': 0, 'Белый соус': 200, 'Карамельный сироп': 180, 'Кленовый сироп': 200, 'Клубничный сироп': 300, 'Черничный сироп': 350, 'Молочный шоколад': 200}
berries = {'Ежевика': 400, 'Малина': 300, 'Голубика': 450, 'Клубника': 500}
decor = {'Фисташки': 300, 'Безе': 400, 'Фундук': 350, 'Пекан': 300, 'Маршмеллоу': 200, 'Марципан': 280}
inscription = {'Инпут ввода': 500}

# Словарь для хранения информации о заказе
order = {}

@bot.message_handler(commands=['start'])
def main_menu(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Заказать торт', callback_data='order_cake'),
               types.InlineKeyboardButton(text='Прайс-лист', callback_data='price_list'),
               types.InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')]
    for btn in buttons:
        markup.add(btn)
    bot.send_message(message.chat.id, 'Добро пожаловать в Главное Меню!',
                     reply_markup=markup, protect_content=True)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'order_cake':
        order_cake(call.message.chat.id)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data.startswith('level_'):
        process_level(call)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data.startswith('shape_'):
        process_shape(call)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data.startswith('topping_'):
        process_topping(call)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data.startswith('berry_'):
        process_berries(call)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data.startswith('decor_'):
        process_decor(call)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data.startswith('inscription_'):
        process_inscription(call)
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data == 'confirm_order':
        confirm_order(call)
        bot.delete_message(call.message.chat.id, call.message.id)
    
    # Добавить обработку других callback_data

def order_cake(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text='Выбрать из готовых', callback_data='prebuilt_cake'),
               types.InlineKeyboardButton(text='Собрать свой торт', callback_data='cake_constructor'),
               types.InlineKeyboardButton(text='Добавить комментарий', callback_data='add_comment'),
               types.InlineKeyboardButton(text='Указать адрес доставки', callback_data='add_address'),
               types.InlineKeyboardButton(text='Указать дату доставки', callback_data='add_date'),
               types.InlineKeyboardButton(text='Указать время доставки', callback_data='add_time')]
    markup.add(*buttons)
    bot.send_message(chat_id, 'Отлично, давай закажем торт!', reply_markup=markup, protect_content=True)

def process_comment(message):
    order['comment'] = message.text
    bot.send_message(message.chat.id, 'Комментарий добавлен!')

# Добавить функции для обработки других callback_data

@bot.callback_query_handler(func=lambda call: call.data == 'add_address')
def ask_for_address(call):
    msg = bot.send_message(call.message.chat.id, 'Введите адрес доставки:')
    bot.register_next_step_handler(msg, process_address)


def process_address(message):
    order['address'] = message.text
    bot.send_message(message.chat.id, 'Адрес добавлен!')

@bot.callback_query_handler(func=lambda call: call.data == 'add_date')
def ask_for_date(call):
    msg = bot.send_message(call.message.chat.id, 'Введите дату доставки в формате дд-мм-гггг:')
    bot.register_next_step_handler(msg, process_date)


def process_date(message):
    date = datetime.datetime.strptime(message.text, '%d-%m-%Y')
    order['date'] = date
    bot.send_message(message.chat.id, 'Дата добавлена!')

@bot.callback_query_handler(func=lambda call: call.data == 'add_time')
def ask_for_time(call):
    msg = bot.send_message(call.message.chat.id, 'Введите время доставки в формате чч:мм:')
    bot.register_next_step_handler(msg, process_time)


def process_time(message):
    time = datetime.datetime.strptime(message.text, '%H:%M').time()
    order['time'] = time
    bot.send_message(message.chat.id, 'Время добавлено!')
    
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('level_'))
def process_level(call):
    level = call.data.split('_')[1]
    order['level'] = level
    bot.send_message(call.message.chat.id, f'Уровень торта выбран: {level}')
    choose_shape(call.message)

def choose_shape(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text=shape, callback_data=f'shape_{shape}') for shape in shapes.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выберите форму торта:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('shape_'))
def process_shape(call):
    shape = call.data.split('_')[1]
    order['shape'] = shape
    bot.send_message(call.message.chat.id, f'Форма торта выбрана: {shape}')
    choose_topping(call.message)

def choose_topping(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text=topping, callback_data=f'topping_{topping}') for topping in toppings.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выберите топпинг:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('topping_'))
def process_topping(call):
    topping = call.data.split('_')[1]
    order['topping'] = topping
    bot.send_message(call.message.chat.id, f'Топпинг выбран: {topping}')
    choose_berries(call.message)

def choose_berries(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text=berry, callback_data=f'berry_{berry}') for berry in berries.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выберите ягоды:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('berry_'))
def process_berries(call):
    berry = call.data.split('_')[1]
    order['berry'] = berry
    bot.send_message(call.message.chat.id, f'Ягоды выбраны: {berry}')
    choose_decor(call.message)

def choose_decor(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text=dec, callback_data=f'decor_{dec}') for dec in decor.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выберите декор:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('decor_'))
def process_decor(call):
    dec = call.data.split('_')[1]
    order['decor'] = dec
    bot.send_message(call.message.chat.id, f'Декор выбран: {dec}')
    choose_inscription(call.message)

def choose_inscription(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text=ins, callback_data=f'inscription_{ins}') for ins in inscription.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выберите надпись:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('inscription_'))
def process_inscription(call):
    ins = call.data.split('_')[1]
    order['inscription'] = ins
    bot.send_message(call.message.chat.id, f'Надпись выбрана: {ins}')
    finalize_order(call.message)

def finalize_order(message):
    order_summary = "Ваш заказ:\n"
    for key, value in order.items():
        order_summary += f"{key}: {value}\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    confirm_button = types.InlineKeyboardButton(text="Подтвердить заказ", callback_data="confirm_order")
    markup.add(confirm_button)
    bot.send_message(message.chat.id, order_summary, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_order')
def confirm_order(call):
    # обработать подтверждение заказа в базу данных
    bot.send_message(call.message.chat.id, "Ваш заказ подтвержден и отправлен в обработку!")
    order.clear()

def main():
    bot.polling()
    
if __name__ == '__main__':
    main()