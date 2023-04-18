from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import CommentForm
from .models import Post, Category, Tag

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'head_image', 'file_upload', 'category', 'tag']

    template_name = 'blog/post_update.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.get_object().author == request.user:
            return super(PostUpdate,self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionError


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'head_image', 'file_upload', 'category', 'tag']

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):

        if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff):
            form.instance.author = self.request.user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/blog/')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostCreate, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_count'] = Post.objects.filter(category=None).count()

        return context

class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_count'] = Post.objects.filter(category=None).count()

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


def categories_page(request, slug):
    if slug=='no-category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else :
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    context = {
        'category' : category,
        'categories' : Category.objects.all(),
        'post_list' : post_list,
        'no_category_count' : Post.objects.filter(category=None).count()
    }
    return render(request, 'blog/post_list.html', context)


def tag_page(request, slug):

    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    context = {
        'tag' : tag,
        'categories' : Category.objects.all(),
        'post_list' : post_list,
        'no_category_count' : Post.objects.filter(category=None).count()
    }
    return render(request, 'blog/post_list.html', context)


def add_comment(request, pk):
    if not request.user.is_authenticated:
        raise PermissionError

    if request.method == 'POST':
        post = Post.objects.get(pk=pk)
        comment_form = CommentForm(request.POST)
        comment_temp = comment_form.save(commit=False)
        comment_temp.post = post
        comment_temp.author = request.user
        comment_temp.save()

        return redirect(post.get_absolute_url())
    else:
        raise PermissionError