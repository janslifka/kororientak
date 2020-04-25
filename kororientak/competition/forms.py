from django import forms


class RegistrationForm(forms.Form):
    name = forms.CharField(label='Tvoje jméno', max_length=255)
    category = forms.ChoiceField(label='Kategorie', choices=(), widget=forms.RadioSelect)

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = choices
