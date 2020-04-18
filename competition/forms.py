from django import forms


class RegistrationForm(forms.Form):
    nickname = forms.CharField(label='Přezdívka', max_length=255)


class AnswerForm(forms.Form):
    answer = forms.CharField(label='Odpověď')