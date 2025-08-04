from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import re

register = template.Library()

@register.filter
def format_price(value):
    """
    Форматирует цену в читаемом виде
    Пример: "1000 руб" -> "1 000 ₽"
    """
    if not value:
        return "Цена не указана"
    
    # Ищем числа в строке
    numbers = re.findall(r'\d+', str(value))
    if numbers:
        number = int(numbers[0])
        # Форматируем число с пробелами
        formatted_number = "{:,}".format(number).replace(',', ' ')
        
        # Заменяем число в исходной строке
        result = re.sub(r'\d+', formatted_number, str(value))
        
        # Заменяем "руб" на символ рубля
        result = result.replace('руб', '₽').replace('руб.', '₽')
        # Убираем лишние точки
        result = result.replace('₽.', '₽')
        
        return result
    
    return value

@register.filter
def format_date_range(start_date, end_date):
    """
    Форматирует диапазон дат
    """
    if not start_date and not end_date:
        return ""
    elif not start_date:
        return end_date.strftime("%d.%m.%Y")
    elif not end_date:
        return start_date.strftime("%d.%m.%Y")
    
    if start_date == end_date:
        return start_date.strftime("%d.%m.%Y")
    else:
        return f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"

@register.filter
def truncate_words_smart(value, arg):
    """
    Умное обрезание текста по словам с сохранением целостности предложений
    """
    if not value:
        return ""
    
    try:
        limit = int(arg)
    except ValueError:
        return value
    
    words = value.split()
    if len(words) <= limit:
        return value
    
    # Берем первые limit слов
    truncated_words = words[:limit]
    truncated_text = ' '.join(truncated_words)
    
    # Ищем последнее предложение и обрезаем до него
    sentences = truncated_text.split('.')
    if len(sentences) > 1:
        # Убираем последнее неполное предложение
        truncated_text = '.'.join(sentences[:-1]) + '.'
    
    return truncated_text + '...'

@register.filter
def highlight_search(text, search_term):
    """
    Подсвечивает поисковые термины в тексте
    """
    if not search_term or not text:
        return text
    
    # Экранируем специальные символы в поисковом термине
    escaped_term = re.escape(search_term)
    pattern = re.compile(f'({escaped_term})', re.IGNORECASE)
    
    highlighted_text = pattern.sub(r'<mark>\1</mark>', str(text))
    return mark_safe(highlighted_text)

@register.filter
def get_category_color(category):
    """
    Возвращает цвет для категории
    """
    colors = {
        'концерт': 'primary',
        'спектакль': 'success',
        'опера': 'danger',
        'форум': 'warning',
        'концерт старинной музыки': 'info',
        'органный концерт': 'secondary',
        'концерт классической музыки': 'primary',
        'концерт симфонической музыки': 'primary',
        'концерт народной музыки': 'success',
        'театрально музыкальная постановка': 'warning',
        'балет': 'danger',
        'цирк': 'warning',
        'виртуальный концерт': 'info',
        'музыкальная сказка для детей': 'success',
        'шоу программа': 'warning',
        'танцы': 'success',
    }
    return colors.get(category, 'secondary')

@register.filter
def get_news_category_color(category):
    """
    Возвращает цвет для категории новостей
    """
    colors = {
        'общие': 'secondary',
        'культура': 'primary',
        'музыка': 'success',
        'театр': 'danger',
        'фестивали': 'warning',
        'анонсы': 'info',
        'интервью': 'primary',
        'обзоры': 'success',
    }
    return colors.get(category, 'secondary')

@register.simple_tag
def get_event_status(event):
    """
    Возвращает статус события (прошедшее, сегодня, будущее)
    """
    from datetime import date, datetime
    
    today = date.today()
    now = datetime.now().time()
    
    if event.date < today:
        return 'past'
    elif event.date == today:
        if event.time < now:
            return 'past'
        else:
            return 'today'
    else:
        return 'future'

@register.simple_tag
def get_event_status_text(event):
    """
    Возвращает текстовый статус события
    """
    status = get_event_status(event)
    status_texts = {
        'past': 'Прошедшее',
        'today': 'Сегодня',
        'future': 'Предстоящее'
    }
    return status_texts.get(status, 'Неизвестно') 