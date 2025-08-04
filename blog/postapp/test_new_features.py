from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.template import Template, Context
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from decimal import Decimal
import tempfile
import os
from PIL import Image

from .models import Event, EventCategory, Venue, Festival, Ensemble, News, NewsCategory
from .templatetags.postapp_extras import format_price, format_date_range, truncate_words_smart, get_category_color, get_news_category_color
from .context_processors import site_stats, navigation_data, user_context, current_time

User = get_user_model()

class ModelManagersTest(TestCase):
    """Тесты для менеджеров моделей"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.venue = Venue.objects.create(
            name='Тестовый зал',
            address='ул. Тестовая, 1'
        )
        
        self.ensemble = Ensemble.objects.create(
            name='Тестовый ансамбль',
            description='Описание ансамбля'
        )
        
        # Создаем события на разные даты
        self.past_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Прошедший концерт',
            date=date.today() - timedelta(days=1),
            time=time(19, 0),
            price='1000 руб',
            description='Прошедший концерт',
            venue=self.venue,
            created_by=self.user
        )
        
        self.today_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Сегодняшний концерт',
            date=date.today(),
            time=time(20, 0),
            price='1500 руб',
            description='Концерт сегодня',
            venue=self.venue,
            created_by=self.user
        )
        
        self.future_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Будущий концерт',
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            price='2000 руб',
            description='Будущий концерт',
            venue=self.venue,
            created_by=self.user
        )
        
        # Создаем новости
        self.news1 = News.objects.create(
            title='Тестовая новость 1',
            content='Содержание первой новости',
            excerpt='Краткое описание первой новости',
            category=NewsCategory.GENERAL,
            author=self.user,
            is_published=True
        )
        
        self.news2 = News.objects.create(
            title='Тестовая новость 2',
            content='Содержание второй новости',
            excerpt='Краткое описание второй новости',
            category=NewsCategory.MUSIC,
            author=self.user,
            is_published=True
        )
        
        self.unpublished_news = News.objects.create(
            title='Неопубликованная новость',
            content='Содержание неопубликованной новости',
            category=NewsCategory.CULTURE,
            author=self.user,
            is_published=False
        )

    def test_event_manager_upcoming(self):
        """Тест менеджера upcoming для событий"""
        upcoming_events = Event.objects.upcoming()
        self.assertIn(self.future_event, upcoming_events)
        self.assertNotIn(self.past_event, upcoming_events)

    def test_event_manager_past(self):
        """Тест менеджера past для событий"""
        past_events = Event.objects.past()
        self.assertIn(self.past_event, past_events)
        self.assertNotIn(self.future_event, past_events)

    def test_event_manager_today(self):
        """Тест менеджера today для событий"""
        today_events = Event.objects.today()
        self.assertIn(self.today_event, today_events)
        self.assertEqual(today_events.count(), 1)

    def test_event_manager_by_category(self):
        """Тест менеджера by_category для событий"""
        concert_events = Event.objects.by_category(EventCategory.CONCERT)
        self.assertEqual(concert_events.count(), 3)

    def test_event_manager_by_venue(self):
        """Тест менеджера by_venue для событий"""
        venue_events = Event.objects.by_venue(self.venue.id)
        self.assertEqual(venue_events.count(), 3)

    def test_event_manager_search(self):
        """Тест менеджера search для событий"""
        search_results = Event.objects.search('концерт')
        self.assertEqual(search_results.count(), 3)

    def test_news_manager_published(self):
        """Тест менеджера published для новостей"""
        published_news = News.objects.published()
        self.assertIn(self.news1, published_news)
        self.assertIn(self.news2, published_news)
        self.assertNotIn(self.unpublished_news, published_news)

    def test_news_manager_by_category(self):
        """Тест менеджера by_category для новостей"""
        general_news = News.objects.by_category(NewsCategory.GENERAL)
        self.assertIn(self.news1, general_news)
        self.assertNotIn(self.news2, general_news)

    def test_news_manager_recent(self):
        """Тест менеджера recent для новостей"""
        recent_news = News.objects.recent(limit=1)
        self.assertEqual(recent_news.count(), 1)

    def test_news_manager_search(self):
        """Тест менеджера search для новостей"""
        search_results = News.objects.search('новость')
        self.assertEqual(search_results.count(), 2)

    def test_news_manager_by_author(self):
        """Тест менеджера by_author для новостей"""
        author_news = News.objects.by_author(self.user)
        self.assertEqual(author_news.count(), 2)  # Только опубликованные

class TemplateFiltersTest(TestCase):
    """Тесты для шаблонных фильтров"""
    
    def test_format_price(self):
        """Тест фильтра format_price"""
        self.assertEqual(format_price('1000 руб'), '1 000 ₽')
        self.assertEqual(format_price('1500 руб.'), '1 500 ₽')
        self.assertEqual(format_price(''), 'Цена не указана')
        self.assertEqual(format_price(None), 'Цена не указана')

    def test_format_date_range(self):
        """Тест фильтра format_date_range"""
        start_date = date(2024, 1, 15)
        end_date = date(2024, 1, 20)
        
        self.assertEqual(format_date_range(start_date, end_date), '15.01.2024 - 20.01.2024')
        self.assertEqual(format_date_range(start_date, start_date), '15.01.2024')
        self.assertEqual(format_date_range(None, end_date), '20.01.2024')

    def test_truncate_words_smart(self):
        """Тест фильтра truncate_words_smart"""
        text = "Это первое предложение. Это второе предложение. Это третье предложение."
        
        result = truncate_words_smart(text, 5)
        self.assertIn('первое предложение', result)
        self.assertNotIn('третье', result)
        self.assertTrue(result.endswith('...'))

    def test_get_category_color(self):
        """Тест фильтра get_category_color"""
        self.assertEqual(get_category_color('концерт'), 'primary')
        self.assertEqual(get_category_color('спектакль'), 'success')
        self.assertEqual(get_category_color('неизвестная'), 'secondary')

    def test_get_news_category_color(self):
        """Тест фильтра get_news_category_color"""
        self.assertEqual(get_news_category_color('общие'), 'secondary')
        self.assertEqual(get_news_category_color('музыка'), 'success')
        self.assertEqual(get_news_category_color('неизвестная'), 'secondary')

class ModelPropertiesTest(TestCase):
    """Тесты для свойств моделей"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.venue = Venue.objects.create(
            name='Тестовый зал',
            address='ул. Тестовая, 1'
        )
        
        self.past_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Прошедший концерт',
            date=date.today() - timedelta(days=1),
            time=time(19, 0),
            price='1000 руб',
            description='Прошедший концерт',
            venue=self.venue,
            created_by=self.user
        )
        
        self.today_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Сегодняшний концерт',
            date=date.today(),
            time=time(20, 0),
            price='1500 руб',
            description='Концерт сегодня',
            venue=self.venue,
            created_by=self.user
        )
        
        self.future_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Будущий концерт',
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            price='2000 руб',
            description='Будущий концерт',
            venue=self.venue,
            created_by=self.user
        )
        
        self.news = News.objects.create(
            title='Тестовая новость',
            content='Это очень длинное содержание новости с множеством слов для тестирования времени чтения. ' * 10,
            excerpt='Краткое описание',
            category=NewsCategory.GENERAL,
            author=self.user,
            is_published=True
        )

    def test_event_is_past(self):
        """Тест свойства is_past для событий"""
        self.assertTrue(self.past_event.is_past)
        self.assertFalse(self.future_event.is_past)

    def test_event_is_today(self):
        """Тест свойства is_today для событий"""
        self.assertTrue(self.today_event.is_today)
        self.assertFalse(self.past_event.is_today)

    def test_event_is_upcoming(self):
        """Тест свойства is_upcoming для событий"""
        self.assertTrue(self.future_event.is_upcoming)
        self.assertFalse(self.past_event.is_upcoming)

    def test_news_reading_time(self):
        """Тест свойства reading_time для новостей"""
        self.assertGreater(self.news.reading_time, 0)

class ContextProcessorsTest(TestCase):
    """Тесты для контекстных процессоров"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем тестовые данные
        self.venue = Venue.objects.create(name='Тестовый зал', address='ул. Тестовая, 1')
        self.ensemble = Ensemble.objects.create(name='Тестовый ансамбль')
        
        self.event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Тестовый концерт',
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            price='1000 руб',
            description='Описание концерта',
            venue=self.venue,
            created_by=self.user
        )
        
        self.news = News.objects.create(
            title='Тестовая новость',
            content='Содержание новости',
            category=NewsCategory.GENERAL,
            author=self.user,
            is_published=True
        )

    def test_site_stats_processor(self):
        """Тест контекстного процессора site_stats"""
        request = self.factory.get('/')
        context = site_stats(request)
        
        self.assertIn('site_stats', context)
        stats = context['site_stats']
        self.assertIn('total_events', stats)
        self.assertIn('total_news', stats)
        self.assertIn('total_venues', stats)
        self.assertIn('total_ensembles', stats)

    def test_navigation_data_processor(self):
        """Тест контекстного процессора navigation_data"""
        request = self.factory.get('/')
        context = navigation_data(request)
        
        self.assertIn('nav_data', context)
        nav_data = context['nav_data']
        self.assertIn('event_categories', nav_data)
        self.assertIn('news_categories', nav_data)

    def test_user_context_processor_authenticated(self):
        """Тест контекстного процессора user_context для авторизованного пользователя"""
        request = self.factory.get('/')
        request.user = self.user
        context = user_context(request)
        
        self.assertIn('user_events_count', context)
        self.assertIn('user_news_count', context)
        self.assertIn('user_recent_events', context)

    def test_user_context_processor_anonymous(self):
        """Тест контекстного процессора user_context для анонимного пользователя"""
        request = self.factory.get('/')
        request.user = None
        context = user_context(request)
        
        self.assertEqual(context, {})

    def test_current_time_processor(self):
        """Тест контекстного процессора current_time"""
        request = self.factory.get('/')
        context = current_time(request)
        
        self.assertIn('current_time', context)
        self.assertIn('current_date', context)

class NewsListViewTest(TestCase):
    """Тесты для NewsListView"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем несколько новостей
        for i in range(15):
            News.objects.create(
                title=f'Новость {i+1}',
                content=f'Содержание новости {i+1}',
                category=NewsCategory.GENERAL if i % 2 == 0 else NewsCategory.MUSIC,
                author=self.user,
                is_published=True
            )

    def test_news_list_view(self):
        """Тест отображения списка новостей"""
        response = self.client.get(reverse('blog:news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'postapp/news_list.html')
        self.assertContains(response, 'Новость 1')

    def test_news_list_pagination(self):
        """Тест пагинации в списке новостей"""
        response = self.client.get(reverse('blog:news_list'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что есть пагинация
        self.assertContains(response, 'Страница')
        self.assertContains(response, 'Следующая')

    def test_news_list_filtering(self):
        """Тест фильтрации новостей по категории"""
        # Используем код категории 'музыка' вместо названия
        response = self.client.get(reverse('blog:news_list'), {'category': 'музыка'})
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что отображаются только новости категории "музыка"
        # Новости с четными номерами (2, 4, 6, ...) - музыкальные
        self.assertContains(response, 'Новость 2')  # Музыкальная новость
        self.assertContains(response, 'Новость 4')  # Музыкальная новость
        
        # Проверяем, что общие новости не отображаются на этой странице
        # Но поскольку у нас пагинация, некоторые общие новости могут быть на странице
        # Проверим, что в контексте есть правильная фильтрация
        self.assertEqual(response.context['selected_category'], 'музыка')
        
        # Проверим, что все отображаемые новости имеют категорию "музыка"
        for news in response.context['news_list']:
            self.assertEqual(news.category, 'музыка')

class SignalsTest(TestCase):
    """Тесты для сигналов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.venue = Venue.objects.create(
            name='Тестовый зал',
            address='ул. Тестовая, 1'
        )

    def test_event_signal_creates_slug(self):
        """Тест автоматического создания slug при создании события"""
        event = Event.objects.create(
            category=EventCategory.CONCERT,
            name='Тестовый концерт',
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            price='1000 руб',
            description='Описание концерта',
            venue=self.venue,
            created_by=self.user
        )
        
        self.assertIsNotNone(event.slug)
        self.assertGreater(len(event.slug), 0)

    def test_news_signal_creates_excerpt(self):
        """Тест автоматического создания excerpt при создании новости"""
        news = News.objects.create(
            title='Тестовая новость',
            content='Это очень длинное содержание новости, которое должно быть автоматически обрезано до краткого описания при сохранении.',
            category=NewsCategory.GENERAL,
            author=self.user,
            is_published=True
        )
        
        self.assertIsNotNone(news.excerpt)
        self.assertGreater(len(news.excerpt), 0)
        self.assertTrue(news.excerpt.endswith('...'))

    def test_news_signal_sets_published_at(self):
        """Тест автоматической установки даты публикации"""
        news = News.objects.create(
            title='Тестовая новость',
            content='Содержание новости',
            category=NewsCategory.GENERAL,
            author=self.user,
            is_published=True
        )
        
        self.assertIsNotNone(news.published_at) 