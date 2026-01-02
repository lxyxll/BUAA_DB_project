# market/stats_views.py

from django.shortcuts import render
from django.contrib import messages

from common.stats_dao import (
    get_system_overview_stats,
    get_user_stats,
    get_room_stats,
    get_floor_stats,
    get_building_stats,
    get_monthly_order_stats,
)


# ======================================================
# 1️⃣ 系统总览统计（管理员）
# ======================================================
def stats_overview_view(request):
    if request.session.get("user_role") != 3:  # 管理员权限
        messages.error(request, "无权限")
        return render(request, "market/index.html")

    overview = get_system_overview_stats()
    return render(request, "market/stats_overview.html", {"overview": overview})


# ======================================================
# 2️⃣ 用户个人统计（出物量、订单完成率、被投诉率等）
# ======================================================
def stats_user_view(request):
    user_id = request.session.get("user_id")
    stats = get_user_stats(user_id)
    return render(request, "market/stats_user.html", {"stats": stats})


# ======================================================
# 3️⃣ 寝室统计（寝室出物量、投诉情况等）
# ======================================================
def stats_room_view(request, room_id):
    stats = get_room_stats(room_id)
    return render(request, "market/stats_room.html", {"stats": stats})


# ======================================================
# 4️⃣ 楼层统计
# ======================================================
def stats_floor_view(request, floor):
    stats = get_floor_stats(floor)
    return render(request, "market/stats_floor.html", {"stats": stats})


# ======================================================
# 5️⃣ 楼栋统计
# ======================================================
def stats_building_view(request, building):
    stats = get_building_stats(building)
    return render(request, "market/stats_building.html", {"stats": stats})


# ======================================================
# 6️⃣ 月度订单统计（折线图用）
# ======================================================
def stats_monthly_orders_view(request):
    stats = get_monthly_order_stats()
    return render(request, "market/stats_monthly_orders.html", {"stats": stats})
