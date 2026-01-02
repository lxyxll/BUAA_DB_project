# market/order_views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from common.order_dao import (
    create_order_by_proc,
    get_buyer_orders,
    get_seller_orders,
    get_order_detail,
    confirm_order_by_proc,
    cancel_order_by_proc,
    complete_order_by_proc,
)


# ======================================================
# 1. 买家创建订单（下单/预定）
# ======================================================
def create_order_view(request, posting_id):
    if request.method == "POST":
        buyer_id = request.session.get("user_id")
        if not buyer_id:
            return redirect("accounts:login")

        quantity = int(request.POST.get("quantity"))

        result = create_order_by_proc(posting_id, buyer_id, quantity)

        if result is False:
            messages.error(request, "下单失败（库存不足或数据库错误）")
        else:
            messages.success(request, "下单成功，等待卖家确认")

        return redirect("market:order_buyer_list")

    # GET 请求：展示下单页面
    return render(request, "market/create_order.html", {
        "posting_id": posting_id
    })

# ======================================================
# 2. 查看买家订单列表
# ======================================================
def order_buyer_list(request):
    user_id = request.session.get("user_id")
    orders = get_buyer_orders(user_id)
    return render(request, "market/order_buyer_list.html", {"orders": orders})


# ======================================================
# 3. 查看卖家订单列表
# ======================================================
def order_seller_list(request):
    user_id = request.session.get("user_id")
    orders = get_seller_orders(user_id)
    return render(request, "market/order_seller_list.html", {"orders": orders})


# ======================================================
# 4. 订单详情
# ======================================================
def order_detail_view(request, order_id):
    user_id = request.session.get("user_id")
    order = get_order_detail(order_id)
    if not order:
        messages.error(request, "订单不存在")
        return redirect("market:order_buyer_list")

     # ===============================
    # ⭐ 关键：计算按钮权限
    # ===============================
    order["can_confirm"] = (
        order["status"] == "待交接"
        and user_id == order["seller_id"]
    )

    order["can_cancel"] = (
        order["status"] != "取消" and order["status"] != "完成"
        and user_id == order["buyer_id"]
        and user_id == order["buyer_id"]
    )

    order["can_complete"] = (
        order["status"] == "已交接"
        and user_id == order["buyer_id"]
    )
     # ===============================
    # ⭐ 投诉权限
    # ===============================
    order["can_complain"] = (
        user_id in (order["buyer_id"], order["seller_id"])
        and order["status"] != "取消" and order["status"] != "完成"
    )
    
    return render(request, "market/order_detail.html", {"order": order})


# ======================================================
# 5. 卖家确认交接（状态：待交接 → 已交接）
# ======================================================
def confirm_order_view(request, order_id):
    if request.method != "POST":
        return redirect("market:order_detail", order_id=order_id)

    seller_id = request.session.get("user_id")
    if not seller_id:
        return redirect("accounts:login")

    ok = confirm_order_by_proc(order_id)
    if not ok:
        messages.error(request, "确认交接失败")
    else:
        messages.success(request, "已确认交接")

    return redirect("market:order_detail", order_id=order_id)


# ======================================================
# 6. 双方完成订单（状态：已交接 → 完成）
# ======================================================
def complete_order_view(request, order_id):
    if request.method != "POST":
        messages.error(request, "非法请求")
        return redirect("market:order_detail", order_id=order_id)

    user_id = request.session.get("user_id")

    ok = complete_order_by_proc(order_id, user_id)
    if ok:
        messages.success(request, "订单已完成")
    else:
        messages.error(request, "完成失败（状态不允许或权限不足）")

    return redirect("market:order_detail", order_id=order_id)




# ======================================================
# 7. 买家或卖家取消订单（状态：取消）
# ======================================================
def cancel_order_view(request, order_id):
    if request.method != "POST":
        messages.error(request, "非法请求")
        return redirect("market:order_detail", order_id=order_id)

    user_id = request.session.get("user_id")
    reason = request.POST.get("reason", "用户取消订单")

    ok = cancel_order_by_proc(order_id, reason, user_id)
    if ok:
        messages.success(request, "订单已取消")
    else:
        messages.error(request, "取消失败（状态不允许或权限不足）")

    return redirect("market:order_detail", order_id=order_id)
