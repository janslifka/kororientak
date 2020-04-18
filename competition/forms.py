from django import forms

CATEGORIES = [('V', 'Výletník'),
              ('B', 'Běžec')]


class RegistrationForm(forms.Form):
    nickname = forms.CharField(label='Tvoje přezdívka', max_length=255)
    category = forms.ChoiceField(label='Kategorie', choices=CATEGORIES, widget=forms.RadioSelect)
