from django.db import models
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Max
from BakeCake.settings import URGENT_ORDER_ALLOWANCE, BOT_LINK
from bot.bitlink import is_bitlink, shorten_link, count_clicks


class CakeParam(models.Model):
    title = models.CharField('Название', max_length=20) 
    image = models.ImageField('Изображение', null=True, blank=True)
    price = models.DecimalField(
        'Цена',
        default=0.00,
        max_digits=6, decimal_places=2)
    is_available = models.BooleanField('Есть в наличии', default=False)

    def __str__(self):
        return str(self.title)

    class Meta:
        abstract = True


class Level(CakeParam):
    LEVEL_CHOICES = [
        (1, '1 уровень'),
        (2, '2 уровня'),
        (3, '3 уровня')
    ]
    title = models.IntegerField(
        'Количество уровней',
        choices=LEVEL_CHOICES,
        unique=True,
        default=1)

    class Meta:
        verbose_name_plural = 'Уровни'


class Shape(CakeParam):
    title = models.CharField('Название формы', max_length=20)

    class Meta:
        verbose_name_plural = 'Форма'


class Topping(CakeParam):
    title = models.CharField('Название топпинга', max_length=20)

    class Meta:
        verbose_name_plural = 'Топпинг'


class Berries(CakeParam):
    title = models.CharField('Название ягод', max_length=20)

    class Meta:
        verbose_name_plural = 'Ягоды'


class Decor(CakeParam):
    title = models.CharField('Название декора', max_length=20)

    class Meta:
        verbose_name_plural = 'Декор'



class Cake(models.Model):
    is_original = models.BooleanField('Оригинальный', default=False)
    title = models.CharField(
        'Название торта',
        null=True, blank=True,
        max_length=50,
        default=f'Торт')
    image = models.ImageField('Изображение', null=True, blank=True)     
    description = models.TextField('Описание', null=True, blank=True)   

    level = models.ForeignKey(
        Level,
        verbose_name='Уровни',
        null=True,
        on_delete=models.PROTECT)  
    shape = models.ForeignKey(
        Shape,
        verbose_name='Форма',
        null=True,
        on_delete=models.PROTECT)  
    topping = models.ForeignKey(
        Topping,
        verbose_name='Топпинг',
        null=True,
        on_delete=models.PROTECT)  
    berries = models.ForeignKey(
        Berries,
        verbose_name='Ягоды',
        null=True, blank=True,
        on_delete=models.SET_NULL)  
    decor = models.ForeignKey(
        Decor,
        verbose_name='Декор',
        null=True, blank=True,
        on_delete=models.SET_NULL)  
    text = models.CharField(
        'Надпись на торте',
        max_length=100,
        null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Торты'

    def __str__(self):
        if self.title:
            return f'Торт {self.title}'
        return f'Торт №{self.id}'

    def get_params(self):
        return [self.level, self.shape,
                self.topping, self.berries, self.topping]

    def get_price(self):
        return sum([param.price if param else 0 for param in self.get_params()]) + \
                   (0 if self.text == 'Без надписи.' or self.text is None else 500)

    def get_composition(self, with_price=True):
        message = f'{self.__str__()}\n' \
                  'Состав:\n'\
                  f'Количество уровней: {self.level}\n' \
                  f'Форма коржей: {self.shape.title}\n' \
                  f'Топпинг: {self.topping.title}' 
        if self.berries:
            message += f'\nЯгоды: {self.berries.title}'
        if self.decor:
            message += f'\nДекор: {self.decor.title}'
        if self.text:
            message += f'\nНадпись на торте: {self.text}'
        if with_price:
            message += f'\nСтоимость торта {self.get_price()} руб.'
        return message

    def verify_cake(self):
        for param in self.get_params():
            if not param.is_available:
                return False
        return True


class Client(models.Model):
    id_telegram = models.CharField('Телеграм id', max_length=20)
    name = models.CharField('Имя', max_length=30, default='Дорогой Гость')
    telegram_url = models.URLField('Ссылка на телеграм', max_length=80, null=True, blank=True,)
    consent_to_pdProc = models.BooleanField(
        'Согласие на обработку ПД',
        default=False)
    nickname = models.CharField('Ник в телеграме', max_length=30, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_url = self.get_tg_link()

    def get_tg_link(self):
        return f'https://t.me/{self.nickname}'

    class Meta:
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.name}, {self.id_telegram}'


class Complaint(models.Model):
    text = models.TextField('Текст жалобы')

    class Meta:
        verbose_name_plural = 'Жалоба'


class PromoCode(models.Model):
    code = models.CharField('Код', unique=True, max_length=20)
    discount = models.DecimalField(
        'Скидка',
        max_digits=3, decimal_places=2,
        validators=[MinValueValidator(0),
                    MaxValueValidator(1)])

    def __str__(self):
        return f'Код "{self.code}" на скидку {self.discount * 100}%'


class Order(models.Model):
    cake = models.ForeignKey(
        Cake,
        verbose_name='Торт',
        on_delete=models.CASCADE)
    client = models.ForeignKey(
        Client,
        verbose_name='Клиент',
        related_name='orders',
        on_delete=models.CASCADE)
    order_dt = models.DateTimeField(
        'Дата и время заказа',
        auto_now_add=True)
    delivery_dt = models.DateTimeField(
        'Дата и время доставки',
        null=True, blank=True)
    address = models.CharField('Адрес', max_length=80, null=True, blank=True)
    promo_code = models.ForeignKey(
        PromoCode,
        verbose_name='Промокод',
        null=True, blank=True,
        on_delete=models.SET_NULL)
    comment = models.TextField('Комментарий', null=True, blank=True)
    complaint = models.OneToOneField(
        Complaint,
        on_delete=models.SET_NULL,
        null=True, blank=True)
    # status

    class Meta:
        verbose_name_plural = 'Заказы'

    def is_urgent_order(self):
        delta = self.delivery_dt - self.order_dt
        return delta < timedelta(days=1)

    def get_price(self):
        cake_price = int(self.cake.get_price())
        order_price = cake_price * \
                      (1 - (self.promo_code.discount if self.promo_code else 0)) * \
                      (1 + (URGENT_ORDER_ALLOWANCE if self.is_urgent_order() else 0))
        return round(float(order_price), 2)

    def get_description(self, with_cake=True, with_cake_price=False):
        message = f'{self.__str__()}:\n'
        if with_cake:
            message += self.cake.get_composition(with_cake_price)
        else:
            message += self.cake.__str__()

        if self.delivery_dt:
            message += f'\nДоставить {self.delivery_dt.strftime("%d.%m.%y %H:%M")}\n'
        if self.address:
            if self.delivery_dt:
                message += f'По адресу {self.address}\n'
            else:
                message += f'Доставить по адресу {self.address}\n'
        if self.comment:
            message += f'Комментарий к заказу: {self.comment}\n\n'

        if self.promo_code:
            message += f'С учетом скидки {self.promo_code.code} ' \
                       f'в {self.promo_code.discount * 100}%\n'
        if self.is_urgent_order():
            message += 'С учетом надбавки за срочный заказ ' \
                       f'в {URGENT_ORDER_ALLOWANCE * 100}%\n'

        message += f'Стоимость заказа {self.get_price()} руб.'
        return message

    def __str__(self):
        return f'Заказ №{self.id} от {self.order_dt.strftime("%d.%m.%y")}'


def create_new_bitlink():
    max_id = Link.objects.aggregate(Max('id'))['id__max']
    if not max_id:
        max_id = 0
    next_bitlink_id = max_id + 1
    while True:
        if not is_bitlink(BOT_LINK, next_bitlink_id):
            return shorten_link(BOT_LINK, next_bitlink_id)
        next_bitlink_id += 1


class Link(models.Model):
    shorten_link = models.CharField(
        'Сокращенная ссылка',
        max_length=20,
        null=True, blank=True,
        default=create_new_bitlink)
    place_of_use = models.CharField(
        'Место использования ссылки',
        max_length=50,
        null=True, blank=True)

    @property
    def clicks(self):
        return count_clicks(self.shorten_link)


