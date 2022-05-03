import csv
import codecs
from email import message

from pathlib import Path

from django.http import HttpResponse

from ecommerce import settings
from store.models import Product, Color, Size, Variation
from accounts.models import Vendor


def object_no_variation(attr=None):
    if attr is None:
        return False 

    if attr == 'Color':
        try:
            nocolor = Color.objects.get(name='No Variation')
            return nocolor
        except:
            nocolor = Color.objects.create(name='No Variation')
            return nocolor

    if attr == 'Size':
        try:
            nosize = Size.objects.get(name='No Variation')
            return nosize
        except:
            nosize = Size.objects.create(name='No Variation')
            return nosize

def get_vendor(request=None):
    if request is None:
        return False 

    try:
        vendor = Vendor.objects.get(user=request.user)
        return vendor
    except:
        return False

def add_variation_for_new_product(new_product_id=None):
    if new_product_id is None:
        return False
    nocolor = object_no_variation(attr='Color')
    nosize = object_no_variation(attr='Size')
    if nocolor and nosize:
        new_no_variation = Variation()
        new_no_variation.product_id = new_product_id
        new_no_variation.color = nocolor 
        new_no_variation.size = nosize
        new_no_variation.quantity = 0
        new_no_variation.sale_price = 0
        new_no_variation.save()
        return True
    return False


def export_model(qs=None, model_name=None, csv_file=None):
    if qs is None or model_name is None or csv_file is None:
        return False
    
    if model_name == 'product':
        with open(csv_file, 'w') as f:
            # fields = [f.name for f in Product._meta.fields]
            fields = ['id', 'owner', 'brand', 'product_code', 'product_name', 'description', 'is_available', 'category']
            writer = csv.writer(f)
            writer.writerow(fields)
            for product in qs.values(*fields):
                writer.writerow([product[field] for field in fields])
                
        return True

    elif model_name == 'variation':
        with open(csv_file, 'w') as f:
            # fields = [f.name for f in Variation._meta.fields]
            fields = ['id', 'product', 'color', 'size', 'quantity', 'currency', 'initial_price', 'expense_percentage', 'expense_fixed', 'final_price', 'sale_price', 'in_stock', 'is_active']
            manual_fields = list(fields)
            manual_fields.append('no_change_product')
            manual_fields.append('no_change_color')
            manual_fields.append('no_change_size')
            manual_fields.append('no_change_brand')
            manual_fields.append('no_change_currency')
            manual_fields.append('delete?')
            writer = csv.writer(f)
            writer.writerow(manual_fields)
            for variation in qs:
                row = []
                # for v in variation.values(*fields):
                row.append(variation.id)
                try:
                    row.append(variation.product.id)
                except:
                    row.append('')
                try:
                    row.append(variation.color.id)
                except:
                    row.append('')
                try:
                    row.append(variation.size.id)
                except:
                    row.append('')
                row.append(variation.quantity)
                try:
                    row.append(variation.currency.id)
                except:
                    row.append('')
                row.append(variation.initial_price)
                row.append(variation.expense_percentage)
                row.append(variation.expense_fixed)
                row.append(variation.final_price)
                row.append(variation.sale_price)
                row.append(variation.in_stock)
                row.append(variation.is_active)
                row.append(variation.product.product_name)
                row.append(variation.color)
                row.append(variation.size)
                row.append(variation.product.brand)
                try:
                    row.append(variation.currency.code)
                except:
                    row.append('')
                writer.writerow(row)
        return True
    else:
        return False


def import_model(request=None, csv_file=None, model_name=None):
    if request is None or csv_file is None or model_name is None:
        return False

    vendor = get_vendor(request=request)
    if not vendor:
        return False

    is_uploader_vendor_or_superadmin = request.user.is_staff
    uploader_vendor_and_csv_vendor_are_same = False
    if not is_uploader_vendor_or_superadmin:
        uploader_vendor_and_csv_vendor_are_same = True
    if is_uploader_vendor_or_superadmin or uploader_vendor_and_csv_vendor_are_same:
        with open(csv_file) as f:
            print('openede file')
            reader = csv.DictReader(f)
            next(reader, None)  # skip the headers
            writer = csv.writer(f)

            # Product table
            if model_name == 'product':
                for row in reader:
                    if request.user.is_staff:
                        new_owner = row.get('owner')
                        if not new_owner:
                            new_owner = vendor.id
                    else:
                        new_owner = vendor.id
                    try:
                        id = row.get('id')
                        if not id:
                            print('I am raising error manually')
                            raise Product.DoesNotExist
                        try:
                            obj = Product.objects.get(id=id)
                            obj.brand = row.get('brand')
                            obj.product_code = row.get('product_code')
                            obj.product_name = row.get('product_name')
                            obj.description = row.get('description')
                            obj.owner_id = new_owner
                            obj.category_id = row.get('category')
                            obj.is_available = row.get('is_available')
                            obj.save()
                        except:
                            print('Variation does not exist.')
                    except Product.DoesNotExist:
                        print('exception successfully thrown')
                        possible_duplicate = Product.objects.filter(owner_id = new_owner, brand = row.get('brand'), product_name = row.get('product_name')).exists()
                        print('possible_duplicate', possible_duplicate)
                        if not possible_duplicate:
                            print('Started to create new Product.')
                            new_obj = Product.objects.create(
                                brand = row.get('brand'),
                                product_code = row.get('product_code'),
                                product_name = row.get('product_name'),
                                description = row.get('description'),
                                owner_id = new_owner,
                                category_id = row.get('category'),
                                is_available = row.get('is_available')
                                )
                            new_obj.save()
                            # Create version with no variation
                            add_variation_for_new_product(new_product_id=new_obj.pk)
                            print('new object created successfully')
                return True
            
            # Variation table
            elif model_name == 'variation':
                for row in reader:
                    try:
                        id = row.get('id')
                        if not id:
                            print('I am raising error manually')
                            raise Variation.DoesNotExist
                        try:
                            obj = Variation.objects.get(pk=id)
                            print('i am here')
                            print('obj.product.owner.account', obj.product.owner.user)
                            print('request.user', request.user)
                            if obj.product.owner.user == request.user or request.user.is_staff:
                                obj.product_id = int(row.get('product'))
                                obj.color_id = int(row.get('color'))
                                obj.size_id = int(row.get('size'))
                                obj.quantity = int(row.get('quantity'))
                                obj.currency_id = row.get('currency')
                                obj.initial_price = float(row.get('initial_price'))
                                obj.expense_percentage = float(row.get('expense_percentage'))
                                obj.expense_fixed = float(row.get('expense_fixed'))
                                obj.final_price = float(row.get('final_price'))
                                obj.sale_price = float(row.get('sale_price'))
                                obj.in_stock = row.get('in_stock')
                                obj.is_active = row.get('is_active')
                                obj.save()
                                print('saved successfully')
                            else:
                                print('that motherfucker')
                        except:
                            print('Variation does not exist.')
                    except Variation.DoesNotExist:
                        print('exception successfully thrown')
                        # 'owner', 'product', 'color', 'size'
                        possible_duplicate = Variation.objects.filter(product_id = row.get('product'), color_id = row.get('color'), size_id=row.get('size')).exists()
                        if not possible_duplicate:
                            new_obj = Variation.objects.create(
                                product_id = int(row.get('product')),
                                color_id = int(row.get('color')),
                                size_id = int(row.get('size')),
                                quantity = int(row.get('quantity')),
                                currency_id = row.get('currency'),
                                initial_price = float(row.get('initial_price')),
                                expense_percentage = float(row.get('expense_percentage')),
                                expense_fixed = float(row.get('expense_fixed')),
                                final_price = float(row.get('final_price')),
                                sale_price = float(row.get('sale_price')),
                                in_stock = row.get('in_stock'),
                                is_active = row.get('is_active'),
                                )
                            new_obj.save()
                            print('New Variation created successfully')
                return True

        return False
                
    else:
        return False
