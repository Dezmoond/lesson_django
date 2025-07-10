from django.db import models

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
    ticket_url = models.CharField("Купить билет", max_length=500)
    image = models.ImageField("Изображение", upload_to="events/", blank=True)
    ensembles = models.ManyToManyField(Ensemble, verbose_name="Коллектив")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, verbose_name="Место проведения")
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Фестиваль")

    def __str__(self):
        return f"{self.name} ({self.date})"
