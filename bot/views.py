from django.shortcuts import render, get_object_or_404
from bot.models import Client, Order
from django.http import JsonResponse


def get_user_orders(id_telegram: int or str):
    user = get_object_or_404(Client, id_telegram=id_telegram)
    orders = []
    for order in user.orders.all()[:5]:
        orders.append(
            {
                'description': f'Заказ №{order.id} от {order.creation.strftime("%d.%m.%y")}',
                'id': order.id,
            }
        )
    return orders


def get_serialized_order(order_id):
    order = get_object_or_404(Order, id=order_id)
    return {
        'description': f'Заказ №{order.id} от {order.creation.strftime("%d.%m.%y")}',
        'id': order.id,
        'cake': order.cake,
        'creation_date': order.creation,
        'delivery_date': order.delivery_date,
        'comment': order.comment,
        'price': order.price()
    }


def order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    serialized_order = f'Заказ №{order.id} от {order.order_dt.strftime("%d.%m.%y")}\n\n'
    serialized_order += f'Торт: {order.cake.title}\n'
    serialized_order += f'Описание: {order.cake.description}\n\n'
    serialized_order += f'Дата и время заказа: {order.order_dt}\n'
    serialized_order += f'Дата и время доставки: {order.delivery_dt}\n'
    serialized_order += f'Комментарий: {order.comment}\n'
    serialized_order += f'Цена: {order.get_price()}'

    return serialized_order