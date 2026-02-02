from django.db import models


'''
主题模型（Theme 表）
'''
class Theme(models.Model):
    # # 用户id字段：外键关联User表，级联删除
    # user_id = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,  # 级联删除：用户删除时，关联的主题也删除
    #     verbose_name='关联用户id',
    # )
    # 用户id字段：暂时先使用 IntegerField，只存储id数字，不验证真实性
    user_id = models.IntegerField(
        verbose_name='关联用户id',
    )
    # 主题名字段
    theme_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='健康饮食小助手对话',
        verbose_name='对话主题名',
    )
    # 创建时间和更新时间字段
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
    )
    # 做逻辑删除：添加一个字段
    is_deleted = models.SmallIntegerField(
        default=0,
        verbose_name='是否删除',
    )
    # 删除时间字段
    delete_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='删除时间',
    )


'''
对话内容模型（Conversation 表）
'''
class Conversation(models.Model):
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
        ('system', '系统'),
    ]
    # 关联主题id字段
    theme_id = models.IntegerField(
        verbose_name='关联对话主题id',
    )
    # 用户id字段
    user_id = models.IntegerField(
        default=0,  # 0 表示大模型回答
        verbose_name='关联用户id',
    )
    # 角色字段
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='角色',
    )
    # 对话内容字段
    content = models.TextField(
        verbose_name='对话内容',
    )
    # 创建时间和更新时间字段
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
    )
    # 逻辑删除字段
    is_deleted = models.SmallIntegerField(
        default=0,
        verbose_name='是否删除',
    )
    # 删除时间字段
    delete_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='删除时间',
    )
    # 多模态的多轮对话：图片URL字段
    image_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='图片URL',
    )

