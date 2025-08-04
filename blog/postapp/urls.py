from django.urls import path
from postapp import views

app_name = 'blog' # Ваше выбранное имя приложения для URL-ов

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('events/', views.EventsView.as_view(), name='events'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'), # Детальная страница события
    path('archive/', views.ArchiveView.as_view(), name='archive'),
    path('create/', views.CreateEventView.as_view(), name='create'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('ensembles/', views.EnsembleListView.as_view(), name='ensembles_list'),
    path('news/', views.NewsListView.as_view(), name='news_list'), # Список новостей
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'), # Детальная страница новости
]