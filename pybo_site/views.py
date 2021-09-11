from django import forms
from django.core.checks import messages
from django.shortcuts import render,get_object_or_404,redirect,resolve_url
from .models import Comment, Question,Answer
from django.utils import timezone
from .forms import AnswerForm, QuestionForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

def index(request):
    page = request.GET.get('page','1')
    kw = request.GET.get('kw','')
    so = request.GET.get('so','recent')

    if so == 'recommend':
        question_list=Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter','-create_date')
    elif so == 'popular':
        question_list=Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer','-create_date')
    else:
        question_list=Question.objects.order_by('-create_date')


    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(answer__author__username__icontains=kw)
        ).distinct()

    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)
    context = {'question_list':page_obj,'page':page,'kw':kw,'so':so}
    return render(request, 'pybo/question_list.html',context)

def detail(request,question_id):
    question = get_object_or_404(Question,pk=question_id)
    context = {'question':question}
    return render(request, 'pybo/question_detail.html',context)


@login_required(login_url='common:login')
def answer_create(request, question_id):
    
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('{}#answer_{}'.format(resolve_url('pybo_site:detail',question_id=question.id), answer.id))
    else:
        form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)

@login_required(login_url='common:login')
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.create_date = timezone.now()
            question.save()
            return redirect('pybo_site:index')
    else:
        form = QuestionForm()
    context = {'form':form}

    return render(request,'pybo/question_form.html',context)

@login_required(login_url='common:login')
def question_modify(request, question_id):

    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다.')
        return redirect('pybo_site:detail', question_id=question.id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()
            question.save()
            return redirect('pybo_site:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    context = {'form':form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user != question.author:
        messages.error(request,'삭제권한이 없습니다.')
        return redirect('pybo_site:detail', question_id=question.id)
    question.delete()
    return redirect('pybo_site:index')

@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '수정권한이 없습니다.')
        return redirect('pybo_site:detail', question_id=answer.question.id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('{}#answer_{}'.format(resolve_url('pybo_site:detail',question_id=answer.question.id),answer.id))
    else:
        form =AnswerForm(instance=answer)
    context = {'answer':answer, 'form':form}
    return render(request, 'pybo/answer_form.html', context)

@login_required(login_url='common:login')
def answer_delete(request,answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request,'삭제권한이 없습니다.')
    else:
        answer.delete()
    return redirect('pybo_site:detail', question_id=answer.question.id)

@login_required(login_url='common:login')
def comment_create_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.question = question
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('pybo_site:detail',question_id=comment.question.id), comment.id))
    else:
        form = CommentForm()
    context = {'form':form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_modify_question(request, comment_id):
    comment = get_object_or_404(Comment,pk=comment_id)
    
    if request.user != comment.author:
        messages.error(request,'수정권한이 없습니다.')
        return redirect('pybo_site:detail',question_id=comment.question.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('pybo_site:detail',question_id=comment.question.id), comment.id))
    else:
        form = CommentForm()
    context = {'form':form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_delete_question(request,comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    if request.user != comment.author:
        messages.error(request,'삭제권한이 없습니다.')
        return redirect('pybo_site:detail', question_id=comment.question.id)
    else:
        comment.delete()
    return redirect('pybo_site:detail',question_id=comment.question.id)


@login_required(login_url='common:login')
def comment_create_answer(request, answer_id):
    """
    pybo 답글댓글등록
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.answer = answer
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('pybo_site:detail',question_id=comment.answer.question.id),comment.id))
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='common:login')
def comment_modify_answer(request, comment_id):
    """
    pybo 답글댓글수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('pybo_site:detail', question_id=comment.answer.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('pybo_site:detail',question_id=comment.answer.question.id),comment.id))
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)


@login_required(login_url='common:login')
def comment_delete_answer(request, comment_id):
    """
    pybo 답글댓글삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('pybo_site:detail', question_id=comment.answer.question.id)
    else:
        comment.delete()
    return redirect('pybo_site:detail', question_id=comment.answer.question.id)

@login_required(login_url='common:login')
def vote_question(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        question.voter.add(request.user)
    return redirect('pybo_site:detail', question_id=question.id)    

def vote_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)

    if request.user == answer.author:
        messages.error(request, '수정권한이 없습니다.')
    else:
        answer.voter.add(request.user)
    return redirect('pybo_site:detail', question_id = answer.question.id)
