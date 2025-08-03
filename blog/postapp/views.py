from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, ListView, CreateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q
from datetime import date, datetime
from django.contrib import messages
from .models import Event, EventCategory, Ensemble, Venue

from .forms import EventForm, ContactForm

# =========================================================
# 1. Class-Based Views для существующих страниц
# =========================================================

# Главная страница (index.html)
class IndexView(TemplateView):
    template_name = 'postapp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь вы можете добавить любой динамический контент для главной страницы, если понадобится
        # Например, последние 3 мероприятия
        context['latest_events'] = Event.objects.filter(
            Q(date__gt=date.today()) | (Q(date=date.today()) & Q(time__gte=datetime.now().time()))
        ).order_by('date', 'time')[:3]
        return context


# Страница со списком предстоящих мероприятий
class EventsView(ListView):
    model = Event
    template_name = 'postapp/events.html'
    context_object_name = 'events'
    ordering = ['date', 'time']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        today = date.today()
        now = datetime.now().time()

        queryset = queryset.filter(Q(date__gt=today) | (Q(date=today) & Q(time__gte=now)))

        # Применяем фильтр по категории
        category_filter = self.request.GET.get('category')
        if category_filter and category_filter != 'all':
            queryset = queryset.filter(category=category_filter)

        # НОВОЕ: Применяем фильтр по коллективу
        ensemble_filter_id = self.request.GET.get('ensemble')
        if ensemble_filter_id and ensemble_filter_id != 'all':
            # ensemble__id для фильтрации ManyToManyField по ID
            queryset = queryset.filter(ensembles__id=ensemble_filter_id)

            # НОВОЕ: Применяем фильтр по площадке
        venue_filter_id = self.request.GET.get('venue')
        if venue_filter_id and venue_filter_id != 'all':
            # venue__id для фильтрации ForeignKey по ID
            queryset = queryset.filter(venue__id=venue_filter_id)

        # Убедимся, что результаты уникальны, если фильтруем по ManyToMany (ensembles)
        # Это может вернуть дубликаты, если одно событие имеет несколько ансамблей,
        # и оба соответствуют фильтру, или если событие соответствует нескольким ансамблям.
        # .distinct() поможет избежать дубликатов в результирующем QuerySet.
        queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.choices
        context['selected_category'] = self.request.GET.get('category', 'all')

        # НОВОЕ: Добавляем все коллективы и площадки в контекст
        context['all_ensembles'] = Ensemble.objects.all().order_by('name')
        context['selected_ensemble_id'] = self.request.GET.get('ensemble', 'all')

        context['all_venues'] = Venue.objects.all().order_by('name')
        context['selected_venue_id'] = self.request.GET.get('venue', 'all')

        return context


# Страница с просмотром детальной информации о мероприятии
class EventDetailView(DetailView):
    model = Event
    template_name = 'postapp/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'  # Используем поле slug для поиска
    slug_url_kwarg = 'slug'  # Имя параметра в URL


# Страница с прошедшими мероприятиями (archive.html)
class ArchiveView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'postapp/archive.html'
    context_object_name = 'events'
    ordering = ['-date', '-time']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        today = date.today()
        now = datetime.now().time()

        # Фильтруем только события текущего пользователя
        queryset = queryset.filter(created_by=self.request.user)
        
        # Фильтруем только прошедшие события
        queryset = queryset.filter(Q(date__lt=today) | (Q(date=today) & Q(time__lt=now)))

        category_filter = self.request.GET.get('category')
        if category_filter and category_filter != 'all':
            queryset = queryset.filter(category=category_filter)

        # НОВОЕ: Применяем фильтр по коллективу
        ensemble_filter_id = self.request.GET.get('ensemble')
        if ensemble_filter_id and ensemble_filter_id != 'all':
            queryset = queryset.filter(ensembles__id=ensemble_filter_id)

        # НОВОЕ: Применяем фильтр по площадке
        venue_filter_id = self.request.GET.get('venue')
        if venue_filter_id and venue_filter_id != 'all':
            queryset = queryset.filter(venue__id=venue_filter_id)

        queryset = queryset.distinct()  # Для избежания дубликатов

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.choices
        context['selected_category'] = self.request.GET.get('category', 'all')

        # НОВОЕ: Добавляем все коллективы и площадки в контекст
        context['all_ensembles'] = Ensemble.objects.all().order_by('name')
        context['selected_ensemble_id'] = self.request.GET.get('ensemble', 'all')

        context['all_venues'] = Venue.objects.all().order_by('name')
        context['selected_venue_id'] = self.request.GET.get('venue', 'all')

        return context


# Страница для создания нового мероприятия
class CreateEventView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm  # Используем ранее определенную форму
    template_name = 'postapp/create.html'

    def get_success_url(self):
        # Перенаправляем на страницу со списком предстоящих мероприятий после успешного создания
        return reverse('blog:events')
    
    def form_valid(self, form):
        # Автоматически устанавливаем создателя события
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ContactView(FormView):
    template_name = 'postapp/contact.html'
    form_class = ContactForm  # Используем нашу новую форму

    # Куда перенаправить пользователя после успешной отправки формы
    # Можно перенаправить обратно на страницу контактов, но с сообщением
    def get_success_url(self):
        return reverse('blog:contact')  # Используем 'blog' namespace

    # Метод, который вызывается, если форма валидна
    def form_valid(self, form):
        # Здесь вы можете обработать данные формы:
        # Например, отправить email, сохранить в базу данных и т.д.
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        message_text = form.cleaned_data['message']

        print(f"Получено новое сообщение от {name} ({email}):")
        print(f"Телефон: {phone if phone else 'Не указан'}")
        print(f"Сообщение:\n{message_text}")

        # Добавляем сообщение об успешной отправке для пользователя
        messages.success(self.request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')

        return super().form_valid(form)  # Вызываем родительский метод для выполнения редиректа

    # Метод, который вызывается, если форма невалидна (например, поле Email неверное)
    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


# =========================================================
# 2. Новая страница: Просмотр коллективов (Ensemble List)
# =========================================================

class EnsembleListView(ListView):
    model = Ensemble
    template_name = 'postapp/ensemble_list.html'  # Создадим шаблон
    context_object_name = 'ensembles'  # Переменная для доступа к списку коллективов в шаблоне
    ordering = ['name']  # Сортировка по имени
    paginate_by = 10