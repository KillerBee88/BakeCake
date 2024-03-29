from django.shortcuts import render, get_object_or_404
from bot.models import Client, Order
from django.http import JsonResponse


def get_user_orders(id_telegram: int or str):
    user = get_object_or_404(Client, id_telegram=id_telegram)
    orders = []
    for order in user.orders.all()[:5]:
        orders.append(
            {
                'description': f'Заказ №{order.id} от {order.order_dt.strftime("%d.%m.%y")}',
                'id': order.id,
            }
        )
    return orders


def get_serialized_order(order_id):
    order = get_object_or_404(Order, id=order_id)
    return {
        'description': f'Заказ №{order.id} от {order.order_dt.strftime("%d.%m.%y")}',
        'id': order.id,
        'cake': order.cake,
        'creation_date': order.order_dt,
        'delivery_date': order.delivery_dt,
        'comment': order.comment,
        'price': order.get_price()
    }


def order_view(order_id):
    order = get_object_or_404(Order, id=order_id)

    serialized_order = {
        'description': f'Заказ №{order.id} от {order.order_dt.strftime("%d.%m.%y")}',
        'id': order.id,
        'cake': {
            'title': order.cake.title,
            'image': order.cake.image.url if order.cake.image else None,
            'description': order.cake.description,
        },
        'creation_date': order.order_dt,
        'delivery_date': order.delivery_dt,
        'comment': order.comment,
        'price': order.get_price()
    }

    return serialized_order


def order_view_str(order_id):
    order = get_object_or_404(Order, id=order_id)

    beautiful_order = f"""
Заказ №{order.id} от {order.order_dt.strftime("%d.%m.%y")}:
Дата доставки: {order.delivery_dt.strftime("%d.%m.%y %H:%M")}.
Адрес доставки: {order.address}.
Комментарий к заказу: {order.comment}.  
Стоимость заказа: {order.get_price()} руб.

Торт в заказе: {order.cake.get_composition()}"""

    return beautiful_order
