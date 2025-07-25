from django import forms
from .models import Event, Ensemble, Venue

class ContactForm(forms.Form):
    name = forms.CharField(label="Ваше имя", max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Введите ваше имя'}))
    email = forms.EmailField(label="Ваш Email",
                             widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}))
    phone = forms.CharField(label="Номер телефона (необязательно)", max_length=20, required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Введите ваш телефон (необязательно)'}))
    message = forms.CharField(label="Сообщение", widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите ваше сообщение здесь'}))

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