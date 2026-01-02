# market/notice_views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST

from common.notice_dao import (
    get_user_notices,
    get_unread_notices,
    mark_notice_read,
    get_announcements,
    get_announcement_detail,
    admin_publish_announcement,
    admin_delete_announcement,
)

def notice_list_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    notices = get_user_notices(user_id)
    return render(request, "market/notice_list.html", {"notices": notices})


def unread_notice_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    notices = get_unread_notices(user_id)
    return render(request, "market/unread_notice.html", {"notices": notices})


@require_POST
def mark_read_view(request, notice_id):
    user_id = request.session.get("user_id")
    if not user_id:
        # 兼容 AJAX / 非 AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "fail", "msg": "未登录"}, status=401)
        return redirect("accounts:login")

    mark_notice_read(notice_id, user_id)

    # AJAX：返回 JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})

    # 非 AJAX：回到来源页；没有来源就回消息列表
    return redirect(request.META.get("HTTP_REFERER") or "market:notice_list")


def announcement_list_view(request):
    announcements = get_announcements()
    is_admin = (request.session.get("user_role") == 3)
    return render(request, "market/announcement_list.html", {
        "announcements": announcements,
        "is_admin": is_admin,
    })


def announcement_detail_view(request, notice_id):
    ann = get_announcement_detail(notice_id)
    if not ann:
        messages.error(request, "公告不存在或已被删除")
        return redirect("market:announcement_list")

    is_admin = (request.session.get("user_role") == 3)
    return render(request, "market/announcement_detail.html", {
        "announcement": ann,
        "is_admin": is_admin,
    })


def admin_publish_announcement_view(request):
    if request.session.get("user_role") != 3:
        messages.error(request, "无权限")
        return redirect("market:announcement_list")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        try:
            admin_publish_announcement(title, content)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, "market/admin_publish_announcement.html")

        messages.success(request, "公告已发布")
        return redirect("market:announcement_list")

    return render(request, "market/admin_publish_announcement.html")


@require_POST
def admin_delete_announcement_view(request, notice_id):
    if request.session.get("user_role") != 3:
        messages.error(request, "无权限")
        return redirect("market:announcement_list")

    admin_delete_announcement(notice_id)
    messages.success(request, "公告已删除")
    return redirect("market:announcement_list")
