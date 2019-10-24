from django import forms


class TeamForm(forms.Form):
    teamname = forms.CharField(label="队名", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

class updateName(forms.Form):
    teamname = forms.CharField(label="队名", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                        'placeholder': '请输入新的队名'}))
