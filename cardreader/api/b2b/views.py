from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from cardreader.api.b2b.serializers import CompanySerializer, B2BIdCardSerializer, B2BHealthCareCardSerializer, \
    B2BStudentCardSerializer
from cardreader.api.serializers import IdCardSerializer, HealthCareCardSerializer, StudentCardSerializer
from cardreader.models import Company
from cardreader.services.healthcarecard_reader_service import HealthCareCardReaderService
from cardreader.services.idcard_reader_service import IdCardReaderService
from cardreader.services.studentcard_reader_service import StudentCardReaderService


@api_view(['POST'])
@permission_classes([AllowAny])
def create_company(request):
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        # Create a new company
        company = serializer.save()

        # Generate an API key
        api_key_obj, api_key = APIKey.objects.create_key(name=company.name)
        company.apiKey = api_key_obj
        company.save()

        return Response(
            {
                "message": "Company created successfully.",
                "apiKey": api_key,  # Send API key to client for storage
            },
            status=201,
        )

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([HasAPIKey])
def read_id_card(request):
    key = request.headers.get("Authorization").split()[1]
    # Get the APIKey instance
    api_key = APIKey.objects.get_from_key(key)
    # Get the company associated with the API key
    company = Company.objects.get(apiKey=api_key)

    image_front = request.FILES['imageFront']
    image_back = request.FILES['imageBack']
    service = IdCardReaderService(image_front, image_back)
    card = service.read_data()
    card_serializer = B2BIdCardSerializer(card)

    company.owedMoney += 10
    company.save()
    return Response(card_serializer.data)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([HasAPIKey])
def read_healthcare_card(request):
    key = request.headers.get("Authorization").split()[1]
    # Get the APIKey instance
    api_key = APIKey.objects.get_from_key(key)
    # Get the company associated with the API key
    company = Company.objects.get(apiKey=api_key)

    image_front = request.FILES['imageFront']
    service = HealthCareCardReaderService(image_front)
    card = service.read_data()
    card_serializer = B2BHealthCareCardSerializer(card)

    company.owedMoney += 10
    company.save()
    return Response(card_serializer.data)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([HasAPIKey])
def read_student_card(request):
    key = request.headers.get("Authorization").split()[1]
    # Get the APIKey instance
    api_key = APIKey.objects.get_from_key(key)
    # Get the company associated with the API key
    company = Company.objects.get(apiKey=api_key)

    image_front = request.FILES['imageFront']
    image_back = request.FILES['imageBack']
    service = StudentCardReaderService(image_front, image_back)
    card = service.read_data()
    card_serializer = B2BStudentCardSerializer(card)

    company.owedMoney += 10
    company.save()
    return Response(card_serializer.data)