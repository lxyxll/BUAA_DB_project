# market/complaint_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect


from common.complaint_dao import (
    submit_complaint,
    get_my_complaints,
    get_complaints_by_order,
    admin_get_pending_complaints,
    admin_get_complaints,
    admin_mark_processing,
    admin_handle_complaint,
    get_complaint_detail,
)


from common.order_dao import get_order_detail

# ======================================================
# 1️⃣ 用户提交投诉
# ======================================================
def submit_complaint_view(request, order_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    # POST：提交投诉
    if request.method == "POST":
        content = request.POST.get("content")

        try:
            submit_complaint(order_id, user_id, content)
        except Exception as e:
            messages.error(request, str(e))
            return redirect("market:submit_complaint", order_id=order_id)

        messages.success(request, "投诉已提交，管理员将尽快处理")
        return redirect("market:order_buyer_list")

    # GET：查询订单信息，用于页面展示
    order = get_order_detail(order_id)
    if not order:
        messages.error(request, "订单不存在")
        return redirect("market:order_buyer_list")

    return render(request, "market/submit_complaint.html", {"order": order})



# ======================================================
# 2️⃣ 用户查看自己的投诉记录
# ======================================================
def my_complaints_view(request):
    user_id = request.session.get("user_id")
    complaints = get_my_complaints(user_id)
    return render(request, "market/my_complaints.html", {"complaints": complaints})


# ======================================================
# 3️⃣ 按订单查看投诉列表（例如买家或卖家查看）
# ======================================================
def complaints_by_order_view(request, order_id):
    complaints = get_complaints_by_order(order_id)
    return render(request, "market/complaints_by_order.html", {"complaints": complaints})


# ======================================================
# 4️⃣ 投诉详情
# ======================================================
def complaint_detail_view(request, complaint_id):
    detail = get_complaint_detail(complaint_id)
    return render(request, "market/complaint_detail.html", {"complaint": detail})


# ======================================================
# 5️⃣ 管理员查看全部待处理投诉
# ======================================================
def admin_complaint_list_view(request):
    if request.session.get("user_role") != 3:
        messages.error(request, "无权限")
        return redirect("market:index")

    status = request.GET.get("status", "待处理")  # 默认只看待处理
    if status == "全部":
        complaints = admin_get_complaints(status=None)
    else:
        # 兼容：你也可以继续用 admin_get_pending_complaints() 做默认待处理
        complaints = admin_get_complaints(status=status)

    return render(request, "market/admin_complaint_list.html", {
        "complaints": complaints,
        "status": status,
    })



# ======================================================
# 6️⃣ 管理员处理投诉（写入处理结果）
# ======================================================
def admin_handle_complaint_view(request, complaint_id):
    if request.session.get("user_role") != 3:
        messages.error(request, "无权限")
        return redirect("market:index")

    detail = get_complaint_detail(complaint_id)
    if not detail:
        messages.error(request, "投诉不存在")
        return redirect("market:admin_complaint_list")

    # 可选：管理员一进入就把待处理 -> 处理中
    try:
        admin_mark_processing(complaint_id)
        detail = get_complaint_detail(complaint_id)
    except Exception:
        pass

    if request.method == "POST":
        result = request.POST.get("result")
        new_status = request.POST.get("status") or "已处理"
        admin_user_id = request.session.get("user_id")

        try:
            admin_handle_complaint(complaint_id, result, admin_user_id=admin_user_id, new_status=new_status)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, "market/admin_handle_complaint.html", {"complaint": detail})

        messages.success(request, "处理结果已提交")
        return redirect(f"{reverse('market:admin_complaint_list')}?status={new_status}")

    return render(request, "market/admin_handle_complaint.html", {"complaint": detail})

