from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import Category, Article, Comment, Profile
from .forms import ArticleForm, LoginForm, RegisterForm, CommentForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login, logout
from django.contrib import messages


#
def index(request):
    categories = Category.objects.all()
    articles = Article.objects.all()
    context = {
        'title': 'Киномания',
        'categories': categories,
        'articles': articles
    }

    return render(request, 'blog/index.html', context)


class ArticleListView(ListView):
    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    extra_context = {
        'title': 'Киномания'
    }


def category_view(request, pk):
    articles = Article.objects.filter(category_id=pk)
    categories = Category.objects.all()
    category = Category.objects.get(pk=pk)

    context = {
        'title': f'Категория {category.title}',
        'articles': articles,
        'categories': categories
    }

    return render(request, 'blog/index.html', context)


class ArticleListByCategory(ArticleListView):

    def get_queryset(self):
        articles = Article.objects.filter(category_id=self.kwargs['pk'])
        return articles


def article_view(request, pk):
    article = Article.objects.get(pk=pk)
    context = {
        'title': f'Статья {article.title}',
        'article': article
    }
    return render(request, 'blog/article_detail.html', context)


def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = Article.objects.create(**form.cleaned_data)
            article.save()
            return redirect('article', article.pk)

    else:
        form = ArticleForm()
    context = {
        'title': 'Создание статьи',
        'form': form
    }

    return render(request, 'blog/add_article.html', context)


class ArticleDetailView(DetailView):
    model = Article
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        article = Article.objects.get(pk=self.kwargs['pk'])
        article.views += 1
        article.save()
        context['title'] = article.title
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(article=article)
        return context


class NewArticle(CreateView):
    form_class = ArticleForm
    template_name = 'blog/add_article.html'
    extra_context = {
        'title': 'Создание статьи'
    }


class ArticleUpdate(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/add_article.html'


class ArticleDelete(DeleteView):
    model = Article
    context_object_name = 'article'
    success_url = reverse_lazy('index')


def user_login(request):
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            if user:
                login(request, user)
                messages.success(request, 'Успешный вход в аккаунт!')
                return redirect('index')
            else:
                messages.warning(request, 'Не верное имя пользователья или пароль!')
                return redirect('login')
        else:
            messages.warning(request, 'Не верное имя пользователья или пароль!')
            return redirect('login')
    else:
        login_form = LoginForm()

    context = {
        'title': 'Вход в аккаунт',
        'login_form': login_form
    }

    return render(request, 'blog/login.html', context)


def user_logout(request):
    logout(request)
    return redirect('index')


class SearchResults(ArticleListView):
    def get_queryset(self):
        word = self.request.GET.get('q').capitalize()
        articles = Article.objects.filter(title__icontains=word)
        return articles


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile = Profile.objects.create(user=user)
            profile.save()

            return redirect('login')

    else:
        form = RegisterForm()

    context = {
        'register_form': form,
        'title': 'Регистратция'
    }

    return render(request, 'blog/register.html', context)


def save_comment(request, pk):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment = Article.objexts.get(pk=pk)
        comment.user = request.user
        comment.save()
        messages.success(request, 'Ваш комментарий опубликован!')
        return redirect('article', pk)


def profile_view(request, pk):
    profile = Profile.objects.get(user_id=pk)

    context = {
        'profile': profile,
        'title': f'Страница {request.user.username}'
    }
    return render(request, 'blog/profile.html', context)


def about_me(request):
    return render(request, 'blog/about_me.html')


