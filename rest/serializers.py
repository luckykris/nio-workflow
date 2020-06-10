from django.contrib.auth.models import Group
from .models import *
from rest_framework import serializers
import traceback
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


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
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


class WorkflowSerializer(serializers.ModelSerializer):

    def create(self, validated_data):

        try:
            instance = Workflow.objects.create(**validated_data)
            instance.create_start_step()
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                    'Got a `TypeError` when calling `%s.%s.create()`. '
                    'This may be because you have a writable field on the '
                    'serializer class that is not a valid argument to '
                    '`%s.%s.create()`. You may need to make the field '
                    'read-only, or override the %s.create() method to handle '
                    'this correctly.\nOriginal exception was:\n %s' %
                    (
                        self.Meta.model.__name__,
                        self.Meta.model._default_manager.name,
                        self.Meta.model.__name__,
                        self.Meta.model._default_manager.name,
                        self.__class__.__name__,
                        tb
                    )
            )
            raise TypeError(msg)

        return instance

    class Meta:
        model = Workflow
        fields = '__all__'