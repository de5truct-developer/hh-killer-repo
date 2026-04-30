from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vacancy, Application, SavedVacancy
from .forms import VacancyForm, ApplicationForm, VacancyFilterForm, ApplicationMessageForm
from .matching import (get_recommended_vacancies, get_match_for_user_vacancy,
                       get_recommended_candidates, get_score_color)
from users.models import SeekerProfile, Notification
from django.urls import reverse


def home(request):
    recent_vacancies = Vacancy.objects.filter(is_active=True).select_related('employer')[:6]
    stats = {
        'vacancies': Vacancy.objects.filter(is_active=True).count(),
        'companies': Vacancy.objects.values('employer').distinct().count(),
        'seekers': SeekerProfile.objects.count(),
    }
    recommended = []
    if request.user.is_authenticated and request.user.is_seeker:
        all_active = Vacancy.objects.filter(is_active=True).prefetch_related('skills_required')
        recommended = get_recommended_vacancies(request.user, all_active, min_score=1, limit=3)
    return render(request, 'home.html', {
        'recent_vacancies': recent_vacancies,
        'stats': stats,
        'recommended': recommended,
    })


def vacancy_list(request):
    form = VacancyFilterForm(request.GET)
    vacancies = Vacancy.objects.filter(is_active=True).prefetch_related('skills_required').select_related('employer')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        location = form.cleaned_data.get('location')
        employment_type = form.cleaned_data.get('employment_type')
        salary_min = form.cleaned_data.get('salary_min')
        skill = form.cleaned_data.get('skill')

        if q:
            vacancies = vacancies.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(employer__employerprofile__company_name__icontains=q)
            )
        if location:
            vacancies = vacancies.filter(location__icontains=location)
        if employment_type:
            vacancies = vacancies.filter(employment_type=employment_type)
        if salary_min:
            vacancies = vacancies.filter(
                Q(salary_min__gte=salary_min) | Q(salary_max__gte=salary_min)
            )
        if skill:
            vacancies = vacancies.filter(skills_required=skill)

    # Attach match scores for seekers
    scored_vacancies = []
    applied_ids = set()
    saved_ids = set()

    if request.user.is_authenticated and request.user.is_seeker:
        applied_ids = set(Application.objects.filter(seeker=request.user).values_list('vacancy_id', flat=True))
        saved_ids = set(SavedVacancy.objects.filter(user=request.user).values_list('vacancy_id', flat=True))
        for v in vacancies:
            score = get_match_for_user_vacancy(request.user, v)
            scored_vacancies.append({
                'vacancy': v,
                'score': score,
                'score_color': get_score_color(score),
                'applied': v.id in applied_ids,
                'saved': v.id in saved_ids,
            })
        scored_vacancies.sort(key=lambda x: x['score'], reverse=True)
    else:
        for v in vacancies:
            scored_vacancies.append({
                'vacancy': v,
                'score': None,
                'score_color': '',
                'applied': False,
                'saved': False,
            })

    return render(request, 'jobs/vacancy_list.html', {
        'vacancies': scored_vacancies,
        'filter_form': form,
        'total': vacancies.count(),
    })


def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)
    vacancy.views_count += 1
    vacancy.save(update_fields=['views_count'])

    score = None
    applied = False
    saved = False
    candidates = []
    app_form = None

    if request.user.is_authenticated:
        if request.user.is_seeker:
            score = get_match_for_user_vacancy(request.user, vacancy)
            applied = Application.objects.filter(seeker=request.user, vacancy=vacancy).exists()
            saved = SavedVacancy.objects.filter(user=request.user, vacancy=vacancy).exists()
            if not applied:
                app_form = ApplicationForm()
        elif request.user.is_employer and request.user == vacancy.employer:
            all_seekers = SeekerProfile.objects.prefetch_related('skills').select_related('user')
            candidates = get_recommended_candidates(vacancy, all_seekers, min_score=1, limit=10)

    return render(request, 'jobs/vacancy_detail.html', {
        'vacancy': vacancy,
        'score': score,
        'score_color': get_score_color(score) if score is not None else '',
        'applied': applied,
        'saved': saved,
        'app_form': app_form,
        'candidates': candidates,
    })


@login_required
def apply_vacancy(request, pk):
    if not request.user.is_seeker:
        messages.error(request, 'Только соискатели могут откликаться на вакансии.')
        return redirect('vacancy_detail', pk=pk)

    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)

    if Application.objects.filter(seeker=request.user, vacancy=vacancy).exists():
        messages.warning(request, 'Вы уже откликались на эту вакансию.')
        return redirect('vacancy_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            score = get_match_for_user_vacancy(request.user, vacancy)
            app = form.save(commit=False)
            app.seeker = request.user
            app.vacancy = vacancy
            app.match_score = score
            app.save()
            
            Notification.objects.create(
                user=vacancy.employer,
                message=f'Новый отклик на вакансию "{vacancy.title}" от {request.user.get_full_name() or request.user.email} (Совпадение: {score}%).',
                link=reverse('vacancy_applications', args=[vacancy.pk])
            )
            
            messages.success(request, f'Отклик отправлен! Совпадение навыков: {score}%')
            return redirect('my_applications')
    return redirect('vacancy_detail', pk=pk)


@login_required
def my_applications(request):
    if not request.user.is_seeker:
        return redirect('home')
    applications = Application.objects.filter(seeker=request.user).select_related('vacancy')
    return render(request, 'jobs/my_applications.html', {'applications': applications})


@login_required
def create_vacancy(request):
    if not request.user.is_employer:
        messages.error(request, 'Только работодатели могут создавать вакансии.')
        return redirect('home')
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.employer = request.user
            vacancy.save()
            form.save_m2m()
            new_skill = form.cleaned_data.get('new_skill', '').strip()
            if new_skill:
                from users.models import Skill
                skill, _ = Skill.objects.get_or_create(name=new_skill)
                vacancy.skills_required.add(skill)
            messages.success(request, 'Вакансия успешно создана!')
            return redirect('vacancy_detail', pk=vacancy.pk)
    else:
        form = VacancyForm()
    return render(request, 'jobs/create_vacancy.html', {'form': form})


@login_required
def edit_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, employer=request.user)
    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вакансия обновлена!')
            return redirect('vacancy_detail', pk=pk)
    else:
        form = VacancyForm(instance=vacancy)
    return render(request, 'jobs/create_vacancy.html', {'form': form, 'edit': True, 'vacancy': vacancy})


@login_required
def delete_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, employer=request.user)
    if request.method == 'POST':
        vacancy.delete()
        messages.success(request, 'Вакансия удалена.')
        return redirect('employer_profile')
    return render(request, 'jobs/confirm_delete.html', {'vacancy': vacancy})


@login_required
def toggle_save_vacancy(request, pk):
    if not request.user.is_seeker:
        return redirect('vacancy_detail', pk=pk)
    vacancy = get_object_or_404(Vacancy, pk=pk)
    obj, created = SavedVacancy.objects.get_or_create(user=request.user, vacancy=vacancy)
    if not created:
        obj.delete()
        messages.info(request, 'Убрано из избранного.')
    else:
        messages.success(request, 'Добавлено в избранное!')
    return redirect('vacancy_detail', pk=pk)


@login_required
def saved_vacancies(request):
    if not request.user.is_seeker:
        return redirect('home')
    saved = SavedVacancy.objects.filter(user=request.user).select_related('vacancy')
    return render(request, 'jobs/saved_vacancies.html', {'saved': saved})


@login_required
def vacancy_applications(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, employer=request.user)
    applications = Application.objects.filter(vacancy=vacancy).select_related('seeker')
    return render(request, 'jobs/vacancy_applications.html', {
        'vacancy': vacancy,
        'applications': applications,
    })


@login_required
def update_application_status(request, pk):
    app = get_object_or_404(Application, pk=pk, vacancy__employer=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            app.status = new_status
            app.save()
            
            status_msg = dict(Application.STATUS_CHOICES).get(new_status).lower()
            Notification.objects.create(
                user=app.seeker,
                message=f'Статус вашего отклика на вакансию "{app.vacancy.title}" изменён на "{status_msg}".',
                link=reverse('my_applications')
            )
            
            messages.success(request, 'Статус обновлён.')
    return redirect('vacancy_applications', pk=app.vacancy_id)


def recommendations(request):
    if not request.user.is_authenticated or not request.user.is_seeker:
        return redirect('vacancy_list')
    all_active = Vacancy.objects.filter(is_active=True).prefetch_related('skills_required')
    recommended = get_recommended_vacancies(request.user, all_active, min_score=1, limit=20)
    return render(request, 'jobs/recommendations.html', {'recommended': recommended})

@login_required
def application_chat(request, pk):
    app = get_object_or_404(Application, pk=pk)
    
    # Check permissions
    if not (request.user == app.seeker or request.user == app.vacancy.employer):
        messages.error(request, 'У вас нет доступа к этому чату.')
        return redirect('home')

    messages_list = app.messages.all()
    
    if request.method == 'POST':
        form = ApplicationMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.application = app
            msg.sender = request.user
            msg.save()
            
            # Notify the other party
            other_user = app.vacancy.employer if request.user == app.seeker else app.seeker
            Notification.objects.create(
                user=other_user,
                message=f'Новое сообщение в чате по вакансии "{app.vacancy.title}" от {request.user.get_full_name() or request.user.email}',
                link=reverse('application_chat', args=[app.pk])
            )
            return redirect('application_chat', pk=app.pk)
    else:
        form = ApplicationMessageForm()

    return render(request, 'jobs/chat.html', {
        'application': app,
        'messages_list': messages_list,
        'form': form,
    })
