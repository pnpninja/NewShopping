from rest_framework import serializers
from users.models import CustomUser, Store, StoreItem
from phonenumber_field.serializerfields import PhoneNumberField

class CustomUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ('username','email','first_name','last_name','phoneNumber','isRegistrationDone','role','id')
		read_only_fields = ['email']

class StoreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Store
		fields = ('store_id','owner','name','description','logo','contactNumber','start','end','sundayOpen','mondayOpen','tuesdayOpen','wednesdayOpen','thursdayOpen','fridayOpen','saturdayOpen')
		read_only_fields = ['store_id']

class UpdateStoreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Store
		fields = ('name','description','contactNumber','start','end','sundayOpen','mondayOpen','tuesdayOpen','wednesdayOpen','thursdayOpen','fridayOpen','saturdayOpen')

class CreateStoreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Store
		fields = ('name','description','logo','contactNumber','start','end','sundayOpen','mondayOpen','tuesdayOpen','wednesdayOpen','thursdayOpen','fridayOpen','saturdayOpen')

class StoreItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = StoreItem
		fields = ('item_id','store','name','description','price','logo')

class CreateStoreItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = StoreItem
		fields = ('name','description','price',)

class UpdateStoreImageSerializer(serializers.Serializer):
	logo = serializers.ImageField(allow_empty_file=False)

class UpdateUserSerializer(serializers.Serializer):
	first_name = serializers.CharField(max_length=30)
	last_name = serializers.CharField(max_length=150)
	phoneNumber = PhoneNumberField(allow_blank=True)
	CUSTOMER = 'CU'
	MERCHANT = 'MR'
	ROLETYPE_CHOICES = (
		(CUSTOMER, 'Customer'),
		(MERCHANT, 'Merchant')
	)
	role = serializers.ChoiceField(choices=ROLETYPE_CHOICES)

