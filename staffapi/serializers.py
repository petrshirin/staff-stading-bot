from rest_framework import serializers
from .models import *


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'name')


class RestaurantBranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = RestaurantBranch
        fields = ('name', 'city', 'address')


class MinimalStudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=255, allow_null=True)
    second_name = serializers.CharField(max_length=255, allow_null=True)
    third_name = serializers.CharField(max_length=255, allow_null=True)
    actions = serializers.IntegerField(min_value=0, allow_null=True)


class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    token = serializers.CharField(max_length=32, allow_null=True)
    position = serializers.CharField(max_length=255, allow_null=True)
    first_name = serializers.CharField(max_length=255, allow_null=True)
    second_name = serializers.CharField(max_length=255, allow_null=True)
    third_name = serializers.CharField(max_length=255, allow_null=True)
    date_work_start = serializers.DateField(allow_null=True)
    date_birth = serializers.DateField(allow_null=True)
    phone = serializers.CharField(max_length=15, min_length=9, allow_null=True)
    email = serializers.EmailField(allow_null=True)
    profile_photo = serializers.ImageField(allow_null=True)


class OpenedQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question = serializers.CharField(allow_null=True)
    answer = serializers.CharField(allow_null=True)


class AnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    complete_theory = serializers.BooleanField(allow_null=True)
    complete_test = serializers.BooleanField(allow_null=True)
    complete_opened_questions = serializers.BooleanField(allow_null=True)
    opened_questions = serializers.ListField(child=serializers.DictField(), allow_empty=True)


class AnswerPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentTheoryTopic
        fields = ('complete_opened_questions',)
