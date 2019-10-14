from django import  forms

class TeamForm(forms.Form):
    teamname=forms.CharField(label="队名",max_length=20,widget=forms.TextInput(attrs={'class':'form-control'}))
    #teamcreater=forms.CharField(label='创建人',max_length=10,widget=forms.TextInput(attrs={'class':'form-control'}))
