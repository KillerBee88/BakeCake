import os
import time
from datetime import datetime, timedelta

from telebot import TeleBot, types
from django.core.management.base import BaseCommand

from bot.views import get_user_orders, get_serialized_order
from bot.models import Client, Cake, Levels, Shape, Topping, Berries, Decor, Order

bot = TeleBot('5969598197:AAHdFTkY8adzmcP3OgVig0pDLiQ8r61mOts')


@bot.message_handler(commands=['start'])
def main_menu(message):
    client = Client.objects.get_or_create(id_telegram=message.from_user.id)[0]
    client.name = f'{message.from_user.first_name}'
    client.save()
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Заказать торт', callback_data='order_cake'),
               types.InlineKeyboardButton(text='Прайс-лист', callback_data='price_list'),
               types.InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Добро пожаловать в Главное Меню! Время заказывать тортики!',
                     reply_markup=markup, )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'order_cake':
        order_cake(call.message.chat.id)
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data == 'price_list':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu;keep_previous')
        markup.add(button)
        with open('price_list.jpg', 'rb+') as file:
            bot.send_photo(call.message.chat.id, caption='Вот наше меню с ценами.', photo=file, reply_markup=markup)
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data == 'my_orders':
        my_orders(call.message)
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data.startswith('main_menu'):
        main_menu(call.message)
        if 'keep_previous' not in call.data:
            pass
            #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data == 'choose_prebuilt_cake':
        choose_prebuilt_cake(call.message)
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data == 'cake_constructor':
        cake = Cake.objects.create()
        choose_level(call.message, cake)
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data.startswith('view_order'):
        call_data = call.data.split(';')
        order_id = call_data[1]
        view_order(call.message, order_id)
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data.startswith('choose_shape'):
        callback = call.data.split(';')
        cake_id = callback[1]
        level_id = callback[2]
        cake = Cake.objects.get(id=cake_id)
        cake.levels = Levels.objects.get(id=level_id)
        cake.save()
        choose_shape(call.message, cake)
    elif call.data.startswith('choose_topping'):
        callback = call.data.split(';')
        cake_id = callback[1]
        shape_id = callback[2]
        cake = Cake.objects.get(id=cake_id)
        cake.shape = Shape.objects.get(id=shape_id)
        cake.save()
        choose_topping(call.message, cake)
    elif call.data.startswith('choose_berries'):
        callback = call.data.split(';')
        cake_id = callback[1]
        topping_id = callback[2]
        cake = Cake.objects.get(id=cake_id)
        cake.topping = Topping.objects.get(id=topping_id)
        cake.save()
        choose_berries(call.message, cake)
    elif call.data.startswith('choose_decor'):
        callback = call.data.split(';')
        cake_id = callback[1]
        berries_id = callback[2]
        cake = Cake.objects.get(id=cake_id)
        cake.berries = Berries.objects.get(id=berries_id)
        cake.save()
        choose_decor(call.message, cake)
    elif call.data.startswith('choose_cake_text'):
        callback = call.data.split(';')
        cake_id = callback[1]
        decor_id = callback[2]
        if decor_id:
            cake = Cake.objects.get(id=cake_id)
            cake.decor = Decor.objects.get(id=decor_id)
            cake.save()
        #bot.set_state(call.message.from_user.id, 'choose_cake_text')
        buttons = [types.InlineKeyboardButton(text='Без надписи', callback_data=f'create_order;{cake_id};')]
        markup = types.InlineKeyboardMarkup()
        markup.add(*buttons)
        msg = bot.send_message(call.message.chat.id, 'Хочешь добавить надпись на торт? Если да, то напиши её.', reply_markup=markup)
        bot.register_next_step_handler(msg, set_cake_text, cake_id)

    elif call.data.startswith('create_order'):
        callback = call.data.split(';')
        cake_id = callback[1]
        cake = Cake.objects.get(id=cake_id)
        user = Client.objects.get(id_telegram=call.message.chat.id)
        order = Order.objects.create(cake=cake, client=user)
        msg = bot.send_message(call.message.chat.id, 'Введите адрес доставки.')
        bot.register_next_step_handler(msg, set_delivery_adress, order.id)

    elif call.data.startswith('get_delivery_datetime'):
        callback = call.data.split(';')
        order_id = callback[1]
        get_order_date(call.message, order_id)

    elif call.data.startswith('set_date'):
        callback = call.data.split(';')
        order_id = callback[1]
        date_str = callback[2]
        date = datetime.strptime(date_str, "%d.%m.%Y")
        order = Order.objects.get(id=order_id)
        order.delivery_dt = date
        order.save()
        get_order_time(call.message, order_id, date_str)

    elif call.data.startswith('set_time'):
        callback = call.data.split(';')
        order_id = callback[1]
        date_str = callback[2]
        date = datetime.strptime(date_str, "%d.%m.%Y_%H:%M")
        order = Order.objects.get(id=order_id)
        order.delivery_dt = date
        order.save()
        accept_order(call.message, order_id)

    elif call.data.startswith('accept_order'):
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
        markup.add(button)
        bot.send_message(call.message.chat.id, f'Ожидайте доставку вашего тортика!', reply_markup=markup)

    elif call.data.startswith('cancel_order'):
        callback = call.data.split(';')
        order_id = callback[1]
        Order.objects.get(id=order_id).delete()
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
        markup.add(button)
        bot.send_message(call.message.chat.id, f'Заказ отменён.', reply_markup=markup)

def accept_order(message, order_id):
    order = Order.objects.get(id=order_id)
    order.text = message.text
    order.save()

    buttons = [types.InlineKeyboardButton(text='Да', callback_data=f'accept_order;{order_id};'),
               types.InlineKeyboardButton(text='Нет', callback_data=f'cancel_order;{order_id};')]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)

    bot.send_message(message.chat.id, f'Вот ваш заказ:\n{order}\nПодтверждаете заказ?', reply_markup=markup)


def get_order_time(message, order_id, date_str):
    base = datetime.strptime(f'{date_str}_10.00', '%d.%m.%Y_%H.%M')
    time_list = [base + timedelta(hours=x) for x in range(8)]

    buttons = [types.InlineKeyboardButton(text=f'{date.strftime("%H:%M")}',
                                          callback_data=f'set_time;{order_id};{date.strftime("%d.%m.%Y_%H:%M")};') for date in
               time_list]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)

    bot.send_message(message.chat.id,
                     'Выберите время доставки.',
                     reply_markup=markup)


def get_order_date(message, order_id):
    base = datetime.today()
    date_list = [base + timedelta(days=x) for x in range(1, 6)]

    buttons = [types.InlineKeyboardButton(text=f'{date.strftime("%d.%m")}', callback_data=f'set_date;{order_id};{date.strftime("%d.%m.%Y")};') for date in date_list]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)

    bot.send_message(message.chat.id,
                     'Выберите дату доставки. Доставка осуществляется на следующий день и позднее. При выборе доставки на следующий день, стоимость заказа увеличивается на 20%.',
                     reply_markup=markup)


def set_delivery_adress(message, order_id):
    order = Order.objects.get(id=order_id)
    order.text = message.text
    order.save()

    buttons = [types.InlineKeyboardButton(text='Да', callback_data=f'get_delivery_datetime;{order_id};'),
               types.InlineKeyboardButton(text='Нет', callback_data=f'main_menu')]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)

    bot.send_message(message.chat.id, f'Вы согласны на обработку персональных данных?', reply_markup=markup)


def set_cake_text(message, cake_id):
    cake = Cake.objects.get(id=cake_id)
    cake.text = message.text
    cake.save()

    buttons = [types.InlineKeyboardButton(text='Оформить заказ', callback_data=f'create_order;{cake_id};'),
               types.InlineKeyboardButton(text='Создать торт заново', callback_data=f'order_cake')]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)

    bot.send_message(message.chat.id, f'Вот какой торт получился:\n{cake}', reply_markup=markup)


def choose_level(message, cake):
    levels = Levels.objects.filter(is_available=True)
    buttons = [types.InlineKeyboardButton(text=level.title, callback_data=f'choose_shape;{cake.id};{level.id}') for level in levels]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выбери количество уровней.', reply_markup=markup)


def choose_shape(message, cake):
    shapes = Shape.objects.filter(is_available=True)
    buttons = [types.InlineKeyboardButton(text=shape.title, callback_data=f'choose_topping;{cake.id};{shape.id}') for shape in shapes]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выбери форму торта.', reply_markup=markup)


def choose_topping(message, cake):
    toppings = Topping.objects.filter(is_available=True)
    buttons = [types.InlineKeyboardButton(text=topping.title, callback_data=f'choose_berries;{cake.id};{topping.id}') for topping in toppings]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выбери топпинг.', reply_markup=markup)


def choose_berries(message, cake):
    berries = Berries.objects.filter(is_available=True)
    buttons = [types.InlineKeyboardButton(text=berry.title, callback_data=f'choose_decor;{cake.id};{berry.id}') for berry in berries]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выбери ягоды.', reply_markup=markup)


def choose_decor(message, cake):
    decors = Decor.objects.filter(is_available=True)
    buttons = [types.InlineKeyboardButton(text=decor.title, callback_data=f'choose_cake_text;{cake.id};{decor.id}') for decor in decors]
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выбери декор.', reply_markup=markup)


def my_orders(message):
    id_telegram = message.chat.id
    orders = get_user_orders(id_telegram=id_telegram)
    markup = types.InlineKeyboardMarkup()
    orders_buttons = [types.InlineKeyboardButton(text=order['description'], callback_data=f'view_order;{order["id"]}')
                      for order in orders]
    button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
    markup.add(*orders_buttons, button)
    bot.send_message(message.chat.id, 'Список твоих последних заказов.', reply_markup=markup)


def view_order(message, order_id):
    order = get_serialized_order(order_id)
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
    markup.add(button)
    bot.send_message(message.chat.id, f'Данные о твоём заказе:\n{order}', reply_markup=markup)


def order_cake(chat_id):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Выбрать из готовых', callback_data='choose_prebuilt_cake'),
               types.InlineKeyboardButton(text='Собрать свой торт', callback_data='cake_constructor'),
               types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')]
    for btn in buttons:
        markup.add(btn)
    bot.send_message(chat_id, 'Отлично, давай закажем торт!',
                     reply_markup=markup, )


def choose_prebuilt_cake(message):
    original_cakes = Cake.objects.filter(is_original=True)
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text=cake.title, callback_data=f'choose_cake_text;{cake.id};') for cake in original_cakes]
    mm_but = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
    markup.add(*buttons, mm_but)
    bot.send_message(message.chat.id, 'Выбирай торт на свой вкус!', reply_markup=markup)


def main():
    bot.polling()


class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **options):
        while True:
            try:
                main()
            except Exception as error:
                print(error)
                raise SystemExit


if __name__ == '__main__':
    main()