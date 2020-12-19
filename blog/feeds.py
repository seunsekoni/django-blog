from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post

class LatestPostsFeed(Feed):
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'

    def items(self):
        return Post.published.all()[:5]

    # receive each object returned by items() and
    # return the title
    def item_title(self, item):
        return item.title

    # receive each object returned by items() and
    # return the description
    def item_description(self, item):
        return truncatewords(item.body, 30)