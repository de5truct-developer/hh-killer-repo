from django import forms
from .models import Vacancy, Application, ApplicationMessage
from users.models import Skill, LOCATION_CHOICES, EXPERIENCE_CHOICES

class VacancyForm(forms.ModelForm):
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), required=False, label='Требуемые навыки',
        widget=forms.CheckboxSelectMultiple
    )
    new_skill = forms.CharField(required=False, label='Добавить навык',
                                widget=forms.TextInput(attrs={'placeholder': 'Введите новый навык...'}))

    class Meta:
        model = Vacancy
        fields = ('title', 'description', 'salary_min', 'salary_max',
                  'employment_type', 'experience_required', 'education_required', 'location', 'skills_required')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Python-разработчик'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Опишите обязанности, требования...'}),
            'salary_min': forms.NumberInput(attrs={'placeholder': '150000'}),
            'salary_max': forms.NumberInput(attrs={'placeholder': '300000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'skills_required':
                self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        vacancy = super().save(commit=False)
        if commit:
            vacancy.save()
            self.save_m2m()
            new_skill_name = self.cleaned_data.get('new_skill', '').strip()
            if new_skill_name:
                skill, _ = Skill.objects.get_or_create(name=new_skill_name)
                vacancy.skills_required.add(skill)
        return vacancy


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('cover_letter', 'resume_file')
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Расскажите, почему вы подходите для этой вакансии...',
            }),
            'resume_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'cover_letter': 'Сопроводительное письмо (необязательно)',
            'resume_file': 'Резюме (файл PDF/DOC, необязательно)',
        }

class ApplicationMessageForm(forms.ModelForm):
    class Meta:
        model = ApplicationMessage
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите сообщение...',
                'autocomplete': 'off',
            }),
        }
        labels = {'text': ''}


class VacancyFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Поиск',
                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Должность, компания...'}))
    location = forms.ChoiceField(
        required=False, label='Город',
        choices=[('', 'Любой город')] + LOCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    employment_type = forms.ChoiceField(
        required=False, label='Тип занятости',
        choices=[('', 'Все')] + list(Vacancy.EMPLOYMENT_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    salary_min = forms.IntegerField(required=False, label='Зарплата от',
                                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    skill = forms.ModelChoiceField(queryset=Skill.objects.all(), required=False,
                                   label='Навык', empty_label='Любой навык',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
