from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Post
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

# Create your views here.
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    # if tag slug is given in the url 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        # filter by tags
        object_list = object_list.filter(tags__in=[tag])

    # instatiate paginator to display only 3 posts per page
    paginator = Paginator(object_list, 3)
    # get the page number from the request parameter from the url
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)

    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 
                    'blog/post/list.html', 
                    {'page': page, 'posts': posts, 'tag':tag}
                )

# using class based view
# class PostListView(ListView):
#     queryset = Post.published.all()
#     paginate_by = 3
#     context_object_name = 'posts'
#     template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                publish__year=year,
                                publish__month=month,
                                publish__day=day
                            )

    # find all comments related to this post
    comments = post.comments.filter(active=True)
    # Initiate new_comment variable
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # partially save the comment because we are yet to get the post the comment is related to
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            # save the comment to the DB
            new_comment.save()
    else:
        comment_form = CommentForm()
    # List of similar posts
    # fetch all tag ids
    post_tag_ids = post.tags.values_list('id', flat=True)
    # post_tag_ids becomes a list(array)
    # fetch all posts with similar tags and exclude the current post
    similar_posts = Post.published.filter(tags__in=post_tag_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

        
    return render(request, 'blog/post/detail.html', {'post': post,
                                                    'comment_form': comment_form,
                                                    'comments': comments,
                                                    'new_comment': new_comment,
                                                    'similar_posts': similar_posts
                                                    })


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    # get submitted details from form
    if request.method == "POST":
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # clean form
            cd = form.cleaned_data

            # build the url to share
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url},  {cd['name']}\'s comments: {cd['comments']}"

            # send email
            send_mail(subject, message, 'admin@site.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})




