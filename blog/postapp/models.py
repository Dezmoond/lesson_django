from django.db import models
from django.utils.text import slugify
from django.db.models import Q
from datetime import date, datetime

# Категории событий
class EventCategory(models.TextChoices):
    CONCERT = "концерт", "Концерт"
    PLAY = "спектакль", "Спектакль"
    OPERA = "опера", "Опера"
    FORUM = "форум", "Форум"
    ANCIENT_MUSIC = "концерт старинной музыки", "Концерт старинной музыки"
    ORGAN_CONCERT = "органный концерт", "Органный концерт"
    CLASSICAL_MUSIC = "концерт классической музыки", "Концерт классической музыки"
    SYMPHONIC_MUSIC = "концерт симфонической музыки", "Концерт симфонической музыки"
    FOLK_MUSIC = "концерт народной музыки", "Концерт народной музыки"
    MUSIC_THEATRE = "театрально музыкальная постановка", "Театрально музыкальная постановка"
    BALLET = "балет", "Балет"
    CIRCUS = "цирк", "Цирк"
    VIRTUAL_CONCERT = "виртуальный концерт", "Виртуальный концерт"
    FAIRY_TALE = "музыкальная сказка для детей", "Музыкальная сказка для детей"
    SHOW = "шоу программа", "Шоу программа"
    DANCE = "танцы", "Танцы"

# Категории новостей
class NewsCategory(models.TextChoices):
    GENERAL = "общие", "Общие новости"
    CULTURE = "культура", "Культурные события"
    MUSIC = "музыка", "Музыкальные новости"
    THEATRE = "театр", "Театральные новости"
    FESTIVAL = "фестивали", "Фестивали"
    ANNOUNCEMENT = "анонсы", "Анонсы мероприятий"
    INTERVIEW = "интервью", "Интервью"
    REVIEW = "обзоры", "Обзоры"

# Менеджер для Event
class EventManager(models.Manager):
    def upcoming(self):
        """Возвращает предстоящие события"""
        today = date.today()
        now = datetime.now().time()
        return self.filter(
            Q(date__gt=today) | (Q(date=today) & Q(time__gte=now))
        ).order_by('date', 'time')
    
    def past(self):
        """Возвращает прошедшие события"""
        today = date.today()
        now = datetime.now().time()
        return self.filter(
            Q(date__lt=today) | (Q(date=today) & Q(time__lt=now))
        ).order_by('-date', '-time')
    
    def today(self):
        """Возвращает события на сегодня"""
        today = date.today()
        return self.filter(date=today).order_by('time')
    
    def this_week(self):
        """Возвращает события на текущую неделю"""
        from datetime import timedelta
        today = date.today()
        week_end = today + timedelta(days=7)
        return self.filter(
            date__gte=today,
            date__lte=week_end
        ).order_by('date', 'time')
    
    def by_category(self, category):
        """Возвращает события по категории"""
        return self.filter(category=category).order_by('date', 'time')
    
    def by_venue(self, venue_id):
        """Возвращает события по площадке"""
        return self.filter(venue_id=venue_id).order_by('date', 'time')
    
    def by_ensemble(self, ensemble_id):
        """Возвращает события по коллективу"""
        return self.filter(ensembles__id=ensemble_id).order_by('date', 'time')
    
    def search(self, query):
        """Поиск событий по названию и описанию"""
        return self.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).order_by('date', 'time')

# Менеджер для News
class NewsManager(models.Manager):
    def published(self):
        """Возвращает только опубликованные новости"""
        return self.filter(is_published=True).order_by('-published_at')
    
    def by_category(self, category):
        """Возвращает новости по категории"""
        return self.published().filter(category=category)
    
    def recent(self, limit=5):
        """Возвращает последние новости"""
        return self.published()[:limit]
    
    def search(self, query):
        """Поиск новостей по заголовку и содержанию"""
        return self.published().filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    def by_author(self, author):
        """Возвращает новости по автору"""
        return self.published().filter(author=author)

# Место проведения
class Venue(models.Model):
    name = models.CharField("Название места", max_length=255)
    description = models.TextField("Описание", blank=True)
    address = models.CharField("Адрес", max_length=500)

    def __str__(self):
        return self.name

# Фестиваль
class Festival(models.Model):
    name = models.CharField("Название фестиваля", max_length=255)
    date = models.DateField("Дата проведения")
    description = models.TextField("Описание фестиваля", blank=True)

    def __str__(self):
        return self.name

# Коллектив
class Ensemble(models.Model):
    name = models.CharField("Название коллектива", max_length=255)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.name

# Событие
class Event(models.Model):
    category = models.CharField(
        "Категория",
        max_length=50,
        choices=EventCategory.choices
    )
    name = models.CharField("Название события", max_length=255, unique=True)
    date = models.DateField("Дата")
    time = models.TimeField("Время")
    price = models.CharField("Цена", max_length=50)
    description = models.TextField("Описание события")
    ticket_url = models.CharField("Купить билет", max_length=500, blank=True, null=True) # Добавил blank/null, если поле может быть пустым
    image = models.ImageField("Изображение", upload_to="events/", blank=True, null=True) # Добавил blank/null
    ensembles = models.ManyToManyField(Ensemble, verbose_name="Коллектив", blank=True) # Добавил blank=True
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Место проведения") # Добавил blank=True
    
    # Связь с пользователем, создавшим событие
    created_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Создатель события",
        null=True,
        blank=True
    )

    # НОВОЕ ПОЛЕ: slug
    slug = models.SlugField(unique=True, max_length=255, blank=True) # Добавляем slug

    # Менеджер
    objects = EventManager()

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ['date', 'time'] # Порядок по умолчанию

    def __str__(self):
        return self.name

    # НОВЫЙ МЕТОД: Сохранение slug при сохранении объекта
    def save(self, *args, **kwargs):
        if not self.slug: # Если slug еще не заполнен
            # Генерируем slug из названия события
            # Добавляем дату к названию, чтобы slug был уникален, если названия событий повторяются в разные даты
            base_slug = slugify(self.name)
            # Добавляем год-месяц-день к slug для лучшей уникальности
            date_suffix = self.date.strftime('-%Y-%m-%d') if self.date else ''
            self.slug = f"{base_slug}{date_suffix}"

            # Проверяем уникальность slug. Если такой slug уже есть, добавляем счетчик
            original_slug = self.slug
            counter = 1
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        """Проверяет, является ли событие предстоящим"""
        today = date.today()
        now = datetime.now().time()
        return (self.date > today) or (self.date == today and self.time >= now)
    
    @property
    def is_today(self):
        """Проверяет, происходит ли событие сегодня"""
        return self.date == date.today()
    
    @property
    def is_past(self):
        """Проверяет, является ли событие прошедшим"""
        today = date.today()
        now = datetime.now().time()
        return (self.date < today) or (self.date == today and self.time < now)

# Новостная модель
class News(models.Model):
    title = models.CharField("Заголовок новости", max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    category = models.CharField(
        "Категория",
        max_length=20,
        choices=NewsCategory.choices,
        default=NewsCategory.GENERAL
    )
    content = models.TextField("Содержание новости")
    excerpt = models.TextField("Краткое описание", max_length=500, blank=True)
    image = models.ImageField("Изображение", upload_to="news/", blank=True, null=True)
    author = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        verbose_name="Автор",
        null=True,
        blank=True
    )
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    # Менеджер
    objects = NewsManager()

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            original_slug = self.slug
            counter = 1
            while News.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:news_detail', kwargs={'slug': self.slug})
    
    @property
    def reading_time(self):
        """Примерное время чтения новости (в минутах)"""
        words_per_minute = 200
        word_count = len(self.content.split())
        minutes = max(1, word_count // words_per_minute)
        return minutes
