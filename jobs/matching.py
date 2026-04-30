"""
Advanced matching algorithm: compares seeker profile vs vacancy.
Factors: Skills (60%), Location (20%), Salary (20%).
Returns match percentage (0-100).
"""
from users.models import SeekerProfile

def calculate_advanced_match(profile, vacancy) -> int:
    score = 0
    
    # 1. Skills (60% weight)
    seeker_skills = set(profile.skills.values_list('name', flat=True))
    vacancy_skills = set(vacancy.skills_required.values_list('name', flat=True))
    
    if not vacancy_skills:
        score += 60  # No requirements = perfect match for skills
    elif seeker_skills:
        seeker_norm = {s.lower().strip() for s in seeker_skills}
        vacancy_norm = {s.lower().strip() for s in vacancy_skills}
        matched = seeker_norm & vacancy_norm
        score += int((len(matched) / len(vacancy_norm)) * 60)

    # 2. Location (20% weight)
    # If remote or no specific location required, give 20.
    if vacancy.employment_type == 'remote' or not vacancy.location:
        score += 20
    elif profile.location and vacancy.location:
        # Match exact or partial (e.g. "Almaty" in "Almaty, Kazakhstan")
        v_loc = vacancy.location.lower().strip()
        p_loc = profile.location.lower().strip()
        if v_loc in p_loc or p_loc in v_loc:
            score += 20
        else:
            score += 0 # Different cities
    else:
        # If vacancy has location but seeker doesn't, give 10 (neutral)
        score += 10

    # 3. Salary (20% weight)
    if not profile.desired_salary:
        score += 20  # Seeker didn't specify -> no conflict
    else:
        ds = profile.desired_salary
        if vacancy.salary_max and ds <= vacancy.salary_max:
            score += 20
        elif vacancy.salary_min and ds <= vacancy.salary_min:
            score += 20
        elif vacancy.salary_min and ds <= vacancy.salary_min * 1.3:
            score += 10 # slightly above min, but reasonable
        elif vacancy.salary_max is None and vacancy.salary_min is None:
            score += 20 # Vacancy didn't specify -> no conflict
        else:
            score += 0 # Too expensive

    # 4. Experience (10 points)
    if vacancy.experience_required:
        if profile.experience_level:
            v_exp = vacancy.experience_required
            p_exp = profile.experience_level
            
            exp_levels = {'no_experience': 0, '1_3_years': 1, '3_6_years': 2, 'more_6_years': 3}
            if exp_levels.get(p_exp, 0) >= exp_levels.get(v_exp, 0):
                score += 10
            else:
                score += 0 # not enough experience
        else:
            score += 0 # no experience level provided
    else:
        # No experience required -> free points
        score += 10

    # 5. Education (10 points)
    if vacancy.education_required:
        if profile.education_level:
            v_edu = vacancy.education_required
            p_edu = profile.education_level
            
            edu_levels = {'secondary': 0, 'secondary_special': 1, 'incomplete_higher': 2, 'higher': 3}
            if edu_levels.get(p_edu, 0) >= edu_levels.get(v_edu, 0):
                score += 10
            else:
                score += 0 # lower education level
        else:
            score += 0
    else:
        score += 10

    # Normalize score to 100 max (max is 60+20+20+10+10 = 120)
    score = min(int((score / 120) * 100), 100)
    return score


def get_match_for_user_vacancy(user, vacancy):
    """Calculate match score between a seeker user and a vacancy."""
    try:
        profile = SeekerProfile.objects.get(user=user)
        return calculate_advanced_match(profile, vacancy)
    except SeekerProfile.DoesNotExist:
        return 0


def get_recommended_vacancies(user, vacancies_qs, min_score=30, limit=10):
    """
    Returns list of (vacancy, score) sorted by score descending.
    Filters vacancies with score >= min_score.
    """
    try:
        profile = SeekerProfile.objects.get(user=user)
    except SeekerProfile.DoesNotExist:
        return []

    scored = []
    for vacancy in vacancies_qs:
        score = calculate_advanced_match(profile, vacancy)
        if score >= min_score:
            scored.append((vacancy, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def get_recommended_candidates(vacancy, seekers_qs, min_score=30, limit=10):
    """
    For an employer: returns list of (seeker_profile, score) sorted by score.
    """
    scored = []
    for profile in seekers_qs:
        score = calculate_advanced_match(profile, vacancy)
        if score >= min_score:
            scored.append((profile, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def get_score_color(score: int) -> str:
    """Return CSS class based on score."""
    if score >= 75:
        return 'success'
    elif score >= 50:
        return 'warning'
    return 'danger'
