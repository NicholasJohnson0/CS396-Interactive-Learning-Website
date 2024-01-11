from django.shortcuts import render, redirect, get_object_or_404

from blog.models import BlogPost
from blog.forms import CreateBlogPostForm, UpdateBlogPostForm, PostReplyForm
from account.models import Account

#create new blog page
def create_blog_view(request):
    
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')

    form = CreateBlogPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        author = Account.objects.filter(email=user.email).first()
        obj.author = author
        obj.save()
        form = CreateBlogPostForm()
    
    context['form'] = form
    
    return render(request, "blog/create_blog.html", {})

def detail_blog_view(request, slug):
    context = {}
    blog_post = get_object_or_404(BlogPost, slug=slug)
    context['blog_post'] = blog_post

    #reply function
    if request.method == 'POST':
        reply_form = PostReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.author = request.user
            reply.blog_post = blog_post
            reply.save()
            reply_form = PostReplyForm()  #clear box after reply

    else:
        reply_form = PostReplyForm()

    context['reply_form'] = reply_form

    return render(request, 'blog/detail_blog.html', context)

def edit_blog_view(request, slug):
    
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect("must_authenticate")

    blog_post = get_object_or_404(BlogPost, slug=slug)
    if request.POST:
        form = UpdateBlogPostForm(request.POST or None, request.FILES or None, instance=blog_post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "Updated"
            blog_post = obj
    form = UpdateBlogPostForm(
            initial = {
                "title": blog_post.title,
                "body": blog_post.body,
                "image": blog_post.image,
            }
        )

    context['form'] = form
    return render(request, 'blog/edit_blog.html', context)