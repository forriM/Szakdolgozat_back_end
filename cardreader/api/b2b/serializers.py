from rest_framework import serializers

from cardreader.models import Company, IdCard, HealthCareCard


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'vatNumber', 'contactEmail', 'owedMoney']
        read_only_fields = ['owedMoney']  # owedMoney is calculated based on API usage

    def create(self, validated_data):
        # Set initial owedMoney to 0
        validated_data['owedMoney'] = 0.00
        return super().create(validated_data)

class B2BIdCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdCard
        exclude = ['imageFront', 'imageBack', 'id', 'user']

class B2BStudentCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdCard
        exclude = ['imageFront', 'imageBack', 'id', 'user']

class B2BHealthCareCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCareCard
        exclude = ['imageFront', 'id', 'user']