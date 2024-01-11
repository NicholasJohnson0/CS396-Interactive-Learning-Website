from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

from .forms import QuizCreationForm, QuizSubmissionForm
from quiz.models import question_model, quiz_submission, SUBJECT_CHOICES
from django.http import HttpResponseForbidden
from django.db.models import Avg, F, Count
from account.models import Account

def create_quiz(request):
    if request.method == 'POST':
        form = QuizCreationForm(request.POST)
        if form.is_valid():
            #create a new question instance from the form
            question = form.save(commit=False)
            selected_option = form.cleaned_data.get('ans')

            #map the selected option to the corresponding content
            if selected_option == 'op1':
                question.ans = question.op1
            elif selected_option == 'op2':
                question.ans = question.op2
            elif selected_option == 'op3':
                question.ans = question.op3
            elif selected_option == 'op4':
                question.ans = question.op4

            question.subject = form.cleaned_data.get('subject')

            question.save()

            return redirect('quiz_list')

    else:
        form = QuizCreationForm()

    return render(request, 'quiz/create_quiz.html', {'form': form})

#view to see all quizes created
def quiz_list_view(request):
    quizzes = question_model.objects.all()
    user = request.user
    selected_subjects = request.GET.getlist('subject')

    if 'All' in selected_subjects:
        #if 'All Subjects' is selected, get all quizzes
        selected_subjects = [choice[0] for choice in SUBJECT_CHOICES]

    filtered_quizzes = filter_quizzes_by_subjects(quizzes, selected_subjects)

    user_has_taken = [quiz_submission.objects.filter(user=user, quiz_question=quiz).exists() for quiz in filtered_quizzes]

    context = {
        'quizzes': filtered_quizzes,
        'user_has_taken': user_has_taken,
    }

    return render(request, 'quiz/quiz_list.html', context)


def filter_quizzes_by_subjects(quizzes, selected_subjects):
    filtered_quizzes = quizzes

    if selected_subjects:
        filtered_quizzes = filtered_quizzes.filter(subject__in=selected_subjects)

    return filtered_quizzes



def take_quiz_view(request, quiz_id):
    #get the quiz question based on quiz_id
    question = get_object_or_404(question_model, pk=quiz_id)
    
    #check if the user has already submitted for this question
    submission, created = quiz_submission.objects.get_or_create(
        user=request.user,
        quiz_question=question,
    )

    #check if the user has already answered this question correctly
    if submission.score == 1:
        return HttpResponseForbidden("You have already answered this question correctly.")

    #check if the maximum number of attempts has been reached
    if submission.attempts >= question.max_attempts:
        return HttpResponseForbidden("You have reached the maximum number of attempts for this quiz.")

    if request.method == 'POST':
        form = QuizSubmissionForm(request.POST, choices=[question.op1, question.op2, question.op3, question.op4])
        if form.is_valid():
            selected_option = form.cleaned_data.get('selected_option')
            #check if the selected_option matches the correct answer (question.ans)
            is_correct = selected_option == question.ans

            #update the quiz_submission record
            submission.selected_option = selected_option
            submission.attempts += 1

            if is_correct:
                submission.score = 1
            
            submission.save()

            #calculate the average score for the subject across all quizzes
            avg_score = quiz_submission.objects.filter(
                user=request.user,
                quiz_question__subject=question.subject
            ).aggregate(avg_score=Avg('score'))

            #calculate the number grade for the subject based on the average score
            grade = avg_score['avg_score'] * 100 if avg_score['avg_score'] is not None else 0
            grade = min(grade, 100)  #cap the grade at 100%

            #update the user's grade for the subject based on the calculated grade
            subject_grade_field = f"{question.subject.lower()}_grade"
            setattr(request.user, subject_grade_field, grade)
            request.user.save()  #save the updated grade

            #redirect the user to the view_results page after a successful submission
            return redirect('view_results')

    else:
        #create a form instance with the previous submission's data, if available
        initial_data = {'selected_option': submission.selected_option}
        form = QuizSubmissionForm(initial=initial_data)

    return render(request, 'quiz/take_quiz.html', {'question': question, 'form': form, 'submission': submission})
    
def results_view(request):
    user = request.user

    if user.is_teacher:
        #retrieve all quiz submissions
        quiz_submissions = quiz_submission.objects.all()

        #retrieve all non-teacher accounts
        students = Account.objects.filter(is_teacher=False)

        #group students' grades by subject
        subject_grades = {}
        for subject_display, _ in SUBJECT_CHOICES:  #assuming question_model has SUBJECT_CHOICES
            subject = subject_display.lower()
            subject_grades[subject] = {
                'user_grades': []  #list to hold user-specific grades for each subject
            }

            #collect number and letter grades for each subject
            for student in students:
                student_grades = {
                    'user': student.username,
                    'number_grade': getattr(student, f'{subject}_grade'),
                    'letter_grade': getattr(student, f'{subject}_letter_grade')
                }
                subject_grades[subject]['user_grades'].append(student_grades)

        #sorting functionality for each subject
        sort_by = request.GET.get('sort_by')
        if sort_by in ['username', 'subject', 'number_grade', 'letter_grade']:
            for subject, grades in subject_grades.items():
                subject_grades[subject]['user_grades'].sort(key=lambda x: x[sort_by])

        return render(request, 'quiz/view_results.html', {'students': students, 'subject_grades': subject_grades, 'quiz_submissions': quiz_submissions})

    else:
        #for students, display their own quiz submissions (similar to the existing implementation)
        quiz_submissions = quiz_submission.objects.filter(user=user)
        return render(request, 'quiz/view_results.html', {'quiz_submissions': quiz_submissions})

def content_view(request):
    return render(request, 'quiz/content_page.html')