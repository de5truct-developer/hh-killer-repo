from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SeekerProfile, EmployerProfile, Skill, LOCATION_CHOICES, EXPERIENCE_CHOICES, EDUCATION_LEVEL_CHOICES, INSTITUTION_CHOICES


class SeekerRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}))
    first_name = forms.CharField(label='Имя', max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(label='Фамилия', max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), required=False, label='Навыки',
        widget=forms.CheckboxSelectMultiple
    )
    profession = forms.CharField(label='Специальность (Должность)', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Frontend-разработчик'}))
    experience_level = forms.ChoiceField(label='Уровень опыта', choices=EXPERIENCE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    location = forms.ChoiceField(label='Город', choices=LOCATION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    desired_salary = forms.IntegerField(label='Желаемая зарплата (₸)', required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '200000'}))
    experience = forms.CharField(label='Где вы работали и что делали?', required=False,
                                 widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите ваш опыт работы...'}))
    education_level = forms.ChoiceField(label='Уровень образования', choices=EDUCATION_LEVEL_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    institution = forms.ChoiceField(label='Учебное заведение', choices=[('', 'Не выбрано')] + INSTITUTION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    photo = forms.ImageField(label='Фото профиля', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['password1', 'password2']:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.role = User.ROLE_SEEKER
        if commit:
            user.save()
            profile = SeekerProfile.objects.create(
                user=user,
                profession=self.cleaned_data.get('profession', ''),
                experience=self.cleaned_data.get('experience', ''),
                experience_level=self.cleaned_data.get('experience_level', ''),
                location=self.cleaned_data.get('location', ''),
                desired_salary=self.cleaned_data.get('desired_salary'),
                education_level=self.cleaned_data.get('education_level', ''),
                institution=self.cleaned_data.get('institution', ''),
                photo=self.cleaned_data.get('photo'),
            )
            skills = self.cleaned_data.get('skills')
            if skills:
                profile.skills.set(skills)
        return user


class EmployerRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'hr@company.com'}))
    company_name = forms.CharField(label='Название компании', max_length=200,
                                   widget=forms.TextInput(attrs={'placeholder': 'ТОО «Компания»'}))
    description = forms.CharField(label='Описание компании', required=False,
                                  widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Расскажите о компании...'}))
    website = forms.URLField(label='Сайт', required=False,
                             widget=forms.URLInput(attrs={'placeholder': 'https://company.kz'}))
    location = forms.ChoiceField(label='Город', choices=LOCATION_CHOICES, required=False)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.role = User.ROLE_EMPLOYER
        if commit:
            user.save()
            EmployerProfile.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name', ''),
                description=self.cleaned_data.get('description', ''),
                website=self.cleaned_data.get('website', ''),
                location=self.cleaned_data.get('location', ''),
            )
        return user


class SeekerProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), required=False, label='Навыки',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = SeekerProfile
        fields = ('photo', 'profession', 'bio', 'education_level', 'institution', 'education', 'interests', 'experience', 'experience_level', 'location', 'phone', 'desired_salary', 'skills')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Расскажите о себе...'}),
            'education': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Дополнительная информация об образовании...'}),
            'experience': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (777) 000-00-00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'skills':
                self.fields[field].widget.attrs['class'] = 'form-control'


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'description', 'website', 'location', 'phone', 'logo')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'website': forms.URLInput(attrs={'placeholder': 'https://'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (727) 000-00-00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class SkillCreateForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Новый навык...'}),
        }
