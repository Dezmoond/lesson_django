from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Расширенная модель пользователя"""
    
    # Дополнительные поля
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name=_('Номер телефона')
    )
    
    birth_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name=_('Дата рождения')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True, 
        null=True,
        verbose_name=_('Аватар')
    )
    
    bio = models.TextField(
        max_length=500, 
        blank=True,
        verbose_name=_('О себе')
    )
    
    # Статус пользователя
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Подтвержденный пользователь')
    )
    
    # Дата создания и обновления
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата регистрации')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Получить полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_short_name(self):
        """Получить короткое имя пользователя"""
        return self.first_name or self.username
