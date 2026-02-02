from django.db import models

'''
用户模型（User 表）
'''
class User(models.Model):
    # 用户名字段 (CharField：对应数据库中的 varchar类型)
    username = models.CharField(
        max_length=20,
        verbose_name='用户名',
        unique=True,  # 唯一
    )
    # 密码字段
    password = models.CharField(
        max_length=20,
        verbose_name='密码',
    )
    # 头像字段 (URLField：对应数据库中的 varchar类型)
    avatar = models.URLField(
        max_length=255,
        blank=True,  # 表单可空 -> 用户可以不填
        null=True,  # 数据库可存Null
        default='',
        verbose_name='头像URL',
    )
    # 创建时间和更新时间字段
    create_time = models.DateTimeField(
        auto_now_add=True,  # 创建时自动设置
        verbose_name='创建时间',
    )
    update_time = models.DateTimeField(
        auto_now=True,  # 更新时自动设置
        verbose_name='更新时间',
    )
