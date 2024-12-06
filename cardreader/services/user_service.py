from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from cardreader.api.serializers import UserSerializer
from cardreader.models import User


class UserService:

    def signup(self, serializer:UserSerializer):
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            raise ValueError('Email already registered')

        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()
        return user
