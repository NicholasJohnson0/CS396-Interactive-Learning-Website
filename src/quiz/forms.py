from django import forms
from quiz.models import question_model

class QuizCreationForm(forms.ModelForm):
    class Meta:
        model = question_model
        fields = ['question', 'op1', 'op2', 'op3', 'op4', 'ans', 'subject']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ans'].widget = forms.RadioSelect(choices=[
            ('op1', 'Option 1'),
            ('op2', 'Option 2'),
            ('op3', 'Option 3'),
            ('op4', 'Option 4'),
        ])

class QuizSubmissionForm(forms.Form):
    selected_option = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        super(QuizSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['selected_option'].choices = [(choice, choice) for choice in choices]
