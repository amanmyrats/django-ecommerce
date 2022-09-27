import pytest 

from store.models import Currency, CurrencyRates, OtherExpense, Product, ReviewRating, Variation, Color, Size
from accounts.accounts_tests.test_models import user, vendor


@pytest.fixture
def product(db):
    return Product.objects.create(product_name='jeans', description='Some description')

@pytest.fixture
def color_yellow(db):
    return Color.objects.create(name='Yellow')

@pytest.fixture
def size_small(db):
    return Size.objects.create(name='S')

@pytest.fixture
def variation(db, product, color_yellow, size_small):
    return Variation.objects.create(
        product=product, color=color_yellow, size=size_small, quantity=10
    )

@pytest.fixture
def reviewrating(db, product, user):
    return ReviewRating.objects.create(user=user, product=product, subject='gaty gowy', 
    review='gaty gowy', rating=1, ip='1.1.1.1')

@pytest.fixture
def currency(db):
    return Currency.objects.create(code='TMM', num='993', currency='manat')

@pytest.fixture
def currencyrates(db, vendor, currency):
    return CurrencyRates.objects.create(vendor=vendor, currency=currency, usdequivalent=20)

@pytest.fixture
def otherexpense(db, variation):
    return OtherExpense.objects.create(variation=variation)

def test_product_model(db, product):
    assert product.__str__()=='jeans'
    assert isinstance(product, Product)
    assert 'default.jpg' in product.image_url()
    assert product.image_small_url()==''
    assert product.image_thumbnail_url()==''
    assert product.has_no_variation()==False
    assert product.colors()==[]
    assert product.sizes()==[]
    assert product.average_review()==0
    assert product.count_reviews()==0

def test_variation_model(db, variation, product):
    assert variation.__unicode__()==product
    assert variation.__str__()=='YellowS'

def test_reviewrating_model(db, reviewrating):
    assert isinstance(reviewrating, ReviewRating)
    assert reviewrating.__str__()=='gaty gowy'

def test_currency_model(db, currency):
    assert isinstance(currency, Currency)
    assert currency.__str__()=='TMM'

def test_currencyrates_model(db, currencyrates, currency):
    assert isinstance(currencyrates, CurrencyRates)
    assert currencyrates.__str__()=='sargajak - TMM - 20'

def test_otherexpense_model(db, otherexpense):
    assert isinstance(otherexpense, OtherExpense)
    assert otherexpense.__str__()=='YellowS - percentage - 0'
