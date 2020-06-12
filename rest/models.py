from django.db import models, transaction
from concurrency.fields import IntegerVersionField
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
import requests
from .toolkits import gen_uuid


# 一致性基类
class BaseConcurrentModel(models.Model):
    _version = IntegerVersionField()
    _ctime = models.DateTimeField(auto_now_add=True)
    _mtime = models.DateTimeField(auto_now=True)


# hook验证配置基类
class HookAuth(BaseConcurrentModel):
    name = models.CharField(primary_key=True, max_length=255)
    objects = PolymorphicManager()


# hook验证配置 - token
class TokenAuth(HookAuth):
    token = models.CharField(max_length=255)
    header = models.CharField(max_length=255, default='Authorization')
    prefix = models.CharField(max_length=255, default='Token')


# hook配置基类
class Hook(PolymorphicModel, BaseConcurrentModel):
    name = models.CharField(primary_key=True, max_length=255)
    objects = PolymorphicManager()


# hook配置基类 - http hook
class HttpHook(Hook):
    methods = (('get', 'get'), ('put', 'put'), ('post', 'post'), ('delete', 'delete'))
    api = models.CharField(max_length=255)
    method = models.CharField(choices=methods, max_length=255)
    auth = models.ForeignKey(HookAuth, null=True, on_delete=models.SET_NULL)

    def run(self):
        cls_method = getattr(requests, self.method)
        if cls_method is None:
            raise KeyError("no method is named %r in requests module" % self.method)


# 流程模版
class WorkflowTemplate(BaseConcurrentModel):
    name = models.CharField(max_length=255)
    start_step_define = models.ForeignKey('StepDefine', on_delete=models.SET_NULL, null=True)


# 流程步骤定义
class StepDefine(BaseConcurrentModel):
    workflow_template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name="step_defines")
    name = models.CharField(max_length=255)
    before_init = models.ManyToManyField(Hook, default=[], related_name='before_init_hook', blank=True)
    after_init = models.ManyToManyField(Hook, default=[], related_name='after_init_hook', blank=True)
    before_commit = models.ManyToManyField(Hook, default=[], related_name='before_commit_hook', blank=True)
    after_commit = models.ManyToManyField(Hook, default=[], related_name='after_commit_hook', blank=True)
    before_reject = models.ManyToManyField(Hook, default=[], related_name='before_reject_hook', blank=True)
    after_reject = models.ManyToManyField(Hook, default=[], related_name='after_reject_hook', blank=True)
    before_submit = models.ManyToManyField(Hook, default=[], related_name='before_submit_hook', blank=True)
    after_submit = models.ManyToManyField(Hook, default=[], related_name='after_submit_hook', blank=True)
    before_success_submit = models.ManyToManyField(Hook, default=[], related_name='before_success_submit_hook', blank=True)
    after_success_submit = models.ManyToManyField(Hook, default=[], related_name='after_success_submit_hook', blank=True)
    before_fail_submit = models.ManyToManyField(Hook, default=[], related_name='before_fail_submit_hook', blank=True)
    after_fail_submit = models.ManyToManyField(Hook, default=[], related_name='after_fail_submit_hook', blank=True)
    success_stepdefines = models.ManyToManyField('StepDefine', default=[], related_name='success_stepdefine', blank=True)
    commit_stepdefines = models.ManyToManyField('StepDefine', default=[], related_name='commit_stepdefine', blank=True)
    fail_stepdefines = models.ManyToManyField('StepDefine', default=[], related_name='fail_stepdefine', blank=True)
    reject_stepdefines = models.ManyToManyField('StepDefine', default=[], related_name='reject_stepdefine', blank=True)

    def is_end(self):
        return len(self.commit_steps) + len(self.success_steps) < 1

    readonly_fields = ('is_end',)

    def require_steps(self):
        return self.objects.filter(
            models.Q(success_stepdefines__in=self) |
            models.Q(commit_stepdefines__in=self) |
            models.Q(fail_stepdefines__in=self) |
            models.Q(reject_stepdefines__in=self)
        ).all()


# 步骤参数定义
class ArgumentDefine(BaseConcurrentModel):
    argument_types = (('int', 'int'), ('string', 'string'), ('choice', 'choice'), ('text', 'text'))
    name = models.CharField(max_length=255)
    argument_type = models.CharField(choices=argument_types, max_length=255)
    extra_args = JSONField(default={})
    step_define = models.ForeignKey(StepDefine, on_delete=models.CASCADE, related_name='arguments')


#  实际工单
class Workflow(models.Model):
    workflow_status_choices = (
        ('submit', 'submit'), # 提交
        ('revoke', 'revoke'), # 撤回
        ('close', 'close'), # 完成关闭
        ('terminate', 'terminate'), # 中止
        ('processing', 'processing'), # 流程中
    )
    id = models.UUIDField(auto_created=True, primary_key=True, default=gen_uuid, editable=False)
    _version = IntegerVersionField()
    _ctime = models.DateTimeField(auto_now_add=True)
    _mtime = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    workflow_status = models.CharField(choices=workflow_status_choices, max_length=255, default='submit')
    arguments = JSONField(default={})
    workflow_template = models.ForeignKey(WorkflowTemplate, on_delete=models.PROTECT)

    # TODO: 判断整体工单状态, 变更工单的状态
    def if_close(self):
        pass

    # TODO: 判断整体工单状态, 变更工单的状态
    def if_terminate(self):
        pass

    def create_start_step(self):
        Step.objects.create(
            step_define=self.workflow_template.start_step_define,
            workflow=self,
            arguments=self.arguments,
            step_status='waiting',
            from_step=None
        )

    def steps(self):
        steps = Step.objects.filter(workflow=self)
        return steps


# 实际工单步骤
class Step(BaseConcurrentModel):
    """
        TODO:
        工单步骤状态机:
        commit流程: waiting -> running -> success
                                      -> fail
        approve流程：waiting -> success
                            -> reject
    """
    step_status_choices = (
        ('waiting', 'waiting'),
        ('running', 'running'),
        ('reject', 'reject'),
        ('success', 'success'),
        ('fail', 'fail'),
    )
    step_define = models.ForeignKey(StepDefine, on_delete=models.PROTECT)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    arguments = JSONField(default={})
    step_status = models.CharField(choices=step_status_choices, max_length=255, default='waiting')
    step_return = JSONField(default={})
    from_step = models.ForeignKey('Step', null=True, on_delete=models.PROTECT)

    # 批准通过流程
    def approve(self):
        with transaction.atomic():
            # TODO:  事务里执行 hook, 根据StepDefine里定义的成功后的下一步，进行步骤创建, 如果没有后续步骤，则检测工单所有状态是否完结，来决定是否close工单
            print(self.step_define.success_stepdefines.all())
            for s in self.step_define.success_stepdefines.all():
                Step.objects.create(step_define=s, workflow=self.workflow, arguments=self.arguments)
            self.step_status = 'success'

    # 执行流程 触发hook 改变步骤状态， commit后外界通过回调，改变fail跟success状态并继续后续步骤. commit在api侧的实现需要加工返回可直接调用的http链接
    def commit(self):
        with transaction.atomic():
            # TODO:  事务里执行 hook
            pass

    #

    # 拒绝流程
    def reject(self):
        with transaction.atomic():
            # TODO:  事务里执行 hook
            for s in self.step_define.reject_stepdefines.all():
                Step.objects.create(step_define=s, workflow=self.workflow, arguments=self.arguments)

    # commit后 回调
    def commit_callback(self):
        with transaction.atomic():
            # TODO:  事务里执行 hook
            pass