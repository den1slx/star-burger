from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator


class OrderQuerySet(models.QuerySet):
    def get_total_price(self):
        price = models.ExpressionWrapper(
            models.Sum(
                models.F('ordered_products__price')
            ), output_field=models.DecimalField()
        )
        orders = self.prefetch_related('ordered_products')
        orders = orders.annotate(price=price)

        return orders


class Order(models.Model):
    ACCEPT = 'AC'
    ASSEMBLE = 'AS'
    DELIVERY = 'DE'
    COMPLETE = 'CO'
    STATUS_CHOICES = [
        (ACCEPT, 'Заказ принят'),
        (ASSEMBLE, 'Заказ собирается'),
        (DELIVERY, 'Заказ у курьера'),
        (COMPLETE, 'Заказ выполнен')
    ]

    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона')
    address = models.TextField('Адрес', db_index=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=ACCEPT,
        db_index=True,
    )
    comment = models.TextField(default='', blank=True)
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderedProduct(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='ordered_products',
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.DO_NOTHING,
        verbose_name='Продукт',
        related_name='ordered_products',
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        null=True,
        validators=[
            MinValueValidator(1), DecimalValidator(
                max_digits=12, decimal_places=2
            )
        ],
    )

    class Meta:
        verbose_name = 'Заказанный продукт'
        verbose_name_plural = 'Заказанные продукты'

    def __str__(self):
        return self.product.name


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"
