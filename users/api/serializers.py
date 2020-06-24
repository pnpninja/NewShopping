from rest_framework import serializers
from users.models import CustomUser
from phonenumber_field.serializerfields import PhoneNumberField

class CustomUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ('username','email','first_name','last_name','phoneNumber','isRegistrationDone','role')
		read_only_fields = ['email']

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

