"""
This file contains the actual "brain" behind career recommendations.
It's plain Python logic - no external AI library - so it's easy to explain
in a viva: we just compare the student's skills/interests against each
career's required skills and score how well they match.
"""
from .models import CareerPath


def recommend_careers(student_skills, student_interests, preferred_domain='', top_n=3):
    """
    student_skills: list of strings, e.g. ['python', 'html', 'sql']
    student_interests: list of strings, e.g. ['web development']
    preferred_domain: optional string the student typed, e.g. 'backend'

    Returns a list of dicts: [{'career': CareerPath, 'match_percent': 82}, ...]
    sorted from best match to worst.
    """
    student_skills = [s.strip().lower() for s in student_skills if s.strip()]
    student_interests = [i.strip().lower() for i in student_interests if i.strip()]
    preferred_domain = preferred_domain.strip().lower()

    results = []

    for career in CareerPath.objects.all():
        required = career.required_skills_list()
        if not required:
            continue

        # how many of the career's required skills does the student already have
        matched_skills = [skill for skill in required if skill in student_skills]
        skill_score = len(matched_skills) / len(required)

        # small bonus if any of the student's interests appear in the career name/description
        interest_bonus = 0
        career_text = (career.name + ' ' + career.description).lower()
        for interest in student_interests:
            if interest and interest in career_text:
                interest_bonus += 0.1

        # small bonus if the student's preferred domain matches the career name
        domain_bonus = 0.15 if preferred_domain and preferred_domain in career.name.lower() else 0

        total_score = skill_score + interest_bonus + domain_bonus
        match_percent = min(round(total_score * 100), 100)

        results.append({
            'career': career,
            'match_percent': match_percent,
            'matched_skills': matched_skills,
        })

    # best match first
    results.sort(key=lambda r: r['match_percent'], reverse=True)
    return results[:top_n]
