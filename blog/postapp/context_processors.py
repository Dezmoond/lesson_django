from django.core.cache import cache
from .models import Event, News, Venue, Ensemble, EventCategory, NewsCategory
from datetime import date, datetime
from django.db.models import Q, Count

def site_stats(request):
    """
    Контекстный процессор для добавления статистики сайта
    """
    # Получаем статистику из кеша или вычисляем заново
    stats = cache.get('site_stats')
    
    if not stats:
        today = date.today()
        now = datetime.now().time()
        
        # Подсчитываем статистику
        stats = {
            'total_events': Event.objects.count(),
            'upcoming_events': Event.objects.filter(
                Q(date__gt=today) | (Q(date=today) & Q(time__gte=now))
            ).count(),
            'today_events': Event.objects.filter(date=today).count(),
            'total_news': News.objects.filter(is_published=True).count(),
            'total_venues': Venue.objects.count(),
            'total_ensembles': Ensemble.objects.count(),
            'event_categories': len(EventCategory.choices),
            'news_categories': len(NewsCategory.choices),
        }
        
        # Кешируем на 10 минут
        cache.set('site_stats', stats, 600)
    
    return {'site_stats': stats}

def navigation_data(request):
    """
    Контекстный процессор для данных навигации
    """
    # Получаем данные из кеша
    nav_data = cache.get('navigation_data')
    
    if not nav_data:
        # Получаем категории событий
        event_categories = EventCategory.choices
        
        # Получаем категории новостей
        news_categories = NewsCategory.choices
        
        # Получаем популярные площадки (те, где больше всего событий)
        popular_venues = Venue.objects.annotate(
            event_count=Count('event')
        ).order_by('-event_count')[:5]
        
        # Получаем популярные коллективы
        popular_ensembles = Ensemble.objects.annotate(
            event_count=Count('event')
        ).order_by('-event_count')[:5]
        
        nav_data = {
            'event_categories': event_categories,
            'news_categories': news_categories,
            'popular_venues': popular_venues,
            'popular_ensembles': popular_ensembles,
        }
        
        # Кешируем на 30 минут
        cache.set('navigation_data', nav_data, 1800)
    
    return {'nav_data': nav_data}

def user_context(request):
    """
    Контекстный процессор для данных пользователя
    """
    context = {}
    
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        # Количество событий, созданных пользователем
        user_events_count = Event.objects.filter(created_by=request.user).count()
        
        # Количество новостей, созданных пользователем
        user_news_count = News.objects.filter(author=request.user).count()
        
        # Последние события пользователя
        user_recent_events = Event.objects.filter(
            created_by=request.user
        ).order_by('-date', '-time')[:3]
        
        context.update({
            'user_events_count': user_events_count,
            'user_news_count': user_news_count,
            'user_recent_events': user_recent_events,
        })
    
    return context

def current_time(request):
    """
    Контекстный процессор для текущего времени
    """
    from django.utils import timezone
    
    return {
        'current_time': timezone.now(),
        'current_date': date.today(),
    } 