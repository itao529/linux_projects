# Create your views here.
import os
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from configures.models import Configures
from envs.models import Envs
from interfaces.models import Interfaces
from interfaces.serializer import InterfaceModelSerializer, InterfaceNameSerializer, InterfaceRunSerializer

from interfaces.utils import get_count_by_project
from learnDjango import settings
from projects.serializer import ProjectNameSerializer
from testcases.models import TestCases
from utils import common


class InterfaceViewSet(ModelViewSet):
    """
     create:
    创建接口

    retrieve:
    获取接口详情数据

    update:
    完整更新接口

    partial_update:
    部分更新接口

    destroy:
    删除接口

    list:
    获取接口列表数据

    names:
    获取所有接口名称
    """
    queryset = Interfaces.objects.all()
    serializer_class = InterfaceModelSerializer
    ordering_fields = ['name']
    filterset_fields = ['id', 'name']

    @action(methods=['get'], detail=False)
    def names(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='configs')
    def configures(self, request, pk=None):
        configures_models = Configures.objects.filter(interface_id=pk, is_delete=False)
        one_list = []
        for obj in configures_models:
            one_list.append({
                'id': obj.id,
                'name': obj.name
            })
        return Response(data=one_list)

    @action(methods=['get'], detail=True, url_path='testcases')
    def testcases(self, request, pk=None):
        testcases_models = TestCases.objects.filter(interface_id=pk, is_delete=False)
        one_list = []
        for obj in testcases_models:
            one_list.append({
                'id': obj.id,
                'name': obj.name,
                'status_code': 200
            })
        return Response(data=one_list)

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        res.data["results"] = get_count_by_project(res.data.get("results"))
        return res

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(methods=['post'], detail=True)
    def run(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        datas = serializer.validated_data
        env_id = datas.get('env_id')  # 获取环境变量env_id

        # 创建测试用例所在目录名
        testcase_dir_path = os.path.join(settings.SUITES_DIR,
                                         datetime.strftime(datetime.now(), "%Y%m%d%H%M%S%f"))
        if not os.path.exists(testcase_dir_path):
            os.mkdir(testcase_dir_path)

        env = Envs.objects.filter(id=env_id, is_delete=False).first()
        testcase_objs = TestCases.objects.filter(is_delete=False, interface=instance)
        if not testcase_objs.exists():  # 如果此接口下没有用例, 则无法运行
            data_dict = {
                "detail": "此接口下无用例, 无法运行!"
            }
            return Response(data_dict, status=status.HTTP_400_BAD_REQUEST)

        for one_obj in testcase_objs:
            common.generate_testcase_files(one_obj, env, testcase_dir_path)

        # 运行用例
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        if self.action == "names":
            return ProjectNameSerializer
        if self.action == "run":
            return InterfaceRunSerializer
        return self.serializer_class
