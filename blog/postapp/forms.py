from django import forms
from .models import Event, Ensemble, Venue

class ContactForm(forms.Form):
    """
    Форма для страницы контактов.
    """
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(label="Ваш email")
    message = forms.CharField(widget=forms.Textarea, label="Ваше сообщение")


class EventForm(forms.ModelForm):
    ensembles = forms.ModelMultipleChoiceField(
        queryset=Ensemble.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Коллективы"
    )

    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all().order_by('name'),
        empty_label="Выберите площадку",
        label="Место проведения"
    )

    class Meta:
        model = Event
        fields = [
            'name',
            'category',
            'date',
            'time',
            'price',
            'description',
            'ticket_url',
            'image',
            'ensembles',
            'venue'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'name': 'Название события',
            'category': 'Категория',
            'date': 'Дата',
            'time': 'Время',
            'price': 'Цена',
            'description': 'Описание события',
            'ticket_url': 'Ссылка на билет',
            'image': 'Изображение',
        }