from django import forms

from .models import Race


class RegistrationForm(forms.Form):
    name = forms.CharField(label='Jméno', max_length=255)
    category = forms.ChoiceField(label='Kategorie', choices=(), widget=forms.RadioSelect)

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = choices


class TaskImportForm(forms.Form):
    race = forms.ModelChoiceField(Race.objects.all(), label='Závod')
    csv_file = forms.FileField(label='CSV tabulka')
