import json
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
# from mptt.templatetags.mptt_tags import cache_tree_children
# from django.views.decorators.http import require_http_methods
# from rest_framework.views import APIView
# from django.http.response import JsonResponse
# from rest_framework import permissions
# from rest_framework_simplejwt import authentication
from rest_framework.filters import BaseFilterBackend, OrderingFilter, SearchFilter
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_extensions.mixins import DetailSerializerMixin


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk
        })


class StepDefineViewSet(viewsets.ModelViewSet):
    # authentication_classes = (authentication.JWTAuthentication,)
    #permission_classes = (permissions.IsAuthenticated,)
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = StepDefine.objects.all()
    serializer_class = StepDefineSerializer
    filter_backends = (OrderingFilter,)

    @action(methods=['post', 'delete'], detail=True)
    def link(self, request, *args, **kwargs):
        obj = self.get_object()
        js = json.loads(request.body)
        to = js.get('to')
        t = js.get('type')
        t_low = t.lower()
        to_obj = StepDefine.objects.get(id=to)
        if t_low == 'commit':
            q_obj = getattr(obj, 'commit_stepdefines')
            # obj.commit_stepdefines.add(to_obj)
        elif t_low == 'reject':
            q_obj = getattr(obj, 'reject_stepdefines')
            # obj.reject_stepdefines.add(to_obj)
        elif t_low == 'success':
            q_obj = getattr(obj, 'success_stepdefines')
            # obj.success_stepdefines.add(to_obj)
        elif t_low == 'fail':
            q_obj = getattr(obj, 'fail_stepdefines')
            # obj.fail_stepdefines.add(to_obj)
        else:
            raise KeyError("no such type")
        print(request.method)
        if request.method.lower() == 'post':
            q_obj.add(to_obj)
        else:
            q_obj.remove(to_obj)
        return Response({'success', True})


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    # authentication_classes = (authentication.JWTAuthentication,)
    #permission_classes = (permissions.IsAuthenticated,)
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    serializer_detail_class = WorkflowTemplateDetailSerializer
    # queryset_detail = queryset.prefetch_related('workflowtemplate')
    #filter_backends = (OrderingFilter,)


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    serializer_detail_class = WorkflowTemplateDetailSerializer
    # queryset_detail = queryset.prefetch_related('workflowtemplate')

    @action(methods=['get'], detail=True)
    def steps(self, request, *args, **kwargs):
        w = self.get_object()
        serializer_context = {
            'request': request,
        }
        serializer = StepSerializer(w.steps(), context=serializer_context,  many=True)
        return Response(serializer.data)