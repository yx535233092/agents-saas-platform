from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from .models import ModelConfig

User = get_user_model()

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), source='permissions'
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_ids']

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), source='groups'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'roles', 'role_ids', 'phone', 'avatar', 'password']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}

    def get_roles(self, obj):
        return [group.name for group in obj.groups.all()]

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        if groups:
            user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        
        if groups is not None:
            instance.groups.set(groups)
            
        return instance


class ModelConfigSerializer(serializers.ModelSerializer):
    """模型配置序列化器"""
    class Meta:
        model = ModelConfig
        fields = [
            'id', 'name', 'model_id', 'description', 'provider', 
            'icon', 'icon_color', 'max_tokens', 'api_base_url', 
            'api_key', 'api_key_env', 'is_active', 'sort_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'api_key': {'write_only': True}}  # API Key 不返回给前端
    
    def to_representation(self, instance):
        """返回时隐藏 API Key 的具体值，只显示是否已配置"""
        ret = super().to_representation(instance)
        ret['api_key_configured'] = bool(instance.api_key)
        return ret


class ModelConfigPublicSerializer(serializers.ModelSerializer):
    """模型配置公开序列化器 - 用于对话广场，不暴露敏感信息"""
    class Meta:
        model = ModelConfig
        fields = [
            'id', 'name', 'model_id', 'description', 'provider', 
            'icon', 'icon_color', 'max_tokens'
        ]
