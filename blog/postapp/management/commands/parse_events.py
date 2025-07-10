import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.management.base import BaseCommand
from postapp.models import Venue, Event
from django.utils.text import slugify
from django.core.files.base import ContentFile
from urllib.parse import urljoin
import os

RU_MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
}

VENUES_CONFIG = [
    {"id": "filarmoniya", "name": "Филармония", "url": "https://quicktickets.ru/chita-filarmoniya"},
    {"id": "uzory", "name": "Забайкальские узоры", "url": "https://quicktickets.ru/chita-zabajkalskie-uzory"},
    {"id": "rodina", "name": "КЗ Родина", "url": "https://quicktickets.ru/chita-kz-rodina"},
    {"id": "teatr", "name": "Театр Забайкалья", "url": "https://quicktickets.ru/chita-teatr-zabajkale"},
    {"id": "oficerov", "name": "Дом офицеров", "url": "https://quicktickets.ru/chita-dom-oficerov"},
]


def parse_date_string(date_str):
    """Конвертирует строку '15 мая 19:00' в datetime.date и datetime.time"""
    try:
        day_str, month_str, time_str = date_str.split()
        day = int(day_str)
        month = RU_MONTHS[month_str.lower()]
        hour, minute = map(int, time_str.split(":"))
        now = datetime.now()
        event_date = datetime(now.year, month, day, hour, minute)
        return event_date.date(), event_date.time()
    except Exception as e:
        print(f"Ошибка парсинга даты '{date_str}': {e}")
        return None, None


def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content, name=os.path.basename(url))
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
    return None


def parse_single_venue(venue_conf):
    events = []

    try:
        response = requests.get(venue_conf["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        for event_div in soup.find_all("div", class_="elem"):
            title_tag = event_div.find("span", class_="underline")
            title = title_tag.get_text(strip=True) if title_tag else "Без названия"

            description_tag = event_div.find("div", class_="d")
            description = description_tag.get_text(strip=True) if description_tag else "Без описания"

            # Даты
            dates = []
            sessions = event_div.find("div", class_="sessions")
            if sessions:
                dates = [d.get_text(strip=True) for d in sessions.find_all("span", class_="underline")]

            # Ссылка на билеты
            ticket_tag = event_div.find("p", class_="b")
            ticket_url = ""
            if ticket_tag and ticket_tag.find("a"):
                ticket_url = urljoin("https://quicktickets.ru", ticket_tag.find("a")["href"])

            # Изображение
            img_tag = event_div.find("img", class_="polaroid")
            image_url = img_tag["src"] if img_tag and img_tag.get("src") else ""

            events.append({
                "title": title,
                "description": description,
                "dates": dates,
                "ticket_link": ticket_url,
                "image_url": image_url,
                "venue": venue_conf
            })

    except Exception as e:
        print(f"Ошибка при парсинге {venue_conf['url']}: {e}")

    return events


class Command(BaseCommand):
    help = "Парсит события с quicktickets и сохраняет их в базу Django"

    def handle(self, *args, **kwargs):
        for venue_conf in VENUES_CONFIG:
            venue_name = venue_conf["name"]

            # Найти или создать Venue
            venue, _ = Venue.objects.get_or_create(
                name=venue_name,
                defaults={"address": "", "description": ""}
            )

            events = parse_single_venue(venue_conf)
            for event in events:
                for date_str in event["dates"]:
                    event_date, event_time = parse_date_string(date_str)
                    if not event_date:
                        continue

                    # Уникальность по названию и дате
                    name_with_date = f"{event['title']} ({event_date})"
                    if Event.objects.filter(name=name_with_date).exists():
                        continue

                    image_file = download_image(event["image_url"])

                    Event.objects.create(
                        category="концерт",  # или классифицировать автоматически
                        name=name_with_date,
                        date=event_date,
                        time=event_time,
                        price="",
                        description=event["description"],
                        ticket_url=event["ticket_link"],
                        image=image_file if image_file else None,
                        venue=venue
                    )

            self.stdout.write(self.style.SUCCESS(f"Обработано место: {venue_name}"))
