from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver, Signal

from .models import ConfirmEmailToken, User, Shop

new_user_registered = Signal()

new_order = Signal()

price_update = Signal()


@shared_task
@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email],
    )
    msg.send()


@shared_task
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    # send an e-mail to the user

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {reset_password_token.user}",
        # message:
        reset_password_token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email],
    )
    msg.send()


@shared_task
@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        f"Заказ сформирован",
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email],
    )
    msg.send()


@shared_task
@receiver(price_update)
def price_update_signal(user_id, **kwargs):
    # Отправка письма об изменении цен
    # send an e-mail to the users
    shop = Shop.objects.get(user_id=user_id).name
    for email in User.objects.exclude(type="shop").values_list("email", flat=True):
        msg = EmailMultiAlternatives(
            # title:
            f"Магазин {shop} обновил цены",
            # message:
            f"Магазин {shop} обновлен цены",
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [email],
        )
        msg.send()