from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser
from users.models import CustomUser, Store, StoreItem, Cart, CartItems
from .serializers import CustomUserSerializer, UpdateUserSerializer, StoreSerializer, UpdateStoreSerializer, CreateStoreSerializer, StoreItemSerializer, CreateStoreItemSerializer, CartItemSerializer
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

class StoreItemImageChangeView(APIView):
	parser_classes = (MultiPartParser,)
	permission_classes = (IsAuthenticated,)
	def post(self, request,storeitem_id=None):
		if(storeitem_id==None):
			return Response({"message":"That's an illegal move"}, status=status.HTTP_403_FORBIDDEN)
		else:
			try:
				storeData = StoreItem.objects.get(storeitem_id=storeitem_id)
				if(storeData.store.owner.id != request.user.id):
					return Response({"message":"User doesn't own the store"}, status=status.HTTP_403_FORBIDDEN)
				else:
					tt = request.FILES['logo']
					storeData.logo = tt
					storeData.save()
					return Response({"message": "OK"}, status=status.HTTP_200_OK)
			except:
				return Response({"message":"Store Item ID Doesn't exist"}, status=status.HTTP_403_FORBIDDEN)


class StoreItemsView(APIView):
	permission_classes = (IsAuthenticated,)
	def get(self, request,store_id=None):
		if store_id==None:
			return Response({"message": "That's an illegal move"}, status=status.HTTP_403_FORBIDDEN)
		else:
			try:
				store = Store.objects.get(store_id=store_id)
				storeitems = StoreItem.objects.filter(store=store)
				return Response(StoreItemSerializer(storeitems,many=True).data)
			except Store.DoesNotExist:
				return Response({"message": "Store ID Doesn't exist"}, status=status.HTTP_403_FORBIDDEN)
			except:
				return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateOrUpdateStoreItemsView(APIView):
	parser_classes = (MultiPartParser, FormParser, JSONParser)
	permission_classes = (IsAuthenticated,)
	#Get a particular item
	def get(self, request,store_id=None,storeitem_id=None):
		if store_id==None or storeitem_id==None:
			return Response({"message": "That's an illegal move"}, status=status.HTTP_403_FORBIDDEN)
		else:
			try:
				store = Store.objects.get(store_id=store_id)
				storeitem = StoreItem.objects.filter(store=store,storeitem_id=storeitem_id)
				return Response(StoreItemSerializer(storeitem).data)
			except Store.DoesNotExist:
				return Response({"message": "Store ID Doesn't exist"}, status=status.HTTP_403_FORBIDDEN)
			except StoreItem.DoesNotExist:
				return Response({"message": "Store Item ID Doesn't exist"}, status=status.HTTP_403_FORBIDDEN)
			except:
				return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	#Create a new item in store
	def post(self, request,store_id=None,storeitem_id=None):
		if store_id==None:
			return Response({"message": "Not possible"}, status=status.HTTP_403_FORBIDDEN)
		else:
			#Verify ownership
			try:
				store = Store.objects.get(store_id=store_id)
				if not store.owner.id == request.user.id:
					return Response({"message": "You do not own the store"}, status=status.HTTP_404_NOT_FOUND)
				else:
					#Validate store item object
					objj = CreateStoreItemSerializer(data=json.loads(request.POST['data']))
					if not objj.is_valid():
						print(UpdateStoreSerializer.errors)
						return Response({"message": "That's an illegal move"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
					else:
						new_store_object = StoreItem()
						new_store_object.store = store
						new_store_object.logo = request.FILES['logo']
						new_store_object.name = objj.data['name']
						new_store_object.description = objj.data['description']
						new_store_object.price = objj.data['price']
						new_store_object.save()
						return Response(status=status.HTTP_200_OK)
			except Store.DoesNotExist:
				return Response({"message": "Store ID Doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

	# Edit an item item in store
	def put(self, request, store_id=None, storeitem_id=None):
			if store_id == None or storeitem_id==None:
				return Response({"message": "Not possible"}, status=status.HTTP_403_FORBIDDEN)
			else:
				# Verify ownership
				try:
					storeitem = StoreItem.objects.get(storeitem_id=storeitem_id)
					if not storeitem.store.owner.id == request.user.id:
						return Response({"message": "You don't own this"}, status=status.HTTP_403_FORBIDDEN)
					else:
						objj = CreateStoreItemSerializer(data=request.data)
						if not objj.is_valid():
							print(objj.errors)
							return Response({"message": "Bad data"}, status=status.HTTP_403_FORBIDDEN)
						else:
							storeitem.name = objj.data['name']
							storeitem.description = objj.data['description']
							storeitem.price = objj.data['price']
							storeitem.save()
							return Response(status=status.HTTP_200_OK)
				except StoreItem.DoesNotExist:
					return Response({"message": "Store Not Found"}, status=status.HTTP_403_FORBIDDEN)


class CartItemsView(APIView):
	permission_classes = (IsAuthenticated,)
	def post(self, request):
		#Validate incoming request
		#Validate Body
		cartAddObj = CartItemSerializer(data=request.data)
		if not cartAddObj.is_valid():
			return Response(cartAddObj.errors, status=status.HTTP_400_BAD_REQUEST)
		else:
			storeid = cartAddObj.data['storeID']
			productid = cartAddObj.data['productID']
			try:
				store = Store.objects.get(store_id=storeid)
				product = StoreItem.objects.get(item_id=productid)
				if product.store.store_id != store.id:
					return Response({"message":"Product isn't owned by store"})
				else:
					usser = CustomUser.objects.get(id=request.user.id)
					cart = Cart.objects.get_or_create(user=usser, store=store)[0]
					cartItem = CartItems.objects.get_or_create(cart=cart, item=product)[0]
					cartItem.quantity = cartAddObj.data['quantity']
					cartItem.save()
					if(cartItem.quantity == 0):
						cartItem.delete()
					return Response(status=status.HTTP_200_OK)
			except Store.DoesNotExist:
				return Response({"message":"Store doesn't exist"})
			except StoreItem.DoesNotExist:
				return Response({"message":"Store doesn't exist"})





