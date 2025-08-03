from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import date, time, datetime
from decimal import Decimal
import tempfile
import os
from PIL import Image

from .models import Event, EventCategory, Venue, Festival, Ensemble
from .forms import EventForm, ContactForm

User = get_user_model()


class EventCategoryTest(TestCase):
    """Тесты для категорий событий"""
    
    def test_event_category_choices(self):
        """Тест проверяет, что все категории событий определены корректно"""
        categories = EventCategory.choices
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        
        # Проверяем, что все категории имеют правильный формат (value, label)
        for value, label in categories:
            self.assertIsInstance(value, str)
            self.assertIsInstance(label, str)
            self.assertGreater(len(value), 0)
            self.assertGreater(len(label), 0)
    
    def test_specific_categories_exist(self):
        """Тест проверяет наличие конкретных категорий"""
        category_values = [choice[0] for choice in EventCategory.choices]
        expected_categories = [
            'концерт', 'спектакль', 'опера', 'форум', 
            'концерт старинной музыки', 'органный концерт'
        ]
        
        for expected in expected_categories:
            self.assertIn(expected, category_values)


class VenueModelTest(TestCase):
    """Тесты для модели Venue"""
    
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Концертный зал Родина",
            description="Главный концертный зал города",
            address="ул. Ленина, 1"
        )
    
    def test_venue_creation(self):
        """Тест создания места проведения"""
        self.assertEqual(self.venue.name, "Концертный зал Родина")
        self.assertEqual(self.venue.description, "Главный концертный зал города")
        self.assertEqual(self.venue.address, "ул. Ленина, 1")
    
    def test_venue_str_method(self):
        """Тест строкового представления места проведения"""
        self.assertEqual(str(self.venue), "Концертный зал Родина")
    
    def test_venue_required_fields(self):
        """Тест обязательных полей"""
        # Попытка создать venue без обязательных полей должна вызвать ошибку
        with self.assertRaises(Exception):
            Venue.objects.create(name="")  # Пустое имя должно вызвать ошибку


class FestivalModelTest(TestCase):
    """Тесты для модели Festival"""
    
    def setUp(self):
        self.festival = Festival.objects.create(
            name="Фестиваль классической музыки",
            date=date(2024, 6, 15),
            description="Ежегодный фестиваль классической музыки"
        )
    
    def test_festival_creation(self):
        """Тест создания фестиваля"""
        self.assertEqual(self.festival.name, "Фестиваль классической музыки")
        self.assertEqual(self.festival.date, date(2024, 6, 15))
        self.assertEqual(self.festival.description, "Ежегодный фестиваль классической музыки")
    
    def test_festival_str_method(self):
        """Тест строкового представления фестиваля"""
        self.assertEqual(str(self.festival), "Фестиваль классической музыки")


class EnsembleModelTest(TestCase):
    """Тесты для модели Ensemble"""
    
    def setUp(self):
        self.ensemble = Ensemble.objects.create(
            name="Симфонический оркестр",
            description="Главный симфонический оркестр города"
        )
    
    def test_ensemble_creation(self):
        """Тест создания коллектива"""
        self.assertEqual(self.ensemble.name, "Симфонический оркестр")
        self.assertEqual(self.ensemble.description, "Главный симфонический оркестр города")
    
    def test_ensemble_str_method(self):
        """Тест строкового представления коллектива"""
        self.assertEqual(str(self.ensemble), "Симфонический оркестр")


class EventModelTest(TestCase):
    """Тесты для модели Event"""
    
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем место проведения
        self.venue = Venue.objects.create(
            name="Концертный зал Родина",
            address="ул. Ленина, 1"
        )
        
        # Создаем коллектив
        self.ensemble = Ensemble.objects.create(
            name="Симфонический оркестр"
        )
        
        # Создаем событие
        self.event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Концерт классической музыки",
            date=date(2024, 6, 15),
            time=time(19, 0),
            price="1000 руб",
            description="Великолепный концерт классической музыки",
            venue=self.venue,
            created_by=self.user
        )
        self.event.ensembles.add(self.ensemble)
    
    def test_event_creation(self):
        """Тест создания события"""
        self.assertEqual(self.event.category, EventCategory.CONCERT)
        self.assertEqual(self.event.name, "Концерт классической музыки")
        self.assertEqual(self.event.date, date(2024, 6, 15))
        self.assertEqual(self.event.time, time(19, 0))
        self.assertEqual(self.event.price, "1000 руб")
        self.assertEqual(self.event.venue, self.venue)
        self.assertEqual(self.event.created_by, self.user)
    
    def test_event_str_method(self):
        """Тест строкового представления события"""
        self.assertEqual(str(self.event), "Концерт классической музыки")
    
    def test_event_slug_generation(self):
        """Тест автоматической генерации slug"""
        self.assertIsNotNone(self.event.slug)
        self.assertGreater(len(self.event.slug), 0)
        # Проверяем, что slug содержит название события (без учета даты)
        base_slug = slugify(self.event.name)
        self.assertIn(base_slug, self.event.slug)
        # Проверяем, что slug содержит дату
        date_suffix = self.event.date.strftime('-%Y-%m-%d')
        self.assertIn(date_suffix, self.event.slug)
    
    def test_event_unique_slug_generation(self):
        """Тест генерации уникального slug для событий с одинаковыми названиями"""
        # Создаем второе событие с тем же названием, но другой датой
        event2 = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Концерт классической музыки 2",  # Изменяем название, чтобы избежать уникальности
            date=date(2024, 6, 16),
            time=time(19, 0),
            price="1000 руб",
            description="Второй концерт",
            venue=self.venue,
            created_by=self.user
        )
        
        # Проверяем, что slug'и разные
        self.assertNotEqual(self.event.slug, event2.slug)
        # Проверяем, что slug содержит название события
        base_slug = slugify(event2.name)
        self.assertIn(base_slug, event2.slug)
    
    def test_event_ordering(self):
        """Тест сортировки событий"""
        # Создаем еще одно событие с более ранней датой
        earlier_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Ранний концерт",
            date=date(2024, 6, 10),
            time=time(18, 0),
            price="800 руб",
            description="Ранний концерт",
            venue=self.venue,
            created_by=self.user
        )
        
        events = Event.objects.all()
        self.assertEqual(events[0], earlier_event)
        self.assertEqual(events[1], self.event)
    
    def test_event_ensemble_relationship(self):
        """Тест связи события с коллективами"""
        self.assertIn(self.ensemble, self.event.ensembles.all())
        self.assertEqual(self.event.ensembles.count(), 1)
        
        # Добавляем еще один коллектив
        ensemble2 = Ensemble.objects.create(name="Камерный оркестр")
        self.event.ensembles.add(ensemble2)
        self.assertEqual(self.event.ensembles.count(), 2)
    
    def test_event_venue_relationship(self):
        """Тест связи события с местом проведения"""
        self.assertEqual(self.event.venue, self.venue)
        self.assertIn(self.event, self.venue.event_set.all())
    
    def test_event_created_by_relationship(self):
        """Тест связи события с создателем"""
        self.assertEqual(self.event.created_by, self.user)
        self.assertIn(self.event, self.user.event_set.all())


class EventFormTest(TestCase):
    """Тесты для формы EventForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.venue = Venue.objects.create(
            name="Концертный зал Родина",
            address="ул. Ленина, 1"
        )
        self.ensemble = Ensemble.objects.create(
            name="Симфонический оркестр"
        )
    
    def test_event_form_valid_data(self):
        """Тест валидных данных формы"""
        form_data = {
            'category': EventCategory.CONCERT,
            'name': 'Тестовый концерт',
            'date': '2024-06-15',
            'time': '19:00',
            'price': '1000 руб',
            'description': 'Описание концерта',
            'venue': self.venue.id,
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_event_form_invalid_data(self):
        """Тест невалидных данных формы"""
        # Форма без обязательных полей
        form = EventForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('date', form.errors)
        self.assertIn('time', form.errors)
        self.assertIn('price', form.errors)
    
    def test_event_form_unique_name(self):
        """Тест уникальности названия события"""
        # Создаем первое событие
        Event.objects.create(
            category=EventCategory.CONCERT,
            name='Уникальный концерт',
            date=date(2024, 6, 15),
            time=time(19, 0),
            price='1000 руб',
            description='Описание',
            venue=self.venue,
            created_by=self.user
        )
        
        # Пытаемся создать второе с тем же названием
        form_data = {
            'category': EventCategory.CONCERT,
            'name': 'Уникальный концерт',
            'date': '2024-06-16',
            'time': '19:00',
            'price': '1000 руб',
            'description': 'Описание',
            'venue': self.venue.id,
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class ContactFormTest(TestCase):
    """Тесты для формы ContactForm"""
    
    def test_contact_form_valid_data(self):
        """Тест валидных данных формы контактов"""
        form_data = {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'subject': 'Вопрос о мероприятии',
            'message': 'Здравствуйте! У меня есть вопрос о мероприятии.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_contact_form_invalid_email(self):
        """Тест невалидного email"""
        form_data = {
            'name': 'Иван Иванов',
            'email': 'invalid-email',
            'subject': 'Вопрос',
            'message': 'Сообщение'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_contact_form_empty_fields(self):
        """Тест пустых обязательных полей"""
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)
