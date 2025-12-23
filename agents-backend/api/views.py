from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from .models import ModelConfig
from .serializers import (
    UserSerializer,
    RoleSerializer,
    PermissionSerializer,
    ModelConfigSerializer,
    ModelConfigPublicSerializer,
)
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import StreamingHttpResponse
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Explicitly load .env file
# Assuming structure:
# agents-saas-platform/
#   agents-backend/api/views.py
#   agents-backend/.env
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ModelConfigViewSet(viewsets.ModelViewSet):
    """模型配置 ViewSet"""

    queryset = ModelConfig.objects.all()
    serializer_class = ModelConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public(self, request):
        """公开接口：获取启用的模型列表（用于对话广场）"""
        queryset = ModelConfig.objects.filter(is_active=True).order_by(
            "sort_order", "-created_at"
        )
        serializer = ModelConfigPublicSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class ChatView(APIView):
    """通用聊天接口 - 支持流式返回"""

    permission_classes = [AllowAny]

    def post(self, request):
        model_id = request.data.get("model_id", "gpt-3.5-turbo")
        messages = request.data.get("messages", [])

        if not messages:
            return Response({"error": "messages is required"}, status=400)

        # 获取模型配置
        try:
            model_config = ModelConfig.objects.get(model_id=model_id, is_active=True)
            api_base_url = model_config.api_base_url or "https://api.siliconflow.cn/v1"
            # 优先使用直接配置的 API Key，其次从环境变量读取
            api_key = (
                model_config.api_key
                or os.getenv(model_config.api_key_env or "SILICONFLOW_API_KEY")
                or os.getenv("SILICONFLOW_API_KEY")
            )
        except ModelConfig.DoesNotExist:
            # 使用默认配置
            api_base_url = "https://api.siliconflow.cn/v1"
            api_key = os.getenv("SILICONFLOW_API_KEY")

        # 检查 API Key 是否存在
        if not api_key:
            return Response(
                {
                    "error": f"API Key 未配置。请在后端设置环境变量 {model_config.api_key_env} 或 SILICONFLOW_API_KEY"
                },
                status=500,
            )

        def event_stream():
            try:
                llm = ChatOpenAI(
                    model=model_id,
                    base_url=api_base_url,
                    api_key=api_key,
                    temperature=0.7,
                    streaming=True,
                )

                # 转换消息格式
                langchain_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        langchain_messages.append(("human", content))
                    elif role == "assistant":
                        langchain_messages.append(("assistant", content))
                    elif role == "system":
                        langchain_messages.append(("system", content))

                prompt = ChatPromptTemplate.from_messages(langchain_messages)
                chain = prompt | llm

                # 流式输出
                for chunk in chain.stream({}):
                    token = chunk.content
                    if token:
                        yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
