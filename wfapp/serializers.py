from django.contrib.auth.models import Group
from .models import *
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer


class HttpHookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HttpHook
        fields = '__all__'


class HookSerializer(serializers.ModelSerializer):
    model_serializer_mapping = {
        HttpHook: HttpHookSerializer,
    }


class StepDefineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepDefine
        fields = '__all__'


class WorkflowTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowTemplate
        fields = '__all__'


class WorkflowTemplateDetailSerializer(serializers.ModelSerializer):
    step_defines = StepDefineSerializer(many=True, required=False)

    class Meta:
        model = WorkflowTemplate
        fields = '__all__'