from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


def test_user_can_create_comment(admin_client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    redirect_url = url + '#comments'
    response = admin_client.post(url, data=form_data)
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_use_bad_words(news, admin_client):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, data',
    (
        ('news:edit', pytest.lazy_fixture('form_data')),
        ('news:delete', None)
    ),
)
def test_author_can_edit_delete_comment(
        name, data, form_data, news, author_client, comment
):
    url = reverse(name, args=(comment.id,))
    redirect_url = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(url, data=data)
    assertRedirects(response, redirect_url)
    if data is not None:
        comment.refresh_from_db()
        assert comment.text == form_data['text']
    else:
        assert Comment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, data',
    (
        ('news:edit', pytest.lazy_fixture('form_data')),
        ('news:delete', None)
    ),
)
def test_user_cant_edit_delete_comment_of_another_author(
    name, data, admin_client, comment
):
    url = reverse(name, args=(comment.id,))
    response = admin_client.post(url, data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    if data is not None:
        comment.refresh_from_db()
        assert comment.text == 'Текст'
    else:
        assert Comment.objects.count() == 1
