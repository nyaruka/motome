from decimal import Decimal
from customers.models import Customer
from django.contrib import auth
from products.models import *
from django_quickblocks.models import *
import re
from smartmin.views import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from orders.models import Order
from locales.models import Country, Currency
from locales.widgets import CoordinatesPickerField
from customers.models import Location
from transactions.models import Credit, Debit

from django.db.models import Sum

# check if the user is trusted
def is_trusted(request):
    return request.session.get('trusted', False)

# gate keeper to verify for visitors with/out secret pass
def has_secret_pass(request):
    SECRET_PASS = 'iamhungry'
    return request.GET and request.GET['password'] == SECRET_PASS

class LoginForm (forms.Form):
    phone_number = forms.CharField()

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub("[^0-9]", "", phone_number)

        if len(phone_number) != 10:
            raise forms.ValidationError("Please enter a phone number with 10 digits, e.g. 0788 55 55 55")

        return phone_number

def home(request):
    country = Country.objects.get(country_code='RW')
    request.session['currency'] = country.currency
    
    # populate favorite stores, for now will be loading all in rwanda
    favorite_stores = []

    for store in Store.objects.filter(country=country):
        favorite_stores.append(store)

    context = dict(product_list=Product.objects.filter(is_active=True), country=country, favorite_stores=favorite_stores, currency=country.currency)

    if has_secret_pass(request) or is_trusted(request):
        request.session['trusted'] = True
        return render_to_response('public/home.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('public/home_login.html', context, context_instance=RequestContext(request))

def cart(request):
    order = Order.from_request(request)
    country = Country.objects.get(country_code='RW')

    if request.method == 'POST':
        if 'add_product' in request.REQUEST:
            product = Product.objects.get(id=request.REQUEST['add_product'], is_active=True)
            order.add_single(product)

        if set(('update', 'checkout', 'shop')).intersection(set(request.REQUEST.keys())):
            for item in order.items.all():
                if 'remove_%d' % item.id in request.REQUEST:
                    order.items.filter(pk=item.id).update(is_active=False)

                for addon in item.product.addons.all():
                    exists_in_order = item.addons.filter(addon=addon)
                    form_name = 'addon_%d_%d' % (item.id, addon.id)
                    exists_in_form = form_name in request.REQUEST

                    if exists_in_order and not exists_in_form:
                        exists_in_order.update(is_active=False)

                    elif exists_in_form and not exists_in_order:
                        item.add_on(addon)

            if 'checkout' in request.REQUEST:
                return HttpResponseRedirect(reverse('public_checkout'))
            elif 'shop' in request.REQUEST:
                return HttpResponseRedirect("%s?password=iamhungry" % reverse('public_home'))

    context = dict(cart=True, order=order, country=country, currency=country.currency)
    return render_to_response('public/cart.html', context, context_instance=RequestContext(request))

def checkout(request):
    order = Order.from_request(request)
    country = Country.objects.get(country_code='RW')
    initial_data = dict()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            phone_number = country.derive_international_number(phone_number)
            customer = Customer.get_or_create_customer(phone_number)
            customer.send_password()

            request.session['customer'] = customer
            return HttpResponseRedirect(reverse('public_login'))
    else:
        form=LoginForm(initial_data)

    context = dict(order=order, country=country, currency=country.currency, form=form)
    return render_to_response('public/checkout.html', context, context_instance=RequestContext(request))

class PasswordForm(forms.Form):
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        password = re.sub("[^0-9]", "", password)

        if not self.user.check_password(password):
            raise forms.ValidationError("Sorry, that password doesn't match, try again.")

        return password

class CustomerForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

def login(request):
    user = request.session['customer']

    if request.method == 'POST':
        password_form = PasswordForm(request.POST, user=user)
        customer_form = CustomerForm(request.POST)

        if password_form.is_valid() and customer_form.is_valid():
            customer = request.session['customer']

            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.email = customer_form.cleaned_data['email']
            customer.save()

            user = auth.authenticate(username=customer.username, password=password_form.cleaned_data['password'])
            auth.login(request, user)
            order = Order.from_request(request)
            order.user = user
            order.save()

            if 'location' in request.session:
                location = request.session['location']
                return HttpResponseRedirect("%s?lat=%s&lng=%s" % (reverse('public.location_create'), location.lat, location.lng))
            else:
                return HttpResponseRedirect(reverse('public.location_create'))
    else:
        password_form = PasswordForm(user=user)
        customer_form = CustomerForm(initial={'first_name':user.first_name, 'last_name':user.last_name, 'email': user.email})

    context = dict(password_form=password_form, customer_form=customer_form, user=user)
    return render_to_response('public/login.html', context, context_instance=RequestContext(request))


class LocationForm(forms.ModelForm):
    coordinates = CoordinatesPickerField(required=True)    

    def clean(self):
        clean = self.cleaned_data;
        if 'coordinates' in clean and self.instance:
            self.instance.lat = clean['coordinates']['lat']
            self.instance.lng = clean['coordinates']['lng']

        return clean

    class Meta:
        model = Location
        fields = ('building', 'business', 'hints', 'coordinates')


class LocationCRUDL(SmartCRUDL):
    model = Location
    actions = ('create',)
    permissions = False

    class Create(SmartCreateView):
        form_class = LocationForm
        fields = ('building', 'business', 'hints', 'coordinates')

        def derive_initial(self):
            if self.object and self.object.lat and self.object.lng:
                return dict(coordinates=(dict(lat=self.object.lat, lng=self.object.lng))) #pragma: no cover
            else:
                country = Country.objects.get(country_code='RW')
                return dict(coordinates=(dict(lat=country.bounds_lat, lng=country.bounds_lng)))

        def get_context_data(self, **kwargs):
            context = super(LocationCRUDL.Create, self).get_context_data(**kwargs)
            context['display_fields'] = ['hints', 'nickname']
            context['order'] = Order.from_request(self.request)

            # add our country and it's root locations
            context['country'] = Country.objects.get(country_code='RW')

            # set the country on our form's location picker
            self.form.fields['coordinates'].set_country(context['country'])
            
            return context

        def pre_save(self, obj):
            obj = super(LocationCRUDL.Create, self).pre_save(obj)
            obj.customer = self.request.user
            
            return obj

        def post_save(self, obj):
            obj = super(LocationCRUDL.Create, self).post_save(obj)
            self.order = Order.from_request(self.request)
            self.order.location = obj
            self.order.stage = 'L'
            self.order.save()

            self.request.session['location'] = obj
            return obj

        def get_success_url(self):
            return reverse('public_pay', args=[self.order.id])

def pay(request, id):
    order = Order.objects.get(id=id)
    country = Country.objects.get(country_code='RW')

    if not Credit.objects.filter(creditor=order.user):
        Credit.objects.create(phone=order.user.username, creditor=order.user, amount=Decimal('0'), created_by=order.user, modified_by=order.user)
        
    # get the sum of all credit associated with this user
    credit_amount = Credit.objects.filter(creditor=order.user).aggregate(Sum('amount'))

    # calculate balance
    balance = credit_amount['amount__sum']
    
    debit_amount = Debit.objects.filter(customer=order.user).aggregate(Sum('amount'))    

    if debit_amount['amount__sum']:
        balance = credit_amount['amount__sum'] - debit_amount['amount__sum'] #pragma: no cover

    context = dict(order=order, user=order.user, country=country, currency=country.currency)    
    # check if the sum of amount is equal or more that the total value on this order
    if balance - order.total_with_delivery >= 0:
        # create debit of order total value hence the balance will change on refresh
        debit = Debit.objects.create(amount=order.total_with_delivery, order=order, customer=order.user, created_by=order.user, modified_by=order.user)
        debit_amount = Debit.objects.filter(customer=order.user).aggregate(Sum('amount'))
        
        # mark the order to be payed
        order.stage = 'P'
    
        # clear all but trusted and currency
        for sesskey in request.session.keys():
            if sesskey != 'trusted' or sesskey != 'currency':
                del request.session[sesskey]

        # send message to "code@nyaruka.com"
        from django.core.mail import EmailMessage
        from django.core.mail import send_mail
        from django.conf import settings
        mail_subject = "Motome Order on the line. Right now!"
        mail_message = "Hello, Motome team %s just send an order job, please make sure you follow up until he/she receive all ordered items" % order.user.username

        send_mail(mail_subject, mail_message, settings.DEFAULT_FROM_EMAIL, ['code@nyaruka.com'])

        # add balance to context
        balance = balance - order.total_with_delivery
        return HttpResponseRedirect(reverse('public_success'))

    context['balance'] = balance
    return render_to_response('public/pay.html', context, context_instance=RequestContext(request))    

def success(request):
    context = dict()
    return render_to_response('public/success.html', context, context_instance=RequestContext(request))    

def confirm(request, id):
    order = Order.objects.get(id=id)
    
    country = Country.objects.get(country_code='RW')

    context = dict(order=order, user=order.user, country=country, currency=country.currency)
    return render_to_response('public/confirm.html', context, context_instance=RequestContext(request))
