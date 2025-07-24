# blog/postapp/views.py
from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse
from datetime import date, datetime, time

# Импортируйте ваши модели и формы
from .models import Event, Ensemble, Venue
from .forms import ContactForm, EventForm # Эти файлы forms.py нужно будет создать

# 1. Новая функция для пустой главной страницы (если она действительно должна быть пустой)
# 1. Функция для "Главной" страницы (статический контент из postapp/index.html)
def main_landing_view(request):
    """
    Представляет главную страницу, которая является статической.
    """
    # Этот шаблон должен быть blog/postapp/templates/postapp/index.html
    return render(request, 'postapp/index.html', {})

# 2. Функция для "Мероприятий" (текущие с сортировкой)
def main_view(request):
    """
    Представляет предстоящие мероприятия с фильтрацией и сортировкой.
    """
    events = Event.objects.all()
    today = date.today()

    # Фильтрация по предстоящим событиям (уже есть, убеждаемся, что она на месте)
    events = events.filter(Q(date__gt=today) | Q(date=today, time__gte=datetime.now().time()))

    # Фильтрация по диапазону дат
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            events = events.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            events = events.filter(date__lte=end_date)
        except ValueError:
            pass

    # Фильтрация по организациям (Ensemble)
    selected_ensembles = request.GET.getlist('ensembles')
    if selected_ensembles:
        events = events.filter(ensembles__name__in=selected_ensembles).distinct()

    # НОВОЕ: Фильтрация по площадкам (Venue)
    selected_venue = request.GET.get('venue')
    if selected_venue:
        events = events.filter(venue__name=selected_venue) # Фильтруем по имени площадки

    # Сортировка: сначала по дате, затем по времени
    events = events.order_by('date', 'time')

    all_ensembles = Ensemble.objects.all().order_by('name')
    all_venues = Venue.objects.all().order_by('name') # Получаем все площадки для фильтра

    context = {
        'events': events,
        'all_ensembles': all_ensembles,
        'all_venues': all_venues, # Передаем все площадки в шаблон
        'selected_ensembles': selected_ensembles,
        'selected_start_date': start_date_str,
        'selected_end_date': end_date_str,
        'selected_venue': selected_venue, # Передаем выбранную площадку в шаблон
    }
    # Этот шаблон должен быть blog/postapp/templates/postapp/events.html
    return render(request, 'postapp/events.html', context)

# 3. Функция для "Прошедшие" (архив с сортировкой)
def past_events_view(request):
    """
    Представляет прошедшие мероприятия с фильтрацией и сортировкой.
    """
    events = Event.objects.all()
    today = date.today()
    current_time = datetime.now().time()

    # Фильтрация по прошедшим событиям
    events = events.filter(Q(date__lt=today) | Q(date=today, time__lt=current_time))

    # Фильтрация по диапазону дат
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            events = events.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            events = events.filter(date__lte=end_date)
        except ValueError:
            pass

    # Фильтрация по организациям (Ensemble)
    selected_ensembles = request.GET.getlist('ensembles')
    if selected_ensembles:
        events = events.filter(ensembles__name__in=selected_ensembles).distinct()

    # НОВОЕ: Фильтрация по площадкам (Venue)
    selected_venue = request.GET.get('venue')
    if selected_venue:
        events = events.filter(venue__name=selected_venue) # Фильтруем по имени площадки

    # Сортировка: сначала по дате (убывание), затем по времени (убывание)
    events = events.order_by('-date', '-time')

    all_ensembles = Ensemble.objects.all().order_by('name')
    all_venues = Venue.objects.all().order_by('name') # Получаем все площадки для фильтра

    context = {
        'events': events,
        'all_ensembles': all_ensembles,
        'all_venues': all_venues, # Передаем все площадки в шаблон
        'selected_ensembles': selected_ensembles,
        'selected_start_date': start_date_str,
        'selected_end_date': end_date_str,
        'selected_venue': selected_venue, # Передаем выбранную площадку в шаблон
    }
    return render(request, 'postapp/archive.html', context)
def create_event(request):
    """
    Позволяет добавлять новые мероприятия через форму.
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('blog:events')) # Перенаправляем на страницу с мероприятиями
    else:
        form = EventForm()
    return render(request, 'postapp/create.html', {'form': form})

# 5. Функция для "Контакты" (форма контактов)
def contact(request):
    """
    Представляет форму контактов и обрабатывает ее отправку.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Здесь логика обработки формы (например, отправка email)
            # print(f"Имя: {form.cleaned_data['name']}")
            # print(f"Email: {form.cleaned_data['email']}")
            # print(f"Сообщение: {form.cleaned_data['message']}")
            return redirect(reverse('blog:index')) # Или на страницу "спасибо"
    else:
        form = ContactForm()
    return render(request, 'postapp/contact.html', {'form': form})