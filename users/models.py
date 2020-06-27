from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from decimal import Decimal
from django.utils.safestring import mark_safe
# Create your models here.
class CustomUser(AbstractUser):
	pass
	# add additional fields in here
	#user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
	CUSTOMER = 'CU'
	MERCHANT = 'MR'
	ROLETYPE_CHOICES = (
		(CUSTOMER,'Customer'),
		(MERCHANT,'Merchant')
	)
	role = models.CharField(
		max_length = 10,
		choices=ROLETYPE_CHOICES,
		default='CUSTOMER'
	)
	phoneNumber = PhoneNumberField(blank=True, help_text='Phone number')
	isRegistrationDone = models.BooleanField(default=False)

class State(models.Model):
	name = models.CharField(max_length=50)
	code = models.CharField(max_length=2)

class Address(models.Model):
	street_address1 = models.CharField(max_length = 100, verbose_name = "Address Line 1")
	street_address2 = models.CharField(max_length = 100, verbose_name = "Address Line 2")
	apt_or_unit_number = models.CharField(max_length=20, blank=True, verbose_name="Apt/Unit") # can be an integer or a character
	additional_details = models.CharField(max_length=50, blank=True, verbose_name="Floor, building, etc.")
	city = models.CharField(max_length=50)
	zipcode = models.PositiveIntegerField(error_messages={'invalid':'Please enter a valid ZIP Code'})
	state = models.ForeignKey(State, on_delete = models.CASCADE,error_messages={'invalid':'Please choose valid state'} )

class Store(models.Model):
	store_id = models.AutoField(primary_key=True)
	owner = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
	name = models.CharField(max_length=75)
	description = models.TextField(blank=True)
	logo = models.ImageField(upload_to='store/')
	contactNumber = PhoneNumberField(blank=True, help_text='Contact number')
	start = models.TimeField(auto_now=False, auto_now_add=False)
	end = models.TimeField(auto_now=False, auto_now_add=False)
	sundayOpen = models.BooleanField(default=False)
	mondayOpen = models.BooleanField(default=False)
	tuesdayOpen = models.BooleanField(default=False)
	wednesdayOpen = models.BooleanField(default=False)
	thursdayOpen = models.BooleanField(default=False)
	fridayOpen = models.BooleanField(default=False)
	saturdayOpen = models.BooleanField(default=False)

	def image_tag(self):
		from django.utils.html import escape
		return mark_safe('<img src="{}" width="150" height="150" />'.format(self.url()))
	image_tag.short_description = 'Image'

	def clean(self):
		if self.start > self.end:
			raise ValidationError('Start Time should be before End Time')
		return super().clean()

	class Meta:
		constraints = [
			models.CheckConstraint(
				check=Q(start__lte=F('end')),
				name='start_before_end')		   
		]

class StoreItem(models.Model):
	item_id = models.AutoField(primary_key=True)
	store = models.ForeignKey(Store, on_delete = models.CASCADE)
	name = models.CharField(max_length = 75)
	description = models.TextField(blank = True)
	price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.01'))])
	logo = models.ImageField(upload_to ='store/')


class Cart(models.Model):
	cart_id = models.AutoField(primary_key=True)
	user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
	store = models.ForeignKey(Store, on_delete = models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True, blank=True)

	class Meta:
		unique_together = ('user','store')

class CartItems(models.Model):
	cartItem_id = models.AutoField(primary_key=True)
	cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
	item = models.ForeignKey(StoreItem, on_delete = models.CASCADE)
	quantity = models.PositiveIntegerField(default=0)

class Order(models.Model):
	order_id = models.AutoField(primary_key=True)
	user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
	store = models.ForeignKey(Store, on_delete = models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True, blank=True)

class OrderItems(models.Model):
	orderItem_id = models.AutoField(primary_key=True)
	order = models.ForeignKey(Order, on_delete = models.CASCADE)
	item = models.ForeignKey(StoreItem, on_delete = models.CASCADE)
	price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.01'))])
	quantity = models.PositiveIntegerField()
	processed = models.BooleanField(default=False)
	added = models.BooleanField(default=False)

	def clean(self):
		if self.added == True and self.processed == False:
			raise ValidationError('Start Time should be before End Time')
		return super().clean()










