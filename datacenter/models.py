from django.db import models


class CakeParam(models.Model):
    title = models.CharField('Название', max_length=20)
    price = models.DecimalField(
        'Цена', 
        default=0.00,
        max_digits=6, decimal_places=2)
    is_available = models.BooleanField('Есть в наличии', default=False)

    class Meta:
        abstract = True


class Shape(CakeParam):
    title = models.CharField('Название формы', max_length=20)


class Topping(CakeParam):
    title = models.CharField('Название топпинга', max_length=20)


class Berries(CakeParam):
    title = models.CharField('Название ягод', max_length=20)


class Decor(CakeParam):
    title = models.CharField('Название декора', max_length=20)


class Cake(models.Model):
    is_original = models.BooleanField('Оригинальный', default=False)
    title = models.CharField('Название торта', max_length=50)           # только для оригинальных?
    image = models.ImageField('Изображение', null=True, blank=True)     # только для оригинальных!
    description = models.TextField('Описание', null=True, blank=True)   # только для оригинальных?

    LEVEL_CHOICES = [
        (1, '1 уровень'),
        (2, '2 уровня'),
        (3, '3 уровня')
    ]
    levels = models.IntegerField(
        'Количество уровней', 
        choices=LEVEL_CHOICES,
        default=1)
    shape = models.ForeignKey(
        Shape,
        verbose_name='Форма', 
        on_delete=models.CASCADE)  # какой on_delete лучше?
    topping = models.ForeignKey(
        Topping,
        verbose_name='Топпинг', 
        on_delete=models.CASCADE)  # какой on_delete лучше?
    berries = models.ForeignKey(
        Berries,
        verbose_name='Ягоды',
        null=True, blank=True, 
        on_delete=models.SET_NULL)  # какой on_delete лучше?
    topping = models.ForeignKey(
        Topping,
        verbose_name='Топпинг',
        null=True, blank=True, 
        on_delete=models.SET_NULL)  # какой on_delete лучше?
    text = models.CharField(
        'Надпись на торте', 
        max_length=100, 
        null=True, blank=True)


    def __str__(self):
        return self.title   # если нет названия, f(){описание из компонентов}







