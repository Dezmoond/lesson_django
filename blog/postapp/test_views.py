from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, datetime
from django.contrib.auth.models import AnonymousUser

from .models import Event, EventCategory, Venue, Festival, Ensemble

User = get_user_model()


class ViewsTestCase(TestCase):
    """Базовый класс для тестов views"""
    
    def setUp(self):
        self.client = Client()
        
        # Создаем пользователей
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
        
        # Создаем будущее событие
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
        
        # Создаем прошедшее событие
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


class IndexViewTest(ViewsTestCase):
    """Тесты для главной страницы"""
    
    def test_index_view_status_code(self):
        """Тест кода ответа главной страницы"""
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('blog:index'))
        self.assertTemplateUsed(response, 'postapp/index.html')
    
    def test_index_view_context(self):
        """Тест контекста главной страницы"""
        response = self.client.get(reverse('blog:index'))
        self.assertIn('latest_events', response.context)
        # Проверяем, что в контексте есть будущие события
        latest_events = response.context['latest_events']
        self.assertIn(self.future_event, latest_events)
        # Проверяем, что прошедшие события не включены
        self.assertNotIn(self.past_event, latest_events)


class EventsViewTest(ViewsTestCase):
    """Тесты для страницы списка событий"""
    
    def test_events_view_status_code(self):
        """Тест кода ответа страницы событий"""
        response = self.client.get(reverse('blog:events'))
        self.assertEqual(response.status_code, 200)
    
    def test_events_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('blog:events'))
        self.assertTemplateUsed(response, 'postapp/events.html')
    
    def test_events_view_shows_only_future_events(self):
        """Тест отображения только будущих событий"""
        response = self.client.get(reverse('blog:events'))
        events = response.context['events']
        self.assertIn(self.future_event, events)
        self.assertNotIn(self.past_event, events)
    
    def test_events_view_filtering_by_category(self):
        """Тест фильтрации по категории"""
        # Создаем событие другой категории
        play_event = Event.objects.create(
            category=EventCategory.PLAY,
            name="Спектакль",
            date=date.today() + timezone.timedelta(days=10),
            time=time(18, 0),
            price="1200 руб",
            description="Спектакль",
            venue=self.venue,
            created_by=self.user
        )
        
        # Фильтруем по категории концерт
        response = self.client.get(reverse('blog:events'), {'category': 'концерт'})
        events = response.context['events']
        self.assertIn(self.future_event, events)
        self.assertNotIn(play_event, events)
    
    def test_events_view_filtering_by_venue(self):
        """Тест фильтрации по месту проведения"""
        # Создаем другое место проведения
        other_venue = Venue.objects.create(
            name="Другой зал",
            address="ул. Пушкина, 10"
        )
        
        other_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Концерт в другом зале",
            date=date.today() + timezone.timedelta(days=5),
            time=time(20, 0),
            price="1500 руб",
            description="Концерт",
            venue=other_venue,
            created_by=self.user
        )
        
        # Фильтруем по первому месту проведения
        response = self.client.get(reverse('blog:events'), {'venue': self.venue.id})
        events = response.context['events']
        self.assertIn(self.future_event, events)
        self.assertNotIn(other_event, events)
    
    def test_events_view_filtering_by_ensemble(self):
        """Тест фильтрации по коллективу"""
        # Создаем другой коллектив
        other_ensemble = Ensemble.objects.create(name="Камерный оркестр")
        
        other_event = Event.objects.create(
            category=EventCategory.CONCERT,
            name="Концерт другого коллектива",
            date=date.today() + timezone.timedelta(days=3),
            time=time(19, 30),
            price="900 руб",
            description="Концерт",
            venue=self.venue,
            created_by=self.user
        )
        other_event.ensembles.add(other_ensemble)
        
        # Фильтруем по первому коллективу
        response = self.client.get(reverse('blog:events'), {'ensemble': self.ensemble.id})
        events = response.context['events']
        self.assertIn(self.future_event, events)
        self.assertNotIn(other_event, events)
    
    def test_events_view_context_data(self):
        """Тест контекста страницы событий"""
        response = self.client.get(reverse('blog:events'))
        self.assertIn('categories', response.context)
        self.assertIn('all_venues', response.context)
        self.assertIn('all_ensembles', response.context)
        self.assertIn('selected_category', response.context)
        self.assertIn('selected_venue_id', response.context)
        self.assertIn('selected_ensemble_id', response.context)


class EventDetailViewTest(ViewsTestCase):
    """Тесты для детальной страницы события"""
    
    def test_event_detail_view_status_code(self):
        """Тест кода ответа детальной страницы"""
        response = self.client.get(reverse('blog:event_detail', kwargs={'slug': self.future_event.slug}))
        self.assertEqual(response.status_code, 200)
    
    def test_event_detail_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('blog:event_detail', kwargs={'slug': self.future_event.slug}))
        self.assertTemplateUsed(response, 'postapp/event_detail.html')
    
    def test_event_detail_view_context(self):
        """Тест контекста детальной страницы"""
        response = self.client.get(reverse('blog:event_detail', kwargs={'slug': self.future_event.slug}))
        self.assertEqual(response.context['event'], self.future_event)
    
    def test_event_detail_view_404_for_invalid_slug(self):
        """Тест 404 для несуществующего slug"""
        response = self.client.get(reverse('blog:event_detail', kwargs={'slug': 'non-existent-slug'}))
        self.assertEqual(response.status_code, 404)


class ArchiveViewTest(ViewsTestCase):
    """Тесты для страницы архива (требует авторизации)"""
    
    def test_archive_view_requires_login(self):
        """Тест требования авторизации для архива"""
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_archive_view_status_code_for_authenticated_user(self):
        """Тест кода ответа для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)
    
    def test_archive_view_template(self):
        """Тест использования правильного шаблона"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:archive'))
        self.assertTemplateUsed(response, 'postapp/archive.html')
    
    def test_archive_view_shows_only_past_events(self):
        """Тест отображения только прошедших событий"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:archive'))
        events = response.context['events']
        self.assertIn(self.past_event, events)
        self.assertNotIn(self.future_event, events)
    
    def test_archive_view_filtering(self):
        """Тест фильтрации в архиве"""
        self.client.login(username='testuser', password='testpass123')
        
        # Создаем еще одно прошедшее событие другой категории
        past_play = Event.objects.create(
            category=EventCategory.PLAY,
            name="Прошедший спектакль",
            date=date.today() - timezone.timedelta(days=5),
            time=time(18, 0),
            price="1100 руб",
            description="Спектакль",
            venue=self.venue,
            created_by=self.user
        )
        
        # Фильтруем по категории концерт
        response = self.client.get(reverse('blog:archive'), {'category': 'концерт'})
        events = response.context['events']
        self.assertIn(self.past_event, events)
        self.assertNotIn(past_play, events)


class CreateEventViewTest(ViewsTestCase):
    """Тесты для страницы создания события (требует авторизации)"""
    
    def test_create_event_view_requires_login(self):
        """Тест требования авторизации для создания события"""
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_create_event_view_status_code_for_authenticated_user(self):
        """Тест кода ответа для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_event_view_template(self):
        """Тест использования правильного шаблона"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:create'))
        self.assertTemplateUsed(response, 'postapp/create.html')
    
    def test_create_event_view_form_submission(self):
        """Тест отправки формы создания события"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'category': EventCategory.CONCERT,
            'name': 'Новый концерт',
            'date': '2024-07-15',
            'time': '19:00',
            'price': '1200 руб',
            'description': 'Описание нового концерта',
            'venue': self.venue.id,
        }
        
        response = self.client.post(reverse('blog:create'), form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешного создания
        
        # Проверяем, что событие создано
        new_event = Event.objects.get(name='Новый концерт')
        self.assertEqual(new_event.created_by, self.user)
        self.assertEqual(new_event.category, EventCategory.CONCERT)
    
    def test_create_event_view_invalid_form(self):
        """Тест отправки невалидной формы"""
        self.client.login(username='testuser', password='testpass123')
        
        # Отправляем форму без обязательных полей
        form_data = {
            'category': EventCategory.CONCERT,
            # Отсутствует name
            'date': '2024-07-15',
            'time': '19:00',
            'price': '1200 руб',
        }
        
        response = self.client.post(reverse('blog:create'), form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertFormError(response, 'form', 'name', ['This field is required.'])


class ContactViewTest(ViewsTestCase):
    """Тесты для страницы контактов"""
    
    def test_contact_view_status_code(self):
        """Тест кода ответа страницы контактов"""
        response = self.client.get(reverse('blog:contact'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('blog:contact'))
        self.assertTemplateUsed(response, 'postapp/contact.html')
    
    def test_contact_view_form_submission(self):
        """Тест отправки формы контактов"""
        form_data = {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'subject': 'Вопрос о мероприятии',
            'message': 'Здравствуйте! У меня есть вопрос.'
        }
        
        response = self.client.post(reverse('blog:contact'), form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешной отправки
    
    def test_contact_view_invalid_form(self):
        """Тест отправки невалидной формы контактов"""
        form_data = {
            'name': 'Иван Иванов',
            'email': 'invalid-email',  # Невалидный email
            'subject': 'Вопрос',
            'message': 'Сообщение'
        }
        
        response = self.client.post(reverse('blog:contact'), form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertFormError(response, 'form', 'email', ['Enter a valid email address.'])


class EnsembleListViewTest(ViewsTestCase):
    """Тесты для страницы списка коллективов"""
    
    def test_ensemble_list_view_status_code(self):
        """Тест кода ответа страницы коллективов"""
        response = self.client.get(reverse('blog:ensembles_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_ensemble_list_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('blog:ensembles_list'))
        self.assertTemplateUsed(response, 'postapp/ensemble_list.html')
    
    def test_ensemble_list_view_context(self):
        """Тест контекста страницы коллективов"""
        response = self.client.get(reverse('blog:ensembles_list'))
        self.assertIn('ensembles', response.context)
        ensembles = response.context['ensembles']
        self.assertIn(self.ensemble, ensembles)


class AuthenticationTest(ViewsTestCase):
    """Тесты аутентификации и прав доступа"""
    
    def test_anonymous_user_access_to_public_pages(self):
        """Тест доступа анонимного пользователя к публичным страницам"""
        public_urls = [
            reverse('blog:index'),
            reverse('blog:events'),
            reverse('blog:contact'),
            reverse('blog:ensembles_list'),
        ]
        
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_anonymous_user_access_to_protected_pages(self):
        """Тест доступа анонимного пользователя к защищенным страницам"""
        protected_urls = [
            reverse('blog:archive'),
            reverse('blog:create'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_authenticated_user_access_to_protected_pages(self):
        """Тест доступа авторизованного пользователя к защищенным страницам"""
        self.client.login(username='testuser', password='testpass123')
        
        protected_urls = [
            reverse('blog:archive'),
            reverse('blog:create'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_user_can_only_see_own_events_in_archive(self):
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


class URLPatternsTest(ViewsTestCase):
    """Тесты URL паттернов"""
    
    def test_url_patterns_exist(self):
        """Тест существования всех URL паттернов"""
        urls_to_test = [
            ('blog:index', {}),
            ('blog:events', {}),
            ('blog:event_detail', {'slug': self.future_event.slug}),
            ('blog:archive', {}),
            ('blog:create', {}),
            ('blog:contact', {}),
            ('blog:ensembles_list', {}),
        ]
        
        for url_name, kwargs in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                self.assertIsInstance(url, str)
                self.assertGreater(len(url), 0)
            except Exception as e:
                self.fail(f"URL {url_name} не существует: {e}")
    
    def test_url_patterns_return_valid_responses(self):
        """Тест, что все URL возвращают валидные ответы"""
        # Публичные URL
        public_urls = [
            ('blog:index', {}),
            ('blog:events', {}),
            ('blog:contact', {}),
            ('blog:ensembles_list', {}),
        ]
        
        for url_name, kwargs in public_urls:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])  # 200 или редирект
        
        # Защищенные URL (требуют авторизации)
        self.client.login(username='testuser', password='testpass123')
        
        protected_urls = [
            ('blog:archive', {}),
            ('blog:create', {}),
        ]
        
        for url_name, kwargs in protected_urls:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200) 