from django.contrib import admin
from .models import Vacancy, Application, SavedVacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_company', 'location', 'employment_type', 'is_active', 'created_at', 'views_count')
    list_filter = ('is_active', 'employment_type', 'created_at')
    search_fields = ('title', 'employer__employerprofile__company_name', 'location')
    filter_horizontal = ('skills_required',)
    actions = ['deactivate_vacancies', 'activate_vacancies']

    def get_company(self, obj):
        return obj.get_company_name()
    get_company.short_description = 'Компания'

    def deactivate_vacancies(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_vacancies.short_description = 'Деактивировать выбранные'

    def activate_vacancies(self, request, queryset):
        queryset.update(is_active=True)
    activate_vacancies.short_description = 'Активировать выбранные'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'vacancy', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('seeker__email', 'vacancy__title')
    readonly_fields = ('match_score', 'applied_at')


@admin.register(SavedVacancy)
class SavedVacancyAdmin(admin.ModelAdmin):
    list_display = ('user', 'vacancy', 'saved_at')
