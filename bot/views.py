from django.shortcuts import render, get_object_or_404

# Create your views here.
from bot.models import Client, Order


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
