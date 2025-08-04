from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import Event, News, Venue, Ensemble
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, **kwargs):
    """
    Сигнал, срабатывающий после сохранения события
    """
    if created:
        logger.info(f'Создано новое событие: {instance.name}')
        # Очищаем кеш для списка событий
        cache.delete('latest_events')
        cache.delete('upcoming_events')
    else:
        logger.info(f'Обновлено событие: {instance.name}')
        # Очищаем кеш
        cache.delete('latest_events')
        cache.delete('upcoming_events')

@receiver(post_save, sender=News)
def news_post_save(sender, instance, created, **kwargs):
    """
    Сигнал, срабатывающий после сохранения новости
    """
    if created:
        logger.info(f'Создана новость: {instance.title}')
        # Очищаем кеш для новостей
        cache.delete('latest_news')
        cache.delete('news_list')
    else:
        logger.info(f'Обновлена новость: {instance.title}')
        # Очищаем кеш
        cache.delete('latest_news')
        cache.delete('news_list')

@receiver(post_delete, sender=Event)
def event_post_delete(sender, instance, **kwargs):
    """
    Сигнал, срабатывающий после удаления события
    """
    logger.info(f'Удалено событие: {instance.name}')
    # Очищаем кеш
    cache.delete('latest_events')
    cache.delete('upcoming_events')

@receiver(post_delete, sender=News)
def news_post_delete(sender, instance, **kwargs):
    """
    Сигнал, срабатывающий после удаления новости
    """
    logger.info(f'Удалена новость: {instance.title}')
    # Очищаем кеш
    cache.delete('latest_news')
    cache.delete('news_list')

@receiver(pre_save, sender=Event)
def event_pre_save(sender, instance, **kwargs):
    """
    Сигнал, срабатывающий перед сохранением события
    """
    # Автоматически устанавливаем дату создания, если событие новое
    if not instance.pk:  # Новое событие
        logger.info(f'Создается новое событие: {instance.name}')
    
    # Проверяем, изменилась ли дата события
    if instance.pk:
        try:
            old_instance = Event.objects.get(pk=instance.pk)
            if old_instance.date != instance.date:
                logger.info(f'Изменена дата события {instance.name}: {old_instance.date} -> {instance.date}')
        except Event.DoesNotExist:
            pass

@receiver(pre_save, sender=News)
def news_pre_save(sender, instance, **kwargs):
    """
    Сигнал, срабатывающий перед сохранением новости
    """
    # Автоматически генерируем excerpt, если он не заполнен
    if not instance.excerpt and instance.content:
        # Берем первые 150 символов и обрезаем до последнего пробела
        excerpt = instance.content[:150]
        if len(instance.content) > 150:
            last_space = excerpt.rfind(' ')
            if last_space > 100:  # Если пробел найден не слишком близко к началу
                excerpt = excerpt[:last_space]
        instance.excerpt = excerpt + '...'
    
    # Автоматически устанавливаем дату публикации при первой публикации
    if instance.is_published and not instance.pk:
        instance.published_at = timezone.now()

@receiver(post_save, sender=Venue)
def venue_post_save(sender, instance, created, **kwargs):
    """
    Сигнал для площадок
    """
    if created:
        logger.info(f'Создана новая площадка: {instance.name}')
    # Очищаем кеш, связанный с площадками
    cache.delete('venues_list')

@receiver(post_save, sender=Ensemble)
def ensemble_post_save(sender, instance, created, **kwargs):
    """
    Сигнал для коллективов
    """
    if created:
        logger.info(f'Создан новый коллектив: {instance.name}')
    # Очищаем кеш, связанный с коллективами
    cache.delete('ensembles_list') 