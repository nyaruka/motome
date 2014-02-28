from decimal import *
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from motome.tests import MotomeTestCase
from rapidsms.models import Backend, Connection
from transactions.models import Credit, Debit

class PublicTest(MotomeTestCase):
    def setUp(self):
        super(PublicTest, self).setUp()
        self.motome_backend = Backend.objects.create(name="motome")
        self.motome_conn = Connection.objects.create(backend=self.motome_backend, identity="mobilemoney")

    def test_public(self):
        # visit the main page, will have a form to fill first
        response = self.client.get(reverse('public_home'))

        self.assertEquals(200, response.status_code)
        self.assertIn('form', response.content)

        #  fill the form with the wrong password
        response = self.client.get("%s?password=iamhungrynot" % reverse('public_home'))
        self.assertEquals(200, response.status_code)
        self.assertIn('form', response.content)

        #  fill the form with the exact password
        response = self.client.get("%s?password=iamhungry" % reverse('public_home'))
        self.assertEquals(200, response.status_code)
        self.assertEquals(0, len(response.client.session.items()))

        # add steak burrito to the cart
        post_data = dict(add_product=self.s_burrito.id)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertEquals(1, len(response.context['order'].items))
        self.assertEquals(1, len(response.client.session.items()))
        self.assertIn('order_id', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])

        # add chicken burrito to the cart
        post_data = dict(add_product=self.c_burrito.id)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertEquals(2, len(response.context['order'].items))

        # keep shopping
        post_data = dict(shop=True)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertAtURL(response, reverse('public_home'))
        self.assertEquals(1, len(response.client.session.items()))
        self.assertIn('order_id', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])

        # remove the one product to the cart
        post_data = dict(update=True, remove_1=True)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertEquals(1, len(response.context['order'].items))

        # add addon to the remaining product
        post_data = dict(update=True, addon_2_1=True)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertEquals(1, len(response.context['order'].items[0].addon_ids()))

        # addon in order but not in form is removed and added the new one
        post_data = dict(update=True, addon_2_2=True)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertEquals(1, len(response.context['order'].items[0].addon_ids()))

        # add three addons at once
        post_data = dict(update=True, addon_2_1=True, addon_2_2=True, addon_2_3=True)
        response = self.assertPost(reverse('public_cart'), post_data)
        self.assertEquals(3, len(response.context['order'].items[0].addon_ids()))

        # checkout this item with its addons
        post_data = dict(checkout=True, addon_2_1=True, addon_2_2=True, addon_2_3=True)
        response = self.client.post(reverse('public_cart'), post_data, follow=True)
        self.assertAtURL(response, reverse('public_checkout'))
        self.assertEquals(1, len(response.client.session.items()))
        self.assertIn('order_id', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])

        # fill the form with a phone number beyond 10 digits
        post_data = dict(phone_number="250111111111", first_name="Eugene", last_name="Rwagasore")
        response = self.client.post(reverse('public_checkout'), post_data, follow=True)
        self.assertAtURL(response, reverse('public_checkout'))         
        self.assertIn("Please enter a phone number with 10 digits, e.g. 0788 55 55 55", response.content)

        # fill the form to checkout
        post_data = dict(phone_number="0111111111", first_name="Eugene", last_name="Rwagasore")
        response = self.client.post(reverse('public_checkout'), post_data, follow=True)
        self.assertAtURL(response, reverse('public_login')) 

        # now in the session there is a user and the same order from above
        self.assertEquals(2, len(response.client.session.items()))
        self.assertIn('order_id', response.client.session.keys())
        self.assertIn('customer', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])
        self.assertEquals('250111111111', str(response.client.session['customer'].username))

        from rapidsms_httprouter.models import Message
        messages = Message.objects.all()
        password = messages[0].text[-8:]

        # login with a wrong password
        post_data = dict(password="wrongpassword")
        response = self.client.post(reverse('public_login'), post_data, follow=True)
        self.assertAtURL(response, reverse('public_login'))         
        self.assertIn("Sorry, that password doesn&#39;t match, try again.", response.content)

        # login with the password sent from sms
        post_data = dict(first_name='Rwagasore', last_name='Eugene', email="rwagasore@gmail.com", password=password)
        response = self.client.post(reverse('public_login'), post_data, follow=True)
        self.assertAtURL(response, reverse('public.location_create')) 

        # now in the session there is a user and the same order from above
        self.assertIn('order_id', response.client.session.keys())
        self.assertIn('customer', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])
        self.assertEquals('250111111111', str(response.client.session['customer'].username))

        # fill the location data
        post_data = dict(coordinates_lat="-1.95", coordinates_lng="30.08", building="ICT Park", business="kLab",hints="Somewhere in Rwanda")
        response = self.client.post(reverse('public.location_create'), post_data, follow=True)
        self.assertAtURL(response, reverse('public_pay', args=[1]))

        # now in the session there is a user and the same order from above
        self.assertIn('order_id', response.client.session.keys())
        self.assertIn('customer', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])
        self.assertEquals('250111111111', str(response.client.session['customer'].username))

        # rollback and revisit the create location with current location in session
        post_data = dict(first_name='Rwagasore', last_name='Eugene', email="rwagasore@gmail.com", password=password)
        self.client.session['location'] = response.client.session['location']
        response = self.client.post(reverse('public_login'), post_data, follow=True)

        # now in the session there is a user and the same order from above
        self.assertIn('order_id', response.client.session.keys())
        self.assertIn('customer', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])
        self.assertEquals('250111111111', str(response.client.session['customer'].username))

        # should come with previous geo coordinates
        self.assertIn('lat=-1.95&lng=30.08', response.request['QUERY_STRING'])

        # repost the location to leach the pay page
        post_data = dict(coordinates_lat="-1.95", coordinates_lng="30.08", building="ICT Park", business="kLab",hints="Somewhere in Rwanda")
        response = self.client.post(reverse('public.location_create'), post_data, follow=True)
        self.assertAtURL(response, reverse('public_pay', args=[1]))

        # now in the session there is a user and the same order from above
        self.assertIn('order_id', response.client.session.keys())
        self.assertIn('customer', response.client.session.keys())
        self.assertEquals(1, response.client.session['order_id'])
        self.assertEquals('250111111111', str(response.client.session['customer'].username))
        
        # check if the order is there remember this order item has 3 addons
        self.assertEquals(len(response.context['order'].items), 1)
        self.assertEquals(len(response.context['order'].items[0].addons), 3)

        # the messages
        wrong_message_from_mm = "This message doesn't contain a valid transaction."
        wrong_connection_id = "You are not a motome user, this message is not supposed to be proccessed. You can use your credit by visiting 'motome.nyaruka.com'"
        successful_creditation = "Thank you. Your motome account has been credited, you can use this credit to order on motome."
        successful_debitation = "Thank you. Your order has been proccessed and your account have been debited and the balance is Rwf 0, you can use this credit to order on Motome."
        mobilemoney_msg = 'You have received Rwf 5,200 from 0111111112 Reason: . Your balance is Rwf 78,500'
        nonmobilemoney_msg = 'Something that is surely from somewhere else but mobile money'

        # send non mobile money msg and connection will receive the wrong connection message
        self.assertSMSResponse(self.sendSMS(nonmobilemoney_msg, self.conn1), wrong_connection_id)

        # send non mobile money msg with a mobile money connection identity 'this case is when mm send some kind of notifications
        self.assertSMSResponse(self.sendSMS("Thanks for using mobilemoney", self.motome_conn), wrong_message_from_mm)
        self.assertSMSResponse(self.sendSMS("Thanks for using mobilemoney we are the best mobile money system in africa continent", self.motome_conn), wrong_message_from_mm)
        self.assertSMSResponse(self.sendSMS("Thanks for using amount 123 we 123456789 the best mobile money system in africa continent", self.motome_conn), wrong_message_from_mm)

        # extract all info from the message and store them withing the credit model
        # because the message is from mobile money then there is amount being credited withing the system
        self.assertSMSResponse(self.sendSMS(mobilemoney_msg, self.motome_conn), successful_creditation)

        # get the credit object for this number
        creditor = User.objects.get(username='250111111112')
        credit = Credit.objects.get(creditor=creditor)

        # check the amount loaded '5200'
        self.assertEquals(Decimal('5200'), credit.amount)
        
        self.assertSMSResponse(self.sendSMS(mobilemoney_msg, self.motome_conn), successful_creditation)

        from django.db.models import Sum
        credit_amount = Credit.objects.filter(creditor=creditor).aggregate(Sum('amount'))
        # check the amount loaded '10400'
        self.assertEquals(Decimal('10400'), credit_amount['amount__sum'])

        # with credit lets get to the successfull payment
        creditor = response.client.session['customer']
        Credit.objects.create(creditor=creditor, amount=Decimal('50000'), phone='250111111111', created_by=creditor, modified_by=creditor)
        response = self.client.get(reverse('public_pay', args=[response.client.session['order_id']]), follow=True)

        # check if the response is successful
        self.assertAtURL(response, reverse('public_success'))

        # now in the session there is a user and the same order from above
        self.assertNotIn('order_id', response.client.session.keys())
        self.assertNotIn('customer', response.client.session.keys())

        # get the order's confirmation page
        # as admin I access the confirm page
        response = self.client.get(reverse('public_confirm', args=['1']), follow=True)
