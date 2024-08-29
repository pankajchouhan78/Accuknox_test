from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from app.manager import MyAccountManager


class Person(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    friends = models.ManyToManyField(
        "self", blank=True, related_name="friends_set", symmetrical=True
    )
    sent_requests = models.ManyToManyField(
        "self", blank=True, related_name="sent_requests_set", symmetrical=False
    )
    received_requests = models.ManyToManyField(
        "self", blank=True, related_name="received_requests_set", symmetrical=False
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = MyAccountManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
