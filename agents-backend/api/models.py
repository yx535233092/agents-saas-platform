from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model.
    """

    # Add custom fields here if needed
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Phone Number"
    )
    avatar = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="Avatar URL"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class ModelConfig(models.Model):
    """
    模型配置 - 用于对话广场的模型选择
    """

    PROVIDER_CHOICES = [
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("deepseek", "DeepSeek"),
        ("alibaba", "Alibaba"),
        ("siliconflow", "SiliconFlow"),
        ("other", "Other"),
    ]

    ICON_CHOICES = [
        ("sparkles", "Sparkles"),
        ("zap", "Zap"),
        ("brain", "Brain"),
        ("cpu", "Cpu"),
        ("bot", "Bot"),
    ]

    name = models.CharField(max_length=100, verbose_name="模型名称")
    model_id = models.CharField(max_length=100, unique=True, verbose_name="模型标识")
    description = models.CharField(max_length=255, blank=True, verbose_name="模型描述")
    provider = models.CharField(
        max_length=50, choices=PROVIDER_CHOICES, default="openai", verbose_name="供应商"
    )
    icon = models.CharField(
        max_length=20, choices=ICON_CHOICES, default="sparkles", verbose_name="图标"
    )
    icon_color = models.CharField(
        max_length=20, default="text-blue-500", verbose_name="图标颜色"
    )
    max_tokens = models.IntegerField(default=4096, verbose_name="最大Token数")
    api_base_url = models.URLField(
        max_length=255, blank=True, verbose_name="API Base URL"
    )
    api_key = models.CharField(
        max_length=255, blank=True, verbose_name="API Key (直接填写)"
    )
    api_key_env = models.CharField(
        max_length=100, blank=True, verbose_name="API Key 环境变量名 (备选)"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "模型配置"
        verbose_name_plural = "模型配置"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.provider})"
