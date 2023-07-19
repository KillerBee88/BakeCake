import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

TOKEN = '6017270704:AAH9MTfQELdHSXbbCAwfPQXL-47Xnuhf0p8'

CHOOSING_LEVEL, CHOOSING_SHAPE, CHOOSING_TOPPING, CHOOSING_DECOR, CHOOSING_COMMENT, CONFIRMATION, ASKING_FOR_BERRIES = range(7)

LEVELS = {
    '1 уровень': 10,
    '2 уровня': 20,
    '3 уровня': 30
}

SHAPES = {
    'Круглая': 5,
    'Квадратная': 7,
    'Прямоугольная': 8
}

TOPPINGS = {
    'Шоколадный': 3,
    'Карамельный': 4,
    'Сливочный': 2
}

BERRIES = {
    'Клубника': 1,
    'Малина': 1,
    'Голубика': 1
}

DECOR = {
    'Цветы': 2,
    'Фигурки': 2,
    'Бантики': 1
}


def start(update, context):
    reply_keyboard = [['Создать торт']]
    update.message.reply_text(
        'Добро пожаловать в наш магазин тортов на заказ! Чтобы создать торт, нажмите "Создать торт".',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )


def cancel(update, context):
    update.message.reply_text(
        'Заказ отменен. Если у вас есть еще вопросы, обращайтесь!'
    )
    return ConversationHandler.END


def create_cake(update, context):
    reply_keyboard = [[key for key in LEVELS]]
    update.message.reply_text(
        'Выберите количество уровней торта:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_LEVEL


def choose_level(update, context):
    context.user_data['level'] = LEVELS[update.message.text]
    reply_keyboard = [[key for key in SHAPES]]
    update.message.reply_text(
        'Выберите форму торта:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_SHAPE


def choose_shape(update, context):
    context.user_data['shape'] = SHAPES[update.message.text]
    reply_keyboard = [[key for key in TOPPINGS]]
    update.message.reply_text(
        'Выберите топпинг для торта:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_TOPPING


def choose_topping(update, context):
    context.user_data['topping'] = TOPPINGS[update.message.text]
    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        'Желаете добавить ягоды к торту?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASKING_FOR_BERRIES


def choose_berries(update, context):
    if update.message.text == 'Да':
        reply_keyboard = [[key for key in BERRIES]]
        update.message.reply_text(
            'Выберите ягоды для торта:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return ASKING_FOR_BERRIES
    else:
        context.user_data['berries'] = 0
        reply_keyboard = [[key for key in DECOR]]
        update.message.reply_text(
            'Выберите декор для торта:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOOSING_DECOR


def choose_decor(update, context):
    context.user_data['decor'] = DECOR[update.message.text]
    reply_keyboard = [['Пропустить']]
    update.message.reply_text(
        'Введите комментарий к заказу (необязательно):',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_COMMENT

def choose_comment(update, context):
    user_input = update.message.text
    if user_input != 'Пропустить':
        context.user_data['comment'] = user_input
    else:
        context.user_data['comment'] = ''
    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        'Желаете подтвердить заказ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CONFIRMATION


def confirm_order(update, context):
    if update.message.text == 'Да':
        level = context.user_data['level']
        shape = context.user_data['shape']
        topping = context.user_data['topping']
        berries = context.user_data.get('berries', 0)
        decor = context.user_data.get('decor', 0)
        comment = context.user_data.get('comment', 'Нет комментария')

        
        total_price = level + shape + topping + berries + decor

        
        update.message.reply_text(
            f'Ваш заказ принят!\n\n'
            f'Количество уровней: {level}\n'
            f'Форма торта: {shape}\n'
            f'Топпинг: {topping}\n'
            f'Ягоды: {berries}\n'
            f'Декор: {decor}\n'
            f'Комментарий: {comment}\n\n'
            f'Общая стоимость заказа: {total_price} руб.'
        )

        
        context.user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Заказ отменен. Если у вас есть еще вопросы, обращайтесь!'
        )

        context.user_data.clear()
        return ConversationHandler.END


def unknown_command(update, context):
    update.message.reply_text(
        'Извините, я не понимаю эту команду. Пожалуйста, используйте кнопки для взаимодействия с ботом.'
    )


def error(update, context):
    logging.error(f'Ошибка: {context.error}')
    update.message.reply_text(
        'Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.'
    )


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
              MessageHandler(Filters.regex('^Создать торт$'), create_cake)],
        states={
            CHOOSING_LEVEL: [MessageHandler(Filters.text, choose_level)],
            CHOOSING_SHAPE: [MessageHandler(Filters.text, choose_shape)],
            CHOOSING_TOPPING: [MessageHandler(Filters.text, choose_topping)],
            ASKING_FOR_BERRIES: [MessageHandler(Filters.text, choose_berries)],
            CHOOSING_DECOR: [MessageHandler(Filters.text, choose_decor)],
            CHOOSING_COMMENT: [MessageHandler(Filters.text, choose_comment)],
            CONFIRMATION: [MessageHandler(Filters.text, confirm_order)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()