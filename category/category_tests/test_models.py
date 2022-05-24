import pytest

from django.test import TestCase
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

def test_test(db):
    # print(len(Category.objects.all()))
    assert len(Category.objects.all())==0

class CategoryModelTest(TestCase):
    def test_category(self):
        print('all categories', Category.objects.all())
        parent = Category.objects.create(name='parent')
        assert Category.objects.all().count()==1
        assert isinstance(parent, Category)
        assert '/' in parent.get_url()

        child = Category.objects.create(name='child', parent=parent)
        assert Category.objects.all().count()==2
        assert isinstance(child, Category)




