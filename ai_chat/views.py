from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, SendMessageSerializer
from .services.ai_service import AIServiceError, OpenAICompatibleAIService
from .services.product_search_service import (
    find_best_product_from_message,
    format_product_reply,
    serialize_product,
)
from .services.telegram_service import is_food_order_message, notify_food_order


ai_service = OpenAICompatibleAIService()


class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chat_id = serializer.validated_data.get("chat_id")
        content = serializer.validated_data["content"]

        if chat_id is None:
            chat = Chat.objects.create(user=request.user, title=content[:40])
            created_new_chat = True
        else:
            chat = get_object_or_404(Chat, id=chat_id, user=request.user)
            created_new_chat = False

        user_message = Message.objects.create(
            chat=chat,
            role=Message.Role.USER,
            content=content,
        )

        assistant_message = Message.objects.create(
            chat=chat,
            role=Message.Role.ASSISTANT,
            content=getattr(settings, "AI_CHAT_STATIC_REPLY", "Holisa ai tez kunda ishga tushadi"),
        )
        assistant_data = MessageSerializer(assistant_message).data

        return Response(
            {
                "chat": ChatSerializer(chat).data,
                "created_new_chat": created_new_chat,
                "user_message": MessageSerializer(user_message).data,
                "assistant_message": assistant_data,
                "best_product": None,
                "ai_error": None,
            },
            status=status.HTTP_201_CREATED,
        )


class ChatListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by("-updated_at", "-id")


class ChatDetailAPIView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)


class ChatMessagesListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs["pk"], user=self.request.user)
        return Message.objects.filter(chat=chat).order_by("created_at", "id")
