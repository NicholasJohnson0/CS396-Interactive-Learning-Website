from django.db import models

# Create your models here.
from django.conf import settings

SUBJECT_CHOICES = (
    ('Reading', 'Reading'),
    ('Math', 'Math'),
    ('Science', 'Science'),
    ('History', 'History'),
)

class question_model(models.Model):
    question = models.CharField(max_length=200,null=True)
    op1 = models.CharField(max_length=200,null=True)
    op2 = models.CharField(max_length=200,null=True)
    op3 = models.CharField(max_length=200,null=True)
    op4 = models.CharField(max_length=200,null=True)
    ans = models.CharField(max_length=200,null=True)
    max_attempts = models.PositiveIntegerField(default=3)  #max attempts
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='Reading')
    
    def __str__(self):
        return self.question

class quiz_submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz_question = models.ForeignKey(question_model, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=200, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)  # Add a score field
    attempts = models.PositiveIntegerField(default=0)  # Track the number of attempts


    def __str__(self):
        return f"Submission by {self.user.username} - Question: {self.quiz_question.question}"

