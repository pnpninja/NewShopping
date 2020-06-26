from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser
from users.models import CustomUser, Store
from .serializers import CustomUserSerializer, UpdateUserSerializer, StoreSerializer, UpdateStoreSerializer, CreateStoreSerializer
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json
from rest_framework.decorators import parser_classes
from rest_framework.authtoken.models import Token
from braces.views import CsrfExemptMixin

#class CustomUserListView(ListAPIView):
#	queryset = CustomUser.objects.all()
#	serializer_class = CustomUserSerializer

#class CustomUserDetailView(RetrieveAPIView):
#	queryset = CustomUser.objects.all()
#	serializer_class = CustomUserSerializer

class PersonalUserDetailView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		return Response(CustomUserSerializer(user).data)

	def post(self, request):
		print(request.data)
		userFromToken = CustomUser.objects.get(email=request.user.email)
		userFromDataSerializer = UpdateUserSerializer(data=request.data)
		if not userFromDataSerializer.is_valid():
			return Response(userFromDataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
		elif userFromDataSerializer.data['role'] != "CU" and userFromDataSerializer.data['role'] != "MR":
			return Response(userFromDataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
		else:
			userFromToken.phoneNumber = userFromDataSerializer.data['phoneNumber']
			userFromToken.role = "CUSTOMER" if userFromDataSerializer.data['role'] == "CU" else "MERCHANT"
			userFromToken.first_name = userFromDataSerializer.data['first_name']
			userFromToken.last_name = userFromDataSerializer.data['last_name']
			userFromToken.isRegistrationDone = True
			userFromToken.save()
			return Response(CustomUserSerializer(userFromToken).data, status=status.HTTP_200_OK)

class StoreDetailView(APIView):
	parser_classes = (MultiPartParser, FormParser, JSONParser)
	permission_classes = (IsAuthenticated,)
	def get(self, request, store_id=None):
		if store_id == None:
			store_data = Store.objects.all()
			return Response(StoreSerializer(store_data,many=True).data)
		else:
			try:
				store_data = Store.objects.get(store_id=store_id)
				return Response(StoreSerializer(store_data).data)
			except:
				return Response(status=status.HTTP_404_NOT_FOUND)

	def put(self, request, store_id=None):
		if store_id == None:
			return Response(status=status.HTTP_403_FORBIDDEN)
		else:
			try:
				store_data = Store.objects.get(store_id=store_id)
				if(store_data.owner.id != request.user.id):
					return Response({"message":"That's an illegal move"},status=status.HTTP_403_FORBIDDEN)
				else:
					store_data_new = UpdateStoreSerializer(data=request.data)
					if not store_data_new.is_valid():
						return Response(UpdateStoreSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
					else:
						store_data.name = store_data_new.data['name']
						store_data.description = store_data_new.data['description']
						store_data.contactNumber = store_data_new.data['contactNumber']
						store_data.start = store_data_new.data['start']
						store_data.end = store_data_new.data['end']
						store_data.sundayOpen = store_data_new.data['sundayOpen']
						store_data.mondayOpen = store_data_new.data['mondayOpen']
						store_data.tuesdayOpen = store_data_new.data['tuesdayOpen']
						store_data.wednesdayOpen = store_data_new.data['wednesdayOpen']
						store_data.thursdayOpen = store_data_new.data['thursdayOpen']
						store_data.fridayOpen = store_data_new.data['fridayOpen']
						store_data.saturdayOpen = store_data_new.data['saturdayOpen']
						store_data.save()
						return Response(status=status.HTTP_200_OK)
			except:
				return Response(status=status.HTTP_404_NOT_FOUND)

	def post(self, request,store_id=None):
		usser = CustomUser.objects.get(email=request.user.email)
		if(usser.role != "MERCHANT"):
			return Response({"message":"That's an illegal move"},status=status.HTTP_403_FORBIDDEN)
		try:
			objj = UpdateStoreSerializer(data=json.loads(request.POST['data']))
			if not objj.is_valid():
				print(UpdateStoreSerializer.errors)
				return Response({"message": "That's an illegal move"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			img = request.FILES['logo']
			newStore = Store()
			newStore.name = objj.data['name']
			newStore.description = objj.data['description']
			newStore.contactNumber = objj.data['contactNumber']
			newStore.start = objj.data['start']
			newStore.end = objj.data['end']
			newStore.sundayOpen = objj.data['sundayOpen']
			newStore.mondayOpen = objj.data['mondayOpen']
			newStore.tuesdayOpen = objj.data['tuesdayOpen']
			newStore.wednesdayOpen = objj.data['wednesdayOpen']
			newStore.thursdayOpen = objj.data['thursdayOpen']
			newStore.fridayOpen = objj.data['fridayOpen']
			newStore.saturdayOpen = objj.data['saturdayOpen']
			newStore.owner = request.user
			newStore.logo = img
			newStore.save()
			return Response(status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class StoreImageChangeView(APIView):
	parser_classes = (MultiPartParser,)
	permission_classes = (IsAuthenticated,)
	def post(self, request,store_id=None):
		if(store_id==None):
			return Response({"message":"That's an illegal move"}, status=status.HTTP_403_FORBIDDEN)
		else:
			try:
				storeData = Store.objects.get(store_id=store_id)
				if(storeData.owner.id != request.user.id):
					return Response({"message":"User doesn't own the store"}, status=status.HTTP_403_FORBIDDEN)
				else:
					tt = request.FILES['logo']
					storeData.logo = tt
					storeData.save()
					return Response({"message": "OK"}, status=status.HTTP_200_OK)
			except:
				return Response({"message":"Store ID Doesn't exist"}, status=status.HTTP_403_FORBIDDEN)

