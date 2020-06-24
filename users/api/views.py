from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from .serializers import CustomUserSerializer, UpdateUserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token

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
		userFromToken = CustomUser.objects.get(email=request.user.email)
		userFromDataSerializer = UpdateUserSerializer(data = request.data)
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
			return Response(userFromToken, status=status.HTTP_200_OK)






