# -*- encoding: utf-8 -*-
import pytest
import io
import PIL
import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from block.models import (
    BlockError,
    Image,
)
from block.tests.factories import (
    ImageCategory,
    ImageCategoryFactory,
    ImageFactory,
)
from login.tests.factories import (
    TEST_PASSWORD,
    UserFactory,
)


def test_file():
    """create an (image) file ready to upload."""
    fp = io.BytesIO()
    PIL.Image.new('1', (1, 1)).save(fp, 'png')
    fp.seek(0)
    return SimpleUploadedFile(
        'file.png',
        fp.read(),
        content_type='image/png'
    )


@pytest.mark.django_db
def test_category_create(client):
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    url = reverse('block.image.category.create')
    data = {
        'name': 'Tennis',
    }
    response = client.post(url, data)
    # check
    assert 302 == response.status_code
    expect = reverse('block.image.category.list')
    assert expect in response['Location']
    categories = ImageCategory.objects.all()
    assert 1 == categories.count()
    assert 'Tennis' == categories[0].name


@pytest.mark.django_db
def test_category_delete(client):
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    category = ImageCategoryFactory()
    assert category.deleted is False
    # test
    url = reverse('block.image.category.delete', args=[category.pk])
    response = client.post(url)
    # check
    assert 302 == response.status_code
    expect = reverse('block.image.category.list')
    assert expect in response['Location']
    category.refresh_from_db()
    assert category.deleted is True


@pytest.mark.django_db
def test_category_delete_exception(client):
    """Should not delete a category which is in use."""
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    category = ImageCategoryFactory()
    ImageFactory(category=category)
    assert category.deleted is False
    # test
    url = reverse('block.image.category.delete', args=[category.pk])
    with pytest.raises(BlockError) as e:
        client.post(url)
    assert 'Cannot delete an image category which is in use' in str(e.value)


@pytest.mark.django_db
def test_category_update(client):
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    category = ImageCategoryFactory()
    url = reverse('block.image.category.update', args=[category.pk])
    data = {
        'name': 'Cricket',
    }
    response = client.post(url, data)
    # check
    assert 302 == response.status_code
    expect = reverse('block.image.category.list')
    assert expect in response['Location']
    category.refresh_from_db()
    assert 'Cricket' == category.name


@pytest.mark.django_db
def test_image_delete(client):
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    image_1 = ImageFactory()
    image_2 = ImageFactory()
    image_3 = ImageFactory()
    url = reverse('block.image.list.delete')
    data = {
        'images': [image_1.pk, image_3.pk],
    }
    response = client.post(url, data)
    # check
    assert 302 == response.status_code
    expect = reverse('block.image.list')
    assert expect in response['Location']
    result = [image.pk for image in Image.objects.images()]
    assert [image_2.pk] == result


@pytest.mark.django_db
def test_image_create(client):
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    url = reverse('block.image.create')
    data = {
        'tags': 'apple pear',
        'title': 'Football',
        'image': test_file(),
    }
    response = client.post(url, data)
    # check
    assert 302 == response.status_code
    expect = reverse('block.image.list')
    assert expect in response['Location']
    image = Image.objects.last()
    assert 'Football' == image.title
    # assert ['apple', 'pear'] == sorted([x for x in image.tags.names()])


@pytest.mark.django_db
def test_image_update(client):
    user = UserFactory(is_staff=True)
    assert client.login(username=user.username, password=TEST_PASSWORD) is True
    image = ImageFactory()
    url = reverse('block.image.update', args=[image.pk])
    data = {
        'tags': 'apple pear',
        'title': 'Football',
    }
    response = client.post(url, data)
    # check
    assert 302 == response.status_code
    expect = reverse('block.image.list')
    assert expect in response['Location']
    image.refresh_from_db()
    assert 'Football' == image.title
    assert ['apple', 'pear'] == sorted([x for x in image.tags.names()])
