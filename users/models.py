from django.contrib.auth.models import AbstractUser
from django.db import models

LOCATION_CHOICES = [
    ('Алматы', 'Алматы'),
    ('Астана', 'Астана'),
    ('Актобе', 'Актобе'),
    ('Шымкент', 'Шымкент'),
    ('Караганда', 'Караганда'),
    ('Другой', 'Другой (Удаленка)'),
]

EXPERIENCE_CHOICES = [
    ('no_experience', 'Нет опыта'),
    ('1_3_years', 'От 1 года до 3 лет'),
    ('3_6_years', 'От 3 до 6 лет'),
    ('more_6_years', 'Более 6 лет'),
]

EDUCATION_LEVEL_CHOICES = [
    ('higher', 'Высшее'),
    ('incomplete_higher', 'Неоконченное высшее'),
    ('secondary_special', 'Средне-специальное'),
    ('secondary', 'Среднее'),
]

INSTITUTION_CHOICES = [
    ('АТТК', 'АТТК (Актюбинский технико-технологический колледж)'),
    ('КазНУ', 'КазНУ им. аль-Фараби'),
    ('ЕНУ', 'ЕНУ им. Л.Н. Гумилева'),
    ('КБТУ', 'Казахстанско-Британский технический университет'),
    ('МУИТ', 'Международный университет информ. технологий'),
    ('АУЭС', 'Алматинский университет энергетики и связи'),
    ('СДУ', 'Университет им. Сулеймана Демиреля'),
    ('other', 'Другое учебное заведение'),
]


class User(AbstractUser):
    ROLE_SEEKER = 'seeker'
    ROLE_EMPLOYER = 'employer'
    ROLE_CHOICES = [
        (ROLE_SEEKER, 'Соискатель'),
        (ROLE_EMPLOYER, 'Работодатель'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SEEKER)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_seeker(self):
        return self.role == self.ROLE_SEEKER

    @property
    def is_employer(self):
        return self.role == self.ROLE_EMPLOYER

    @property
    def profile(self):
        if self.is_seeker:
            return getattr(self, 'seekerprofile', None)
        return getattr(self, 'employerprofile', None)


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class SeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seekerprofile')
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Фото профиля')
    skills = models.ManyToManyField(Skill, blank=True, related_name='seekers')
    profession = models.CharField(max_length=150, blank=True, verbose_name='Специальность / Должность')
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, blank=True, verbose_name='Уровень образования')
    institution = models.CharField(max_length=100, choices=INSTITUTION_CHOICES, blank=True, verbose_name='Учебное заведение')
    education = models.TextField(blank=True, verbose_name='Доп. инфо об образовании')
    interests = models.TextField(blank=True, verbose_name='Интересы')
    experience = models.TextField(blank=True, verbose_name='Опыт работы (описание)')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True, verbose_name='Уровень опыта')
    bio = models.TextField(blank=True, verbose_name='О себе')
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True, verbose_name='Город')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    desired_salary = models.PositiveIntegerField(null=True, blank=True, verbose_name='Желаемая зарплата')

    class Meta:
        verbose_name = 'Профиль соискателя'
        verbose_name_plural = 'Профили соискателей'

    def __str__(self):
        return f'Профиль: {self.user.email}'


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employerprofile')
    company_name = models.CharField(max_length=200, verbose_name='Название компании')
    description = models.TextField(blank=True, verbose_name='Описание компании')
    website = models.URLField(blank=True, verbose_name='Сайт')
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True, verbose_name='Город')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name='employers',
                                             verbose_name='Нужные навыки')

    class Meta:
        verbose_name = 'Профиль работодателя'
        verbose_name_plural = 'Профили работодателей'

    def __str__(self):
        return self.company_name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255, verbose_name='Сообщение')
    link = models.CharField(max_length=255, blank=True, verbose_name='Ссылка')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'{self.user.email}: {self.message}'
