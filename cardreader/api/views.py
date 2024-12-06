from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from torch.distributed import group

from .serializers import UserSerializer, IdCardSerializer, HealthCareCardSerializer, StudentCardSerializer, \
    GroupListSerializer, GroupCreateSerializer, GroupDetailSerializer, InvitationSerializer, AddCardsSerializer
from cardreader.models import IdCard, StudentCard, HealthCareCard, Group, Invitation
from rest_framework import status

from ..services.converter_service import ConverterService
from ..services.healthcarecard_reader_service import HealthCareCardReaderService
from ..services.idcard_reader_service import IdCardReaderService
from ..services.studentcard_reader_service import StudentCardReaderService
from ..services.user_service import UserService


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    user_service = UserService()
    if serializer.is_valid():
        try:
            user = user_service.signup(serializer)
        except ValueError as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(access),
        })

    return Response({'errors':serializer.errors, 'code':status.HTTP_400_BAD_REQUEST})



@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated])
def healthcare_card_view(request, id=None, group_id = None):
    user = request.user

    if request.method == 'GET':
        cards = HealthCareCard.objects.filter(user=user)
        serializer = HealthCareCardSerializer(cards, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        image_front = request.FILES['imageFront']
        service = HealthCareCardReaderService(image_front, user)
        card = service.read_data()
        card.save()
        return Response({'message': 'Healthcare card added successfully'}, status=201)

    elif request.method == 'PUT' and id:
        card = get_object_or_404(HealthCareCard, id=id, user=user)
        serializer = HealthCareCardSerializer(card, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and id and group_id:
        card = get_object_or_404(HealthCareCard, id=id, user=user)
        group = Group.objects.get(id=group_id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not group.healthCareCards.contains(card):
            return Response({'error': 'Card not inside group'}, status=status.HTTP_400_BAD_REQUEST)

        group.healthCareCards.remove(card)
        group.save()

    elif request.method == 'DELETE' and id:
        card = get_object_or_404(HealthCareCard, id=id, user=user)
        card.delete()
        return Response({'message': 'Healthcare card deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated])
def student_card_view(request, id=None, group_id = None):
    user = request.user
    if request.method == "GET":
        cards = StudentCard.objects.filter(user=user)
        serializer = StudentCardSerializer(cards, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == "POST":
        image_front = request.FILES['imageFront']
        image_back = request.FILES['imageBack']


        service = StudentCardReaderService(image_front,image_back, user)

        card = service.read_data()
        card.save()
        return Response({'message': 'Student card added successfully'}, status=201)

    elif request.method == 'PUT' and id:
        card = get_object_or_404(StudentCard, id=id, user=user)
        serializer = StudentCardSerializer(card, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and id and group_id:
        card = get_object_or_404(StudentCard, id=id, user=user)
        group = Group.objects.get(id=group_id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not group.studentCards.contains(card):
            return Response({'error': 'Card not inside group'}, status=status.HTTP_400_BAD_REQUEST)

        group.studentCards.remove(card)
        group.save()

    elif request.method == 'DELETE' and id:
        card = get_object_or_404(StudentCard, id=id, user=user)
        card.delete()
        return Response({'message': 'Student card deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated])
def idcard_view(request, id=None, group_id = None):
    user = request.user

    if request.method == 'POST':
        image_front = request.FILES['imageFront']
        image_back = request.FILES['imageBack']
        service = IdCardReaderService(image_front, image_back, user)
        card = service.read_data()
        card.save()

        return Response({'message': 'ID card added successfully'}, status=201)

    elif request.method == 'GET':
        # Handle retrieving the ID cards for the user
        cards = IdCard.objects.filter(user=user)
        serializer = IdCardSerializer(cards, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT' and id:
        card = get_object_or_404(IdCard, id=id, user=user)
        serializer = IdCardSerializer(card, data=request.data, partial=True, context={'request': request})
        print(serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and id and group_id:
        card = get_object_or_404(StudentCard, id=id, user=user)
        group = Group.objects.get(id=group_id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not group.studentCards.contains(card):
            return Response({'error': 'Card not inside group'}, status=status.HTTP_400_BAD_REQUEST)

        group.studentCards.remove(card)
        group.save()

    elif request.method == 'DELETE' and id:
        card = get_object_or_404(IdCard, id=id, user=user)
        card.delete()
        return Response({'message': 'ID card deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_idcard_base64(request):
    converter_service = ConverterService()
    image_front = converter_service.base64_to_file(request.data['imageFront'])
    image_back = converter_service.base64_to_file(request.data['imageBack'])
    service = IdCardReaderService(image_front, image_back, request.user)
    card = service.read_data()
    card.save()
    return Response({'message': 'ID card added successfully'}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_healthcare_card_base64(request):
    converter_service = ConverterService()
    image_front = converter_service.base64_to_file(request.data['imageFront'])
    service = HealthCareCardReaderService(image_front, request.user)
    card = service.read_data()
    card.save()
    return Response({'message': 'Healthcare card added succesfuly'}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_student_card_base64(request):
    converter_service = ConverterService()
    image_front = converter_service.base64_to_file(request.data['imageFront'])
    image_back = converter_service.base64_to_file(request.data['imageBack'])
    service = StudentCardReaderService(image_front, image_back, request.user)
    card = service.read_data()
    card.save()
    return Response({'message': 'Student ID card added successfully'}, status=201)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def group_view(request, id=None):
    if request.method == 'POST':
        serializer = GroupCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            group = serializer.save()
            return Response({'id': group.id, 'name': group.name}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET' and id:
        user = request.user
        group = Group.objects.get(id=id)
        if not group.users.contains(user):
            return Response({'message': 'User not in group'}, status=status.HTTP_404_NOT_FOUND)
        serializer = GroupDetailSerializer(group, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'GET':
        # Get the list of groups the user is part of
        user = request.user
        groups = Group.objects.filter(users=user)  # Get all groups the user is a part of
        serializer = GroupListSerializer(groups, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_invitations(request):
    user = request.user
    invitations = Invitation.objects.filter(receiver=user, status='pending')
    serializer = InvitationSerializer(invitations, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_invitation(request, invitation_id, action):
    user = request.user
    try:
        invitation = Invitation.objects.get(id=invitation_id)
    except Invitation.DoesNotExist:
        return Response({'message': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)

    if invitation.receiver.id != user.id:
        return Response({'message': 'User not in invitation'}, status=status.HTTP_403_FORBIDDEN)
    if invitation.status != 'pending':
        return Response({'message': 'Invitation already answered'}, status=status.HTTP_400_BAD_REQUEST)
    if action not in ['accept', 'reject']:
        return Response({'message': 'Invitation action not supported'}, status=status.HTTP_400_BAD_REQUEST)

    if action == 'accept':
        invitation.status = 'accepted'
        invitation.group.users.add(user)
        invitation.save()
        return Response({'message': 'Invitation accepted'}, status=status.HTTP_200_OK)

    if action == 'reject':
        invitation.status = 'rejected'
        invitation.save()
        return Response({'message': 'Invitation rejected'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_user(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

    data = {
        "email": request.data.get("email"),
    }

    serializer = InvitationSerializer(data=data, context={"request": request, "group": group})
    if serializer.is_valid():
        serializer.save(sender=request.user, group=group)
        return Response({"success": "Invitation sent successfully."}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_cards_to_group(request, group_id):
    serializer = AddCardsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Retrieve the group by group_id
    group = get_object_or_404(Group, id=group_id)

    # Process ID Cards
    id_card_ids = serializer.validated_data.get("selectedIdCardIds", [])
    if id_card_ids:
        id_cards = IdCard.objects.filter(id__in=id_card_ids)
        group.idCards.add(*id_cards)

    # Process Student Cards
    student_card_ids = serializer.validated_data.get("selectedStudentCardIds", [])
    if student_card_ids:
        student_cards = StudentCard.objects.filter(id__in=student_card_ids)
        group.studentCards.add(*student_cards)

    # Process HealthCare Cards
    health_care_card_ids = serializer.validated_data.get("selectedHealthCareCardIds", [])
    if health_care_card_ids:
        health_care_cards = HealthCareCard.objects.filter(id__in=health_care_card_ids)
        group.healthCareCards.add(*health_care_cards)

    return Response({"message": "Cards successfully added to the group"}, status=status.HTTP_200_OK)




