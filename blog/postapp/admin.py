from django.contrib import admin
from .models import EventCategory, Venue, Festival, Ensemble, Event
from django.core.management import call_command

# Register your models here.
@admin.action(description="🔄 Запустить парсинг мероприятий с QuickTickets")
def run_parser(modeladmin, request, queryset):
    call_command("parse_events")  # Запускает management-команду

class EventAdmin(admin.ModelAdmin):
    actions = [run_parser]  # Добавляем кнопку в раздел “Мероприятия”
admin.site.register(Venue)
admin.site.register(Festival)
admin.site.register(Ensemble)
admin.site.register(Event, EventAdmin)
