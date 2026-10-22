"""
This file contains the AI-based roadmap generator.

Idea: the student picks a career, tells us their current skills, interests,
experience level and a learning goal. We send that to an AI API (if a key is
configured) and ask it to build a personalised roadmap. If the API key is
missing, the request fails, or the response is not usable for any reason,
we fall back to a simple roadmap built from data already in our own database
(CareerPath / Roadmap / RoadmapStage / RoadmapItem / LearningResource) so the
page never breaks and the user always sees something useful.
"""
import json
import requests
from decouple import config

from .models import CareerPath, LearningResource

AI_API_KEY = config('AI_API_KEY', default='')
AI_API_URL = config('AI_API_URL', default='https://api.openai.com/v1/chat/completions')
AI_MODEL = config('AI_MODEL', default='gpt-4o-mini')


def generate_ai_roadmap(career, skills, interests, experience_level, learning_goal):
    """
    career, experience_level, learning_goal: plain strings
    skills, interests: lists of strings

    Returns a dictionary the frontend can render directly. Always returns
    something usable - either 'source': 'ai' or 'source': 'fallback'.
    """
    if AI_API_KEY:
        ai_result = _call_ai_api(career, skills, interests, experience_level, learning_goal)
        if ai_result:
            ai_result['source'] = 'ai'
            return ai_result

    fallback_result = _build_fallback_roadmap(career, skills, interests, experience_level)
    fallback_result['source'] = 'fallback'
    return fallback_result


def _call_ai_api(career, skills, interests, experience_level, learning_goal):
    """
    Calls an OpenAI-compatible chat completion API and asks for a roadmap
    back as JSON. Returns None (never raises) if anything goes wrong, so the
    caller can fall back safely.
    """
    prompt = f"""You are a career mentor helping a student plan their learning path.

Career/Role: {career}
Current skills: {', '.join(skills) if skills else 'none mentioned'}
Interests: {', '.join(interests) if interests else 'none mentioned'}
Experience level: {experience_level or 'beginner'}
Learning goal: {learning_goal or 'become job-ready in this field'}

Reply with ONLY a JSON object (no extra text, no markdown) in exactly this shape:
{{
  "recommended_skills": ["skill1", "skill2", ...],
  "topics_to_learn": ["topic1", "topic2", ...],
  "learning_sequence": [
    {{"stage": "Beginner", "topics": ["...", "..."]}},
    {{"stage": "Intermediate", "topics": ["...", "..."]}},
    {{"stage": "Advanced", "topics": ["...", "..."]}}
  ],
  "suggested_projects": ["project idea 1", "project idea 2", "project idea 3"],
  "resources": ["resource or website name 1", "resource or website name 2"],
  "estimated_stages": [
    {{"stage": "Beginner", "duration": "1-2 months"}},
    {{"stage": "Intermediate", "duration": "2-3 months"}},
    {{"stage": "Advanced", "duration": "2-3 months"}}
  ]
}}"""

    headers = {
        'Authorization': f'Bearer {AI_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': AI_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.5,
    }

    try:
        response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']

        # the model sometimes wraps JSON in ```json ... ``` even when told not to
        content = content.strip().strip('`')
        if content.startswith('json'):
            content = content[4:].strip()

        parsed = json.loads(content)

        required_keys = ['recommended_skills', 'topics_to_learn', 'learning_sequence',
                          'suggested_projects', 'resources', 'estimated_stages']
        if not all(key in parsed for key in required_keys):
            return None

        return parsed
    except Exception:
        # network error, timeout, bad API key, bad JSON from the model, etc.
        # We deliberately don't crash the request - the view falls back instead.
        return None


def _build_fallback_roadmap(career, skills, interests, experience_level):
    """
    Simple rule based roadmap, built using whatever we already have stored
    in the database for this career. No external API involved.
    """
    student_skills = [s.strip().lower() for s in skills if s.strip()]

    career_obj = CareerPath.objects.filter(name__icontains=career).first()

    if career_obj:
        required_skills = career_obj.required_skills_list()
        recommended_skills = [s for s in required_skills if s not in student_skills] or required_skills
    else:
        # no matching career in our database, build a generic list from what the student typed
        recommended_skills = list(dict.fromkeys(skills + interests))[:6] or ['Communication', 'Problem Solving']

    learning_sequence = []
    topics_to_learn = []

    if career_obj and hasattr(career_obj, 'roadmap'):
        stages = career_obj.roadmap.stages.prefetch_related('items')
        for stage in stages:
            stage_topics = [item.title for item in stage.items.all()]
            learning_sequence.append({'stage': stage.get_level_display(), 'topics': stage_topics})
            topics_to_learn.extend(stage_topics)
        estimated_total_months = career_obj.roadmap.estimated_duration_months
    else:
        # generic 3 stage plan when we don't have a ready made roadmap for this career
        learning_sequence = [
            {'stage': 'Beginner', 'topics': [f'Learn the basics of {career}', 'Understand core concepts and tools']},
            {'stage': 'Intermediate', 'topics': [f'Build small projects in {career}', 'Practice with real world examples']},
            {'stage': 'Advanced', 'topics': ['Work on a full project', 'Prepare for interviews']},
        ]
        for stage in learning_sequence:
            topics_to_learn.extend(stage['topics'])
        estimated_total_months = 6

    # adjust pacing a little based on the student's stated experience level
    level = (experience_level or 'beginner').lower()
    if level == 'intermediate':
        estimated_total_months = max(3, estimated_total_months - 2)
    elif level == 'advanced':
        estimated_total_months = max(2, estimated_total_months - 4)

    per_stage_months = max(1, estimated_total_months // max(1, len(learning_sequence)))
    estimated_stages = [
        {'stage': s['stage'], 'duration': f'{per_stage_months} month(s)'} for s in learning_sequence
    ]

    suggested_projects = [
        f'Build a beginner project that uses {career}',
        f'Recreate a simple real-world app related to {career}',
        f'Contribute to or build a portfolio project showcasing {career} skills',
    ]

    resources = []
    if career_obj:
        matches = LearningResource.objects.filter(category__icontains=career_obj.name.split()[0])[:5]
        resources = [r.title for r in matches]
    if not resources:
        resources = [r.title for r in LearningResource.objects.all()[:5]]

    return {
        'career': career,
        'recommended_skills': recommended_skills,
        'topics_to_learn': topics_to_learn,
        'learning_sequence': learning_sequence,
        'suggested_projects': suggested_projects,
        'resources': resources,
        'estimated_stages': estimated_stages,
    }
