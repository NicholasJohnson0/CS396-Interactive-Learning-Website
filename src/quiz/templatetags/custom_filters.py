from django import template
from quiz.models import quiz_submission

register = template.Library()

@register.filter
def get_score(user_scores, quiz_id):
    # Assuming user_scores is a dictionary with quiz IDs as keys
    return user_scores.get(quiz_id, "Not taken")
