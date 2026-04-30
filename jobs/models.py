from django.db import models
from users.models import User, Skill, LOCATION_CHOICES, EXPERIENCE_CHOICES, EDUCATION_LEVEL_CHOICES


class Vacancy(models.Model):
    EMPLOYMENT_CHOICES = [
        ('full', 'Полная занятость'),
        ('part', 'Частичная занятость'),
        ('remote', 'Удалённая работа'),
        ('contract', 'Контракт'),
        ('internship', 'Стажировка'),
    ]

    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=200, verbose_name='Название вакансии')
    description = models.TextField(verbose_name='Описание')
    salary_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='Зарплата от')
    salary_max = models.PositiveIntegerField(null=True, blank=True, verbose_name='Зарплата до')
    skills_required = models.ManyToManyField(Skill, blank=True, related_name='vacancies',
                                             verbose_name='Требуемые навыки')
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True, verbose_name='Опыт')
    education_required = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, blank=True, verbose_name='Требуемое образование')
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True, verbose_name='Город')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES,
                                       default='full', verbose_name='Тип занятости')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return f'{self.title} — {self.get_company_name()}'

    def get_company_name(self):
        try:
            return self.employer.employerprofile.company_name
        except Exception:
            return self.employer.email

    def get_salary_display(self):
        if self.salary_min and self.salary_max:
            return f'{self.salary_min:,} – {self.salary_max:,} ₸'
        elif self.salary_min:
            return f'от {self.salary_min:,} ₸'
        elif self.salary_max:
            return f'до {self.salary_max:,} ₸'
        return 'Не указана'


class Application(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_VIEWED = 'viewed'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'На рассмотрении'),
        (STATUS_VIEWED, 'Просмотрено'),
        (STATUS_ACCEPTED, 'Принято'),
        (STATUS_REJECTED, 'Отклонено'),
    ]

    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    match_score = models.PositiveIntegerField(default=0, verbose_name='Совпадение (%)')
    cover_letter = models.TextField(blank=True, verbose_name='Сопроводительное письмо')
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name='Резюме (файл)')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seeker', 'vacancy')
        ordering = ['-applied_at']
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def __str__(self):
        return f'{self.seeker.email} → {self.vacancy.title}'

    def get_status_color(self):
        colors = {
            self.STATUS_PENDING: 'warning',
            self.STATUS_VIEWED: 'info',
            self.STATUS_ACCEPTED: 'success',
            self.STATUS_REJECTED: 'danger',
        }
        return colors.get(self.status, 'secondary')


class SavedVacancy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_vacancies')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vacancy')
        verbose_name = 'Сохранённая вакансия'
        verbose_name_plural = 'Сохранённые вакансии'

class ApplicationMessage(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение в чате'
        verbose_name_plural = 'Сообщения в чате'

    def __str__(self):
        return f'Message from {self.sender.email} in App {self.application.id}'
