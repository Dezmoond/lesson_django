from django.contrib import admin
from .models import EventCategory, Venue, Festival, Ensemble, Event, News, NewsCategory
from django.core.management import call_command

# Register your models here.
@admin.action(description="🔄 Запустить парсинг мероприятий с QuickTickets")
def run_parser(modeladmin, request, queryset):
    call_command("parse_events")  # Запускает management-команду

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'date', 'time', 'price', 'venue', 'created_by')
    list_filter = ('category', 'date', 'venue', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('date', 'time')
    actions = [run_parser]  # Добавляем кнопку в раздел "Мероприятия"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового объекта
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'published_at')
    list_filter = ('category', 'is_published', 'published_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    ordering = ('-published_at',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'category', 'content', 'excerpt')
        }),
        ('Медиа', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Публикация', {
            'fields': ('is_published', 'author', 'published_at')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового объекта
            obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Venue)
admin.site.register(Festival)
admin.site.register(Ensemble)
admin.site.register(Event, EventAdmin)
admin.site.register(News, NewsAdmin)
