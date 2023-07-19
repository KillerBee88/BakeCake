from telebot import TeleBot, types

import datetime
import re
import requests

from views import get_user_orders

bot = TeleBot('6017270704:AAH9MTfQELdHSXbbCAwfPQXL-47Xnuhf0p8')


@bot.message_handler(commands=['start'])
def main_menu(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Заказать торт', callback_data='order_cake'),
               types.InlineKeyboardButton(text='Прайс-лист', callback_data='price_list'),
               types.InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Добро пожаловать в Главное Меню! Время заказывать тортики!',
                     reply_markup=markup,)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'order_cake':
        order_cake(call.message.chat.id)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'price_list':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
        markup.add(button)
        with open('price_list.jpg', 'rb+') as file:
            bot.send_photo(call.message.chat.id, caption='Вот наше меню с ценами.', photo=file, reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'my_orders':
        my_orders(call.message)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'main_menu':
        main_menu(call.message)
    if call.data == 'prebuilt_cake':
        markup = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text='Верона', callback_data='o1'),
                   types.InlineKeyboardButton(text='Восточный', callback_data='p2'),
                   types.InlineKeyboardButton(text='Шоколадно-банановый', callback_data='m3'),
                   types.InlineKeyboardButton(text='Чёрный лес', callback_data='b4'),
                   types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')]
        markup.add(*buttons)
        with open('ready_cakes.jpg', 'rb+') as file:
            bot.send_photo(call.message.chat.id, caption='Выбирай торт на свой вкус!! (Это заглушка).', photo=file,
                           reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'cake_constructor':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
        markup.add(button)
        bot.send_message(call.message.chat.id, 'Здесь будет инженер-конструктор', reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.id)
    if call.data == 'view_order':
        view_order()
        bot.delete_message(call.message.chat.id, call.message.id)


def my_orders(message):

    id_telegram = message.user.id
    orders = get_user_orders(id_telegram=id_telegram)
    markup = types.InlineKeyboardMarkup()
    orders_buttons = [types.InlineKeyboardButton(text=order['description'], callback_data='view_order') for order in orders]
    button = types.InlineKeyboardButton(text='В Главное Меню', callback_data='main_menu')
    markup.add(*orders_buttons, button)
    bot.send_message(message.chat.id, 'Список твоих последних заказов.', reply_markup=markup)


def view_order(message):
    pass


def order_cake(chat_id):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Выбрать из готовых', callback_data='prebuilt_cake'),
               types.InlineKeyboardButton(text='Собрать свой торт', callback_data='cake_constructor')]
    for btn in buttons:
        markup.add(btn)
    bot.send_message(chat_id, 'Отлично, давай закажем торт!',
                     reply_markup=markup, )


def main():
    bot.polling()


if __name__ == '__main__':
    main()
