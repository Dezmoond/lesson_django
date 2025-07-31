from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

User = get_user_model()

class SignUpView(CreateView):
    """Представление для регистрации пользователей"""
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация прошла успешно! Теперь вы можете войти в систему.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при регистрации. Пожалуйста, исправьте ошибки.')
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    """Представление для авторизации пользователей"""
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Добро пожаловать, {self.request.user.get_full_name()}!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)

@login_required
def logout_view(request):
    """Представление для выхода из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('blog:index')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлен!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при обновлении профиля. Пожалуйста, исправьте ошибки.')
        return super().form_invalid(form)

@login_required
def profile_view(request):
    """Представление для просмотра профиля"""
    return render(request, 'users/profile.html', {'user': request.user})
