from rest_framework import serializers
from cardreader.models import User, IdCard, HealthCareCard, StudentCard, Group, Invitation
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']

class IdCardSerializer(serializers.ModelSerializer):
    image_front_url = serializers.SerializerMethodField()
    image_back_url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = IdCard
        exclude = ['imageFront', 'imageBack']

    def get_image_front_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.imageFront.url) if obj.imageFront else None

    def get_image_back_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.imageBack.url) if obj.imageBack else None

class HealthCareCardSerializer(serializers.ModelSerializer):
    image_front_url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = HealthCareCard
        exclude = ['imageFront']

    def get_image_front_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.imageFront.url) if obj.imageFront else None

class StudentCardSerializer(serializers.ModelSerializer):
    image_front_url = serializers.SerializerMethodField()
    image_back_url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = StudentCard
        exclude = ['imageFront', 'imageBack']

    def get_image_front_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.imageFront.url) if obj.imageFront else None

    def get_image_back_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.imageBack.url) if obj.imageBack else None


class GroupListSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer()
    users = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'createdAt', 'createdBy', 'users']
        read_only_fields = ['createdBy', 'createdAt'] # Only expose the name field for input

class GroupDetailSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer()
    users = UserSerializer(many=True)

    idCards = IdCardSerializer(many=True)
    healthCareCards = HealthCareCardSerializer(many=True)
    studentCards = StudentCardSerializer(many=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'createdAt', 'createdBy', 'users', 'idCards', 'healthCareCards', 'studentCards']
        read_only_fields = ['createdBy', 'createdAt'] # Only expose the name field for input



class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']  # Only 'name' field is required for creation

    def create(self, validated_data):
        # Get the user from the request (assumed to be authenticated)
        user = self.context['request'].user

        # Create the group instance with only the name and the user for createdBy and users
        group = Group.objects.create(
            name=validated_data['name'],
            createdBy=user,
        )

        # Add the user to the users field (many-to-many relationship)
        group.users.add(user)

        return group

class InvitationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    group = GroupListSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'sender', 'receiver', 'group', 'email']
        extra_kwargs = {
            'receiver': {'read_only': True},  # Ensure receiver is read-only and only set via email
            'sender': {'read_only': True},  # Make sender read-only as it’s derived from the request user
        }

    def validate(self, data):
        email = data.get("email")
        group = self.context['group']

        # Check if the receiver exists
        try:
            receiver = User.objects.get(email=email)
            data['receiver'] = receiver
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        # Check if the user is already in the group
        if group.users.filter(id=receiver.id).exists():
            raise serializers.ValidationError("User is already a member of this group.")

        # Check if an invitation already exists
        if Invitation.objects.filter(receiver=receiver, group=group).exists():
            raise serializers.ValidationError("An invitation to this group has already been sent to this user.")

        return data

    def create(self, validated_data):
        validated_data.pop('email', None)  # Remove email from validated_data before saving
        return super().create(validated_data)

class AddCardsSerializer(serializers.Serializer):
    selectedIdCardIds = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    selectedStudentCardIds = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    selectedHealthCareCardIds = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )