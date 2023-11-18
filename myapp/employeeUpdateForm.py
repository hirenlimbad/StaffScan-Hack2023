from django import forms

POSITION_CHOICES = [
    ('senior_developer', 'Senior Manager'),
    ('junior_developer', 'Junior Manager'),
    ('manager', 'Manager'),
]
class EmployeeUpdateForm(forms.Form):
    id = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=100, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    education = forms.CharField(max_length=25, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    position = forms.ChoiceField(choices=POSITION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    salary = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))