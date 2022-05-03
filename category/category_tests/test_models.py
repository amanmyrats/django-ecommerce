import pytest

from category.models import Category


@pytest.fixture
def category_caga(db):
    return Category.objects.create(name='caga')


def test_category_model(db, category_caga):
    lists = category_caga.get_slug_list()
    name = category_caga.__str__()
    urls = category_caga.get_url()
    assert name=='caga'
    assert len(Category.objects.all())==1

    assert category_caga.name=='caga'

    # assert True

def test_test(db):
    # print(len(Category.objects.all()))
    assert len(Category.objects.all())==0