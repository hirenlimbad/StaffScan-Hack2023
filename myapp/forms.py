from django import forms

class EmployeeForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    education = forms.CharField(max_length=25, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    position = forms.CharField(max_length=25, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    salary = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    faceImage = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    
class AssignTaskForm(forms.Form):

    employee_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'}),
        required=False
    )
    employee_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Name'})
    )
    task_header = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Header'})
    )
    task_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Task Description'})
    )
    deadline = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )
