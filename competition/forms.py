from django import forms


class RegistrationForm(forms.Form):
    nickname = forms.CharField(label='Tvoje přezdívka', max_length=255)
