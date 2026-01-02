# market/views.py
# ======================================================
# market 模块的汇总视图（首页 / 仪表盘）
# ======================================================

from django.shortcuts import render, redirect
from django.contrib import messages

from common.posting_dao import get_posting_list, get_user_favorites
from common.notice_dao import get_unread_notices, get_announcements
from common.order_dao import get_buyer_orders, get_seller_orders
from common.stats_dao import get_user_stats


# ======================================================
# 系统首页（未登录 / 已登录通用）
# ======================================================
def index(request):
    """
    系统首页：
    - 最新出物
    - 公告
    - 登录状态
    """
    postings = get_posting_list()[:10]          # 最新 10 条出物
    announcements = get_announcements()[:5]    # 最新 5 条公告

    context = {
        "postings": postings,
        "announcements": announcements,
        "is_logged_in": request.session.get("is_logged_in", False),
        "username": request.session.get("username"),
    }

    return render(request, "market/index.html", context)


# ======================================================
# 我的主页 / Dashboard（登录后）
# ======================================================
def dashboard(request):
    """
    用户个人总览页面：
    - 我的出物
    - 我的订单
    - 我的收藏
    - 我的统计
    """
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "请先登录")
        return redirect("accounts:login")

    buyer_orders = get_buyer_orders(user_id)
    seller_orders = get_seller_orders(user_id)
    favorites = get_user_favorites(user_id)
    unread_notices = get_unread_notices(user_id)
    stats = get_user_stats(user_id)

    context = {
        "buyer_orders": buyer_orders[:5],
        "seller_orders": seller_orders[:5],
        "favorites": favorites[:5],
        "unread_notice_count": len(unread_notices),
        "stats": stats,
    }

    return render(request, "market/dashboard.html", context)


# ======================================================
# 管理员入口页（可选）
# ======================================================
def admin_panel(request):
    if request.session.get("user_role") != 3:
        messages.error(request, "无权限")
        return redirect("market:index")

    return render(request, "market/admin_panel.html")