from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import SeekerRegisterForm, EmployerRegisterForm, SeekerProfileForm, EmployerProfileForm
from .models import User, SeekerProfile, EmployerProfile, Skill, Notification
from jobs.models import Vacancy, Application


def register_choice(request):
    return render(request, 'users/register_choice.html')


def register_seeker(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SeekerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать! Ваш профиль создан.')
            return redirect('seeker_profile')
    else:
        form = SeekerRegisterForm()
    return render(request, 'users/register_seeker.html', {'form': form})


def register_employer(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = EmployerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать! Профиль компании создан.')
            return redirect('employer_profile')
    else:
        form = EmployerRegisterForm()
    return render(request, 'users/register_employer.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'С возвращением, {user.first_name or user.email}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


@login_required
def seeker_profile(request):
    if not request.user.is_seeker:
        return redirect('employer_profile')
    profile, _ = SeekerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = SeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('seeker_profile')
    else:
        form = SeekerProfileForm(instance=profile)
    applications = Application.objects.filter(seeker=request.user).select_related('vacancy')
    return render(request, 'users/seeker_profile.html', {
        'form': form,
        'profile': profile,
        'applications': applications,
    })


@login_required
def employer_profile(request):
    if not request.user.is_employer:
        return redirect('seeker_profile')
    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.email}
    )
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль компании обновлён!')
            return redirect('employer_profile')
    else:
        form = EmployerProfileForm(instance=profile)
    vacancies = Vacancy.objects.filter(employer=request.user)
    return render(request, 'users/employer_profile.html', {
        'form': form,
        'profile': profile,
        'vacancies': vacancies,
    })


def public_seeker_profile(request, pk):
    user = get_object_or_404(User, pk=pk, role=User.ROLE_SEEKER)
    profile = get_object_or_404(SeekerProfile, user=user)
    return render(request, 'users/public_seeker.html', {'profile': profile, 'seeker': user})


def public_employer_profile(request, pk):
    user = get_object_or_404(User, pk=pk, role=User.ROLE_EMPLOYER)
    profile = get_object_or_404(EmployerProfile, user=user)
    vacancies = Vacancy.objects.filter(employer=user, is_active=True)
    return render(request, 'users/public_employer.html', {
        'profile': profile,
        'employer': user,
        'vacancies': vacancies,
    })

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'users/notifications.html', {'notifications': notifications})

@login_required
def read_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications_list')

@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications_list')
