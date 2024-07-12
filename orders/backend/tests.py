from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker

from orders.backend.models import (
    User,
    Contact,
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
)


@pytest.fixture
def client():
    return APIClient()


USER = {
    "email": "testing1@test.com",
    "password": "test_123",
    "username": "test_user",
    "full_name": "test",
    "company": "test",
    "position": "manager",
}


@pytest.fixture
def buyer(django_user_model):
    buyer = django_user_model.objects.create_user(
        email=USER["email"],
        password=USER["password"],
        username=USER["username"],
        type="buyer",
    )
    return buyer


@pytest.fixture
def seller(django_user_model):
    seller = django_user_model.objects.create_user(
        email=USER["email"],
        password=USER["password"],
        username=USER["username"],
        type="shop",
    )
    return seller



@pytest.mark.django_db
def test_register(client):
    data = {
        "email": USER["email"],
        "password": USER["password"],
        "username": USER["username"],
        "type": "buyer",
        "full_name": USER["full_name"],
        "company": USER["company"],
        "position": USER["position"],
    }
    url = reverse("register")

    request = client.post(path=url, data=data)

    assert request.status_code == 200
    user = User.objects.get(email=data["email"])
    assert user


@pytest.mark.django_db
def test_login(client, user_factory):
    test_user = user_factory(_quantity=1)
    url = reverse("login")

    request = client.post(
        path=url,
        data={"username": test_user[0].username, "password": test_user[0].password},
    )

    assert request.status_code == 200


@pytest.mark.django_db
def test_get_contact(client, buyer):
    test_user = buyer
    test_contact = {
        "city": "Omsk",
        "street": "Elm",
        "house": "15",
        "structure": None,
        "building": None,
        "apartment": None,
        "phone": "0 000 000 00 00",
    }
    url = reverse("get_contact_info")

    client.force_authenticate(test_user)
    request = client.post(path=url, data=test_contact)
    client.force_authenticate(user=None)

    assert request.status_code == 200
    contact = Contact.objects.get(phone=test_contact["phone"])
    assert contact


@pytest.mark.django_db
def test_update(client, seller):
    test_user = seller

    client.force_authenticate(test_user)
    request = client.post("/update/shop1.yaml/")
    client.force_authenticate(user=None)

    assert request.status_code == 200
    assert Shop.objects.count() == 1
    assert Category.objects.count() == 3
    assert Product.objects.count() == 4
    assert ProductInfo.objects.count() == 4
    assert Parameter.objects.count() == 4
    assert ProductParameter.objects.count() == 16
