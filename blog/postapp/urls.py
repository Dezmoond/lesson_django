from django.urls import path
from postapp import views

app_name = 'blog' # Ваше выбранное имя приложения для URL-ов

urlpatterns = [
    # Главная страница (статическая) - использует blog/postapp/templates/postapp/index.html
    path('', views.main_landing_view, name='index'),

    # Мероприятия (динамические, текущие с сортировкой) - будет использовать blog/postapp/templates/postapp/events.html
    path('events/', views.main_view, name='events'),

    # Прошедшие мероприятия - использует blog/postapp/templates/postapp/history.html
    path('archive/', views.past_events_view, name='archive'),

    # Добавить мероприятие - использует blog/postapp/templates/postapp/create_event.html
    path('create/', views.create_event, name='create'),

    # Контакты - использует blog/postapp/templates/postapp/contact.html
    path('contact/', views.contact, name='contact'),
]