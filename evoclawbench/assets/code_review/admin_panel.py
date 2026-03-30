import requests
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import User, AuditLog, SystemConfig

class AdminUserView(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password,
            "is_admin": user.is_staff,
            "last_login": str(user.last_login),
            "date_joined": str(user.date_joined),
        })

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        for key, value in request.POST.items():
            setattr(user, key, value)
        user.save()
        return JsonResponse({"status": "updated"})

class AdminConfigView(View):
    def post(self, request):
        key = request.POST.get("key")
        value = request.POST.get("value")
        config, _ = SystemConfig.objects.get_or_create(key=key)
        config.value = value
        config.save()
        return JsonResponse({"status": "saved"})

class URLPreviewView(View):
    def post(self, request):
        url = request.POST.get("url")
        try:
            response = requests.get(url, timeout=10)
            return JsonResponse({
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type"),
                "body": response.text[:5000],
            })
        except Exception as e:
            return JsonResponse({"error": str(e), "traceback": __import__('traceback').format_exc()}, status=500)

class AuditLogView(View):
    def get(self, request):
        logs = AuditLog.objects.all().order_by("-created_at")[:100]
        return JsonResponse({
            "logs": [
                {
                    "id": log.id,
                    "user": log.user.username,
                    "action": log.action,
                    "ip_address": log.ip_address,
                    "details": log.details,
                    "created_at": str(log.created_at),
                }
                for log in logs
            ]
        })
