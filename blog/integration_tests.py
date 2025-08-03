from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time
from django.core import mail

from postapp.models import Event, EventCategory, Venue, Ensemble

User = get_user_model()


class IntegrationTestCase(TestCase):
    """Базовый класс для интеграционных тестов"""
    
    def setUp(self):
        self.client = Client()
        
        # Создаем пользователей
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Создаем тестовые данные
        self.venue = Venue.objects.create(
            name="Концертный зал Родина",
            address="ул. Ленина, 1"
        )
        
        self.ensemble = Ensemble.objects.create(
            name="Симфонический оркестр"
        )
        
        # Создаем события
        self.future_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Будущий концерт",
            date=date.today() + timezone.timedelta(days=7),
            time=time(19, 0),
            price="1000 руб",
            description="Концерт в будущем",
            venue=self.venue,
            created_by=self.user
        )
        self.future_event.ensembles.add(self.ensemble)
        
        self.past_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Прошедший концерт",
            date=date.today() - timezone.timedelta(days=7),
            time=time(19, 0),
            price="800 руб",
            description="Концерт в прошлом",
            venue=self.venue,
            created_by=self.user
        )
        self.past_event.ensembles.add(self.ensemble)


class UserEventIntegrationTest(IntegrationTestCase):
    """Тесты интеграции пользователей и событий"""
    
    def test_user_can_create_event(self):
        """Тест создания события пользователем"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'category': EventCategory.CONCERT,
            'name': 'Новый концерт от пользователя',
            'date': '2024-07-15',
            'time': '19:00',
            'price': '1200 руб',
            'description': 'Описание нового концерта',
            'venue': self.venue.id,
        }
        
        response = self.client.post(reverse('blog:create'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что событие создано и связано с пользователем
        new_event = Event.objects.get(name='Новый концерт от пользователя')
        self.assertEqual(new_event.created_by, self.user)
        self.assertEqual(new_event.category, EventCategory.CONCERT)
    
    def test_user_sees_only_own_events_in_archive(self):
        """Тест, что пользователь видит только свои события в архиве"""
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Создаем событие от другого пользователя
        other_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Событие другого пользователя",
            date=date.today() - timezone.timedelta(days=3),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=other_user
        )
        
        # Авторизуемся как первый пользователь
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:archive'))
        events = response.context['events']
        
        # Проверяем, что видим только свои события
        self.assertIn(self.past_event, events)
        self.assertNotIn(other_event, events)
    
    def test_event_creation_requires_authentication(self):
        """Тест, что создание события требует авторизации"""
        form_data = {
            'category': EventCategory.CONCERT,
            'name': 'Попытка создать без авторизации',
            'date': '2024-07-15',
            'time': '19:00',
            'price': '1200 руб',
            'description': 'Описание',
            'venue': self.venue.id,
        }
        
        response = self.client.post(reverse('blog:create'), form_data)
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
        
        # Проверяем, что событие не создано
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(name='Попытка создать без авторизации')
    
    def test_user_profile_shows_created_events(self):
        """Тест отображения созданных событий в профиле пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        
        # Проверяем, что в контексте есть пользователь
        self.assertEqual(response.context['user'], self.user)
        
        # Проверяем, что пользователь связан с событиями
        user_events = self.user.event_set.all()
        self.assertIn(self.future_event, user_events)
        self.assertIn(self.past_event, user_events)


class AuthenticationFlowTest(IntegrationTestCase):
    """Тесты полного цикла аутентификации"""
    
    def test_complete_user_journey(self):
        """Тест полного пути пользователя"""
        # 1. Регистрация
        signup_data = {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'password1': 'journeypass123',
            'password2': 'journeypass123',
            'first_name': 'Путешественник',
            'last_name': 'Тестовый'
        }
        
        response = self.client.post(reverse('users:signup'), signup_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Вход в систему
        login_data = {
            'username': 'journeyuser',
            'password': 'journeypass123'
        }
        
        response = self.client.post(reverse('users:login'), login_data)
        self.assertEqual(response.status_code, 302)
        
        # 3. Создание события
        event_data = {
            'category': EventCategory.CONCERT,
            'name': 'Концерт путешественника',
            'date': '2024-08-15',
            'time': '20:00',
            'price': '1500 руб',
            'description': 'Концерт нового пользователя',
            'venue': self.venue.id,
        }
        
        response = self.client.post(reverse('blog:create'), event_data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Проверка создания события
        new_event = Event.objects.get(name='Концерт путешественника')
        new_user = User.objects.get(username='journeyuser')
        self.assertEqual(new_event.created_by, new_user)
        
        # 5. Просмотр архива
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)
        
        # 6. Редактирование профиля
        profile_data = {
            'first_name': 'Обновленный',
            'last_name': 'Путешественник',
            'email': 'updated@example.com',
            'phone': '+7-999-111-22-33',
            'bio': 'Обновленный профиль'
        }
        
        response = self.client.post(reverse('users:profile_edit'), profile_data)
        self.assertEqual(response.status_code, 302)
        
        # 7. Проверка обновления профиля
        updated_user = User.objects.get(username='journeyuser')
        self.assertEqual(updated_user.first_name, 'Обновленный')
        self.assertEqual(updated_user.email, 'updated@example.com')
        
        # 8. Выход из системы
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        
        # 9. Проверка, что доступ к защищенным страницам закрыт
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 302)


class PermissionTest(IntegrationTestCase):
    """Тесты прав доступа"""
    
    def test_anonymous_user_permissions(self):
        """Тест прав анонимного пользователя"""
        # Публичные страницы доступны
        public_urls = [
            reverse('blog:index'),
            reverse('blog:events'),
            reverse('blog:contact'),
            reverse('blog:ensembles_list'),
            reverse('users:signup'),
            reverse('users:login'),
        ]
        
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        
        # Защищенные страницы недоступны
        protected_urls = [
            reverse('blog:archive'),
            reverse('blog:create'),
            reverse('users:profile'),
            reverse('users:profile_edit'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_authenticated_user_permissions(self):
        """Тест прав авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        
        # Все страницы доступны
        all_urls = [
            reverse('blog:index'),
            reverse('blog:events'),
            reverse('blog:contact'),
            reverse('blog:ensembles_list'),
            reverse('blog:archive'),
            reverse('blog:create'),
            reverse('users:profile'),
            reverse('users:profile_edit'),
        ]
        
        for url in all_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_user_cannot_access_other_user_events(self):
        """Тест, что пользователь не может получить доступ к событиям других пользователей"""
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Создаем событие от другого пользователя
        other_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Секретное событие",
            date=date.today() + timezone.timedelta(days=5),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=other_user
        )
        
        # Авторизуемся как первый пользователь
        self.client.login(username='testuser', password='testpass123')
        
        # Пытаемся получить доступ к событию другого пользователя
        response = self.client.get(reverse('blog:event_detail', kwargs={'slug': other_event.slug}))
        # Детальная страница события должна быть доступна всем (публичная)
        self.assertEqual(response.status_code, 200)
        
        # Но в архиве мы не должны видеть события других пользователей
        response = self.client.get(reverse('blog:archive'))
        events = response.context['events']
        self.assertNotIn(other_event, events)


class DataIntegrityTest(IntegrationTestCase):
    """Тесты целостности данных"""
    
    def test_event_deletion_cascade(self):
        """Тест каскадного удаления событий при удалении пользователя"""
        # Создаем пользователя и его события
        temp_user = User.objects.create_user(
            username='tempuser',
            email='temp@example.com',
            password='temppass123'
        )
        
        temp_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Временное событие",
            date=date.today() + timezone.timedelta(days=10),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=temp_user
        )
        
        # Проверяем, что событие создано
        self.assertEqual(temp_event.created_by, temp_user)
        
        # Удаляем пользователя
        temp_user.delete()
        
        # Проверяем, что событие тоже удалено (CASCADE)
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(name="Временное событие")
    
    def test_venue_deletion_set_null(self):
        """Тест SET_NULL при удалении места проведения"""
        # Создаем событие с местом проведения
        event_with_venue = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Событие с местом",
            date=date.today() + timezone.timedelta(days=15),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        # Проверяем, что событие связано с местом проведения
        self.assertEqual(event_with_venue.venue, self.venue)
        
        # Удаляем место проведения
        self.venue.delete()
        
        # Обновляем событие из базы данных
        event_with_venue.refresh_from_db()
        
        # Проверяем, что venue стало None (SET_NULL)
        self.assertIsNone(event_with_venue.venue)
    
    def test_ensemble_relationship_integrity(self):
        """Тест целостности связи ManyToMany с коллективами"""
        # Создаем событие с коллективом
        event_with_ensemble = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Событие с коллективом",
            date=date.today() + timezone.timedelta(days=20),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        event_with_ensemble.ensembles.add(self.ensemble)
        
        # Проверяем связь
        self.assertIn(self.ensemble, event_with_ensemble.ensembles.all())
        
        # Удаляем коллектив
        self.ensemble.delete()
        
        # Обновляем событие из базы данных
        event_with_ensemble.refresh_from_db()
        
        # Проверяем, что связь удалена
        self.assertEqual(event_with_ensemble.ensembles.count(), 0)


class BusinessLogicTest(IntegrationTestCase):
    """Тесты бизнес-логики"""
    
    def test_future_events_filtering(self):
        """Тест фильтрации будущих событий"""
        # Создаем события с разными датами
        today_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Событие сегодня",
            date=date.today(),
            time=time(20, 0),  # После текущего времени
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        past_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Прошедшее событие",
            date=date.today() - timezone.timedelta(days=1),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        # Проверяем, что на странице событий показываются только будущие
        response = self.client.get(reverse('blog:events'))
        events = response.context['events']
        
        self.assertIn(self.future_event, events)
        self.assertIn(today_event, events)
        self.assertNotIn(past_event, events)
        self.assertNotIn(self.past_event, events)
    
    def test_archive_shows_only_past_events(self):
        """Тест, что архив показывает только прошедшие события"""
        self.client.login(username='testuser', password='testpass123')
        
        # Создаем событие на сегодня, но уже прошедшее по времени
        past_today_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Прошедшее сегодня",
            date=date.today(),
            time=time(10, 0),  # Раннее время
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        response = self.client.get(reverse('blog:archive'))
        events = response.context['events']
        
        self.assertIn(self.past_event, events)
        self.assertIn(past_today_event, events)
        self.assertNotIn(self.future_event, events)
    
    def test_slug_generation_uniqueness(self):
        """Тест уникальности генерации slug"""
        # Создаем несколько событий с одинаковыми названиями
        event1 = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Одинаковое название",
            date=date.today() + timezone.timedelta(days=1),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        event2 = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Одинаковое название",
            date=date.today() + timezone.timedelta(days=2),
            time=time(19, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        # Проверяем, что slug'и разные
        self.assertNotEqual(event1.slug, event2.slug)
        self.assertIn("odinakovoe-nazvanie", event1.slug)
        self.assertIn("odinakovoe-nazvanie", event2.slug)
        
        # Проверяем, что оба slug'а уникальны в базе данных
        all_slugs = Event.objects.values_list('slug', flat=True)
        self.assertEqual(len(all_slugs), len(set(all_slugs)))
    
    def test_event_ordering(self):
        """Тест сортировки событий"""
        # Создаем события с разными датами и временем
        early_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Раннее событие",
            date=date.today() + timezone.timedelta(days=1),
            time=time(18, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        late_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Позднее событие",
            date=date.today() + timezone.timedelta(days=1),
            time=time(20, 0),
            price="1000 руб",
            description="Описание",
            venue=self.venue,
            created_by=self.user
        )
        
        # Проверяем сортировку на странице событий
        response = self.client.get(reverse('blog:events'))
        events = list(response.context['events'])
        
        # События должны быть отсортированы по дате и времени
        self.assertEqual(events[0], early_event)
        self.assertEqual(events[1], late_event)
        self.assertEqual(events[2], self.future_event) 