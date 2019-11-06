# Create your views here.

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet

from interfaces.models import Interfaces
from interfaces.serializer import InterfaceInfoSerializer
from projects.models import Projects
from projects.serializer import ProjectModelSerializer


class ProjectsViewSet(ModelViewSet):
    """
     list:
     返回项目（多个）列表数据

     create:
     创建项目

     retrieve:
     返回项目（单个）详情数据

     update:
     更新（全）项目

     partial_update:
     更新（部分）项目

     destroy:
     删除项目

     names:
     返回所有项目ID和名称

     interfaces:
     返回某个项目的所有接口信息（ID和名称）
     """
    queryset = Projects.objects.all()
    serializer_class = ProjectModelSerializer
    ordering_fields = ('id', 'name')
    filterset_fields = ['id', 'name']
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=True, url_path='interfaces')
    def interfaces(self, request, pk=None):
        interface_models = Interfaces.objects.filter(project_id=pk, is_deleted=False)
        one_list = []
        for obj in interface_models:
            one_list.append({
                'id': obj.id,
                'name': obj.name
            })
        return Response(data=one_list)

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(methods=['get'], detail=True)
    def interface_info(self, request, *args, **kwargs):
        project_model = self.get_object()
        # serializer = self.get_serializer(instance=project_model, many=True)
        # return Response(serializer.data.get("interfaces"))
        interfaces_name = self.get_serializer(instance=project_model).data.get("interfaces")
        interface_model = Interfaces.objects.filter(name__in=interfaces_name)
        serializer = InterfaceInfoSerializer(instance=interface_model, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     datas = serializer.data

        #     return self.get_paginated_response(datas)

        serializer = self.get_serializer(queryset, many=True)

        datas = serializer.data
        return Response(datas)
