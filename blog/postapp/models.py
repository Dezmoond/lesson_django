from django.db import models
from django.utils.text import slugify

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

    # НОВОЕ ПОЛЕ: slug
    slug = models.SlugField(unique=True, max_length=255, blank=True) # Добавляем slug

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
