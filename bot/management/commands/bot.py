import os
import time

from telebot import TeleBot, types
from django.core.management.base import BaseCommand

from bot.views import get_user_orders, get_serialized_order
from bot.models import Client, Cake, Levels, Shape

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
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'price_list':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu;keep_previous')
        markup.add(button)
        with open('price_list.jpg', 'rb+') as file:
            bot.send_photo(call.message.chat.id, caption='Вот наше меню с ценами.', photo=file, reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'my_orders':
        my_orders(call.message)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data.startswith('main_menu'):
        main_menu(call.message)
        if 'keep_previous' not in call.data:
            bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'choose_prebuilt_cake':
        choose_prebuilt_cake(call.message)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'cake_constructor':
        cake = Cake.objects.create()
        choose_level(call.message, cake)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data.startswith('view_order'):
        call_data = call.data.split(';')
        order_id = call_data[1]
        view_order(call.message, order_id)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data.startswith('choose_shape'):
        callback = call.data.split(';')
        cake_id = callback[1]
        level_id = callback[2]
        cake = Cake.objects.get(id=cake_id)
        cake.level = Levels.objects.get(id=level_id)
        cake.save()
        choose_shape(call.message, cake)


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
    buttons = [types.InlineKeyboardButton(text=cake.title, callback_data=f'choose_cake_text;{cake.id}') for cake in original_cakes]
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
