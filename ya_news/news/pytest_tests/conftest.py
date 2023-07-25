from datetime import datetime, timedelta

import pytest
from news.models import Comment, News
from yanews import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(text='Текст', news=news, author=author)
    return comment


@pytest.fixture
def comment_list(news, author):
    today = datetime.today()
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'Tекст {index}', created=today - timedelta(days=index)
        )
        for index in range(4)
    ]
    comment_list = Comment.objects.bulk_create(all_comments)
    return comment_list


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    news_list = News.objects.bulk_create(all_news)
    return news_list


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def news_id(news):
    return news.id,
