from django import forms
from .models import Exercise, ExerciseSet,  WorkoutPlan, PlanDay, PlanExercise, BMIRecord
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class ExerciseForm(forms.Form):
    exercise_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Bench Press',
            'id': 'exerciseName'
        })
    )
    sets_count = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 9)],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'setsCount',
            'onchange': 'generateSetInputs()'
        }),
        initial=''
    )

class SetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        sets_count = kwargs.pop('sets_count', 1)
        super().__init__(*args, **kwargs)
        
        for i in range(1, sets_count + 1):
            self.fields[f'reps_{i}'] = forms.IntegerField(
                min_value=1,
                widget=forms.NumberInput(attrs={
                    'class': 'set-input',
                    'placeholder': 'Reps',
                    'id': f'reps_{i}'
                })
            )
            self.fields[f'weight_{i}'] = forms.DecimalField(
                min_value=0,
                decimal_places=2,
                widget=forms.NumberInput(attrs={
                    'class': 'set-input',
                    'placeholder': 'Weight (kg)',
                    'step': '0.5',
                    'id': f'weight_{i}'
                })
            )


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        


class BMICalculatorForm(forms.ModelForm):
    weight = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter weight in kg',
            'class': 'form-control',
            'step': '0.1'
        })
    )
    height = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter height in cm',
            'class': 'form-control',
            'step': '0.1'
        })
    )
    
    class Meta:
        model = BMIRecord
        fields = ['weight', 'height']



from django import forms
from .models import WorkoutPlan, PlanDay, PlanExercise

class WorkoutPlanForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Push Pull Legs, Full Body Split',
            'required': True
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Brief description of your workout plan...',
            'rows': 3
        })
    )
    
    class Meta:
        model = WorkoutPlan
        fields = ['name', 'description']

class PlanDayForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control day-name-input',
            'placeholder': 'e.g., Monday: Push Day, Workout A',
            'required': True
        })
    )
    
    class Meta:
        model = PlanDay
        fields = ['name']