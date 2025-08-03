from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from django.core import mail
from django.contrib.auth.models import AnonymousUser

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Тесты для модели CustomUser"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов',
            phone='+7-999-123-45-67',
            birth_date=date(1990, 1, 1),
            bio='Тестовый пользователь'
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Иван')
        self.assertEqual(self.user.last_name, 'Иванов')
        self.assertEqual(self.user.phone, '+7-999-123-45-67')
        self.assertEqual(self.user.birth_date, date(1990, 1, 1))
        self.assertEqual(self.user.bio, 'Тестовый пользователь')
        self.assertFalse(self.user.is_verified)
    
    def test_user_str_method(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_user_get_full_name(self):
        """Тест получения полного имени"""
        self.assertEqual(self.user.get_full_name(), 'Иван Иванов')
        
        # Тест для пользователя без имени и фамилии
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.assertEqual(user2.get_full_name(), 'user2')
    
    def test_user_get_short_name(self):
        """Тест получения короткого имени"""
        self.assertEqual(self.user.get_short_name(), 'Иван')
        
        # Тест для пользователя без имени
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.assertEqual(user2.get_short_name(), 'user2')
    
    def test_user_auto_fields(self):
        """Тест автоматически заполняемых полей"""
        self.assertIsNotNone(self.user.created_at)
        self.assertIsNotNone(self.user.updated_at)
        self.assertFalse(self.user.is_verified)
    
    def test_user_ordering(self):
        """Тест сортировки пользователей"""
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        users = User.objects.all()
        # Сортировка по -date_joined (новые сначала)
        self.assertEqual(users[0], user2)
        self.assertEqual(users[1], self.user)


class CustomUserCreationFormTest(TestCase):
    """Тесты для формы регистрации"""
    
    def test_user_creation_form_valid_data(self):
        """Тест валидных данных формы регистрации"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'phone': '+7-999-987-65-43',
            'birth_date': '1995-05-15',
            'bio': 'Новый пользователь'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_creation_form_invalid_data(self):
        """Тест невалидных данных формы регистрации"""
        # Форма без обязательных полей
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
    
    def test_user_creation_form_password_mismatch(self):
        """Тест несовпадения паролей"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass123',
            'first_name': 'Петр',
            'last_name': 'Петров'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_user_creation_form_duplicate_username(self):
        """Тест дублирования имени пользователя"""
        # Создаем пользователя
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        # Пытаемся создать пользователя с тем же именем
        form_data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Петр',
            'last_name': 'Петров'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_user_creation_form_duplicate_email(self):
        """Тест дублирования email"""
        # Создаем пользователя
        User.objects.create_user(
            username='user1',
            email='existing@example.com',
            password='pass123'
        )
        
        # Пытаемся создать пользователя с тем же email
        form_data = {
            'username': 'user2',
            'email': 'existing@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Петр',
            'last_name': 'Петров'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class CustomAuthenticationFormTest(TestCase):
    """Тесты для формы аутентификации"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_authentication_form_valid_data(self):
        """Тест валидных данных формы входа"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_authentication_form_invalid_data(self):
        """Тест невалидных данных формы входа"""
        # Неправильный пароль
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_authentication_form_empty_data(self):
        """Тест пустых данных формы входа"""
        form = CustomAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class UserProfileFormTest(TestCase):
    """Тесты для формы профиля пользователя"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов'
        )
    
    def test_profile_form_valid_data(self):
        """Тест валидных данных формы профиля"""
        form_data = {
            'first_name': 'Петр',
            'last_name': 'Петров',
            'email': 'petr@example.com',
            'phone': '+7-999-111-22-33',
            'birth_date': '1995-05-15',
            'bio': 'Обновленный профиль'
        }
        form = UserProfileForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_profile_form_invalid_email(self):
        """Тест невалидного email в форме профиля"""
        form_data = {
            'first_name': 'Петр',
            'last_name': 'Петров',
            'email': 'invalid-email',
            'phone': '+7-999-111-22-33'
        }
        form = UserProfileForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class ViewsTestCase(TestCase):
    """Базовый класс для тестов views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов'
        )


class SignUpViewTest(ViewsTestCase):
    """Тесты для страницы регистрации"""
    
    def test_signup_view_status_code(self):
        """Тест кода ответа страницы регистрации"""
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
    
    def test_signup_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
    
    def test_signup_view_form_submission(self):
        """Тест отправки формы регистрации"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'phone': '+7-999-987-65-43',
            'birth_date': '1995-05-15',
            'bio': 'Новый пользователь'
        }
        
        response = self.client.post(reverse('users:signup'), form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешной регистрации
        
        # Проверяем, что пользователь создан
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.first_name, 'Петр')
        self.assertEqual(new_user.last_name, 'Петров')
    
    def test_signup_view_invalid_form(self):
        """Тест отправки невалидной формы регистрации"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'differentpass123',
        }
        
        response = self.client.post(reverse('users:signup'), form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertFormError(response, 'form', 'email', ['Enter a valid email address.'])
        self.assertFormError(response, 'form', 'password2')


class CustomLoginViewTest(ViewsTestCase):
    """Тесты для страницы входа"""
    
    def test_login_view_status_code(self):
        """Тест кода ответа страницы входа"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('users:login'))
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_view_successful_login(self):
        """Тест успешного входа"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('users:login'), form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа
        
        # Проверяем, что пользователь авторизован
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)
    
    def test_login_view_invalid_credentials(self):
        """Тест входа с неверными данными"""
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(reverse('users:login'), form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertFormError(response, 'form', '__all__', ['Please enter a correct username and password. Note that both fields may be case-sensitive.'])


class LogoutViewTest(ViewsTestCase):
    """Тесты для выхода из системы"""
    
    def test_logout_view(self):
        """Тест выхода из системы"""
        # Сначала входим в систему
        self.client.login(username='testuser', password='testpass123')
        
        # Проверяем, что пользователь авторизован
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        
        # Выходим из системы
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
        
        # Проверяем, что пользователь больше не авторизован
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа


class ProfileViewTest(ViewsTestCase):
    """Тесты для страницы профиля"""
    
    def test_profile_view_requires_login(self):
        """Тест требования авторизации для просмотра профиля"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_profile_view_status_code_for_authenticated_user(self):
        """Тест кода ответа для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_view_template(self):
        """Тест использования правильного шаблона"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertTemplateUsed(response, 'users/profile.html')
    
    def test_profile_view_context(self):
        """Тест контекста страницы профиля"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.context['user'], self.user)


class ProfileUpdateViewTest(ViewsTestCase):
    """Тесты для страницы редактирования профиля"""
    
    def test_profile_update_view_requires_login(self):
        """Тест требования авторизации для редактирования профиля"""
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_profile_update_view_status_code_for_authenticated_user(self):
        """Тест кода ответа для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_update_view_template(self):
        """Тест использования правильного шаблона"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile_edit'))
        self.assertTemplateUsed(response, 'users/profile_edit.html')
    
    def test_profile_update_view_form_submission(self):
        """Тест отправки формы редактирования профиля"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'first_name': 'Петр',
            'last_name': 'Петров',
            'email': 'petr@example.com',
            'phone': '+7-999-111-22-33',
            'birth_date': '1995-05-15',
            'bio': 'Обновленный профиль'
        }
        
        response = self.client.post(reverse('users:profile_edit'), form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешного обновления
        
        # Проверяем, что профиль обновлен
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.first_name, 'Петр')
        self.assertEqual(updated_user.last_name, 'Петров')
        self.assertEqual(updated_user.email, 'petr@example.com')
        self.assertEqual(updated_user.phone, '+7-999-111-22-33')
    
    def test_profile_update_view_invalid_form(self):
        """Тест отправки невалидной формы редактирования профиля"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'first_name': 'Петр',
            'last_name': 'Петров',
            'email': 'invalid-email',
            'phone': '+7-999-111-22-33'
        }
        
        response = self.client.post(reverse('users:profile_edit'), form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertFormError(response, 'form', 'email', ['Enter a valid email address.'])


class AuthenticationIntegrationTest(ViewsTestCase):
    """Интеграционные тесты аутентификации"""
    
    def test_complete_auth_flow(self):
        """Тест полного цикла аутентификации"""
        # 1. Регистрация нового пользователя
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Новый',
            'last_name': 'Пользователь'
        }
        
        response = self.client.post(reverse('users:signup'), signup_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Вход в систему
        login_data = {
            'username': 'newuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('users:login'), login_data)
        self.assertEqual(response.status_code, 302)
        
        # 3. Проверяем доступ к защищенным страницам
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Выход из системы
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        
        # 5. Проверяем, что доступ к защищенным страницам закрыт
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
    
    def test_redirect_after_login(self):
        """Тест редиректа после входа"""
        # Пытаемся получить доступ к защищенной странице без авторизации
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        
        # Входим в систему
        self.client.login(username='testuser', password='testpass123')
        
        # Проверяем, что теперь можем получить доступ
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)


class URLPatternsTest(ViewsTestCase):
    """Тесты URL паттернов пользовательского приложения"""
    
    def test_url_patterns_exist(self):
        """Тест существования всех URL паттернов"""
        urls_to_test = [
            ('users:signup', {}),
            ('users:login', {}),
            ('users:logout', {}),
            ('users:profile', {}),
            ('users:profile_edit', {}),
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
            ('users:signup', {}),
            ('users:login', {}),
        ]
        
        for url_name, kwargs in public_urls:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        
        # Защищенные URL (требуют авторизации)
        self.client.login(username='testuser', password='testpass123')
        
        protected_urls = [
            ('users:profile', {}),
            ('users:profile_edit', {}),
        ]
        
        for url_name, kwargs in protected_urls:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        
        # URL выхода
        logout_url = reverse('users:logout')
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, 302)
