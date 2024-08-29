from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class MyAccountManager(BaseUserManager):
    def create_user(self, name, email, password=None):
        if not email:
            raise ValueError(_("User must have an email address"))
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None):
        user = self.create_user(
            name=name,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user
