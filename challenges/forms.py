from django import forms
from . import models


class flagForm(forms.Form):
    flag = forms.CharField(label="提交flag", max_length=100,widget=forms.TextInput(attrs={'autofocus': ''}))
