
from django.shortcuts import render,get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request,'blog/post/comment.html',
                           { 'post':post,
                             'form':form,
                             'comment': comment})


def post_share(request, post_id):
    post = get_object_or_404(Post,id = post_id, status = Post.Status.PUBLISHED)
    sent = False
                             
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(cmd,
                post.get_absolute_url())
            subject = f"{cd['name']} recomends your read"\
                      f"{post.title}"
            message = f"Read{post.title} at {post_url}\n\n"\
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'swahab947@gmail.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})
        

class PostListView(ListView):

    """
    Alternative post ListView

    """
    queryset = Post.objects.all()
    context_object_name = 'posts'
    paginated_by = 3
    template_name = 'blog/post/list.html'
    

# Create your views here.
def post_list(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list,3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # if page number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)


    return render(request,
                  'blog/post/list.html',
                  {'posts':posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status = Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()  
    return render(request,
                  'blog/post/detail.html',
                  {'post': post, 
                   'comments': comments,
                   'form': form})

