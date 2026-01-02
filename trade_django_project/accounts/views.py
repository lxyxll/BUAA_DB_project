# accounts/views.py —— SQL 版本用户模块

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings


from common.user_dao import (
    check_user_exists,
    insert_user,
    get_user_by_student_id,
    get_user_by_id,
    update_user_profile,
    update_user_password,
    get_room_list,
    bind_room,
    admin_get_all_users,
    ban_user_by_id,
    unban_user_by_id,
)


# ======================================================
# 1️⃣ 用户注册
# ======================================================
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")
        wechat = request.POST.get("wechat")
        student_id = request.POST.get("student_id")
        room_id = request.POST.get("room_id")

        # 空字段检查
        if not all([username, password, password2, email, student_id, room_id]):
            messages.error(request, "请填写所有字段")
            return render(request, "accounts/register.html")

        if password != password2:
            messages.error(request, "两次输入的密码不一致")
            return render(request, "accounts/register.html")

        # 重名检查
        if check_user_exists(email, student_id, username):
            messages.error(request, "用户名、邮箱或学号已被注册")
            return render(request, "accounts/register.html")

        # 插入用户
        #insert_user(username, password, email, wechat, student_id, room_id)
        #messages.success(request, "注册成功，请登录")
        #return redirect("accounts:login")
        # accounts/views.py  register()

        # 读取注册类型：user / admin
        account_type = request.POST.get("account_type", "user")

        # 默认普通用户
        role = 0
        user_role = 1

        # 如果选择管理员，校验管理员注册码
        if account_type == "admin":
            admin_code = (request.POST.get("admin_code") or "").strip()
            expected_code = getattr(settings, "ADMIN_REGISTER_CODE", "")
            if not expected_code or admin_code != expected_code:
                messages.error(request, "管理员注册码错误")
                rooms = get_room_list()
                return render(request, "accounts/register.html", {"rooms": rooms})

            user_role = 3  # 管理员权限（与你现有权限判断一致）

        # 插入用户（写入不同 user_role）
        insert_user(username, password, email, wechat, student_id, room_id, role=role, user_role=user_role)

        messages.success(request, "注册成功，请登录")
        return redirect("accounts:login")


    rooms = get_room_list()
    return render(request, "accounts/register.html", {"rooms": rooms})


# ======================================================
# 2️⃣ 登录（使用 session，不使用 Django Auth）
# ======================================================
def login_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        password = request.POST.get("password")

        user = get_user_by_student_id(student_id)
        if not user:
            messages.error(request, "学号或密码错误")
            return render(request, "accounts/login.html")

        user_id, username, pwd_in_db, status, role, user_role = user


        if status == "封禁":
            messages.error(request, "用户已被封禁")
            return render(request, "accounts/login.html")

        if pwd_in_db != password:
            messages.error(request, "学号或密码错误")
            return render(request, "accounts/login.html")

        # 登录成功 → 写入 session
        request.session["user_id"] = user_id
        request.session["username"] = username
        request.session["is_logged_in"] = True
        request.session["role"] = role
        request.session["user_role"] = user_role

        return redirect("market:index")

    return render(request, "accounts/login.html")


# ======================================================
# 3️⃣ 登出（session 版本）
# ======================================================
def logout_view(request):
    request.session.flush()
    return redirect("market:index")


# ======================================================
# 4️⃣ 查看个人资料
# ======================================================
def profile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    user = get_user_by_id(user_id)
    return render(request, "accounts/profile.html", {"user": user})


# ======================================================
# 5️⃣ 修改个人资料（邮箱、微信、寝室）
# ======================================================
def update_profile_view(request):
    user_id = request.session.get("user_id")

    if request.method == "POST":
        email = request.POST.get("email")
        wechat = request.POST.get("wechat")
        room_id = request.POST.get("room_id")

        if not email or not room_id:
            messages.error(request, "邮箱和寝室信息不能为空")
            return redirect("accounts:profile")

        update_user_profile(email, wechat, room_id, user_id)
        messages.success(request, "资料已更新")
        return redirect("accounts:profile")

    user = get_user_by_id(user_id)
    rooms = get_room_list()
    return render(request, "accounts/update_profile.html", {"user_obj": user, "rooms": rooms})


# ======================================================
# 6️⃣ 修改密码
# ======================================================
def change_password_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    if request.method == "POST":
        old_pwd = request.POST.get("old_password")
        new_pwd = request.POST.get("new_password")
        confirm = request.POST.get("new_password2")

        if not all([old_pwd, new_pwd, confirm]):
            messages.error(request, "请填写所有字段")
            return redirect("accounts:change_password")

        # 先拿到 student_id（get_user_by_id 里有）
        user = get_user_by_id(user_id)
        if not user:
            messages.error(request, "用户不存在")
            return redirect("accounts:change_password")

        # 用你现有方法 get_user_by_student_id 取出数据库密码
        row = get_user_by_student_id(user["student_id"])
        if not row:
            messages.error(request, "用户不存在")
            return redirect("accounts:change_password")

        pwd_in_db = row[2]  # (user_id, username, password, status, role, user_role)

        if pwd_in_db != old_pwd:
            messages.error(request, "旧密码错误")
            return redirect("accounts:change_password")

        if new_pwd != confirm:
            messages.error(request, "两次新密码不一致")
            return redirect("accounts:change_password")

        update_user_password(user_id, new_pwd)
        messages.success(request, "密码修改成功")
        return redirect("accounts:profile")

    return render(request, "accounts/change_password.html")



# ======================================================
# 7️⃣ 管理员查看用户列表
# ======================================================
def admin_user_list_view(request):
    if request.session.get("user_role") != 3:  # 管理员权限检查
        messages.error(request, "无权限")
        return redirect("market:index")

    users = admin_get_all_users()
    return render(request, "accounts/admin_user_list.html", {"users": users})


# ======================================================
# 8️⃣ 管理员封禁用户
# ======================================================
def admin_ban_user_view(request, user_id):
    if request.session.get("user_role") != 3:
        return JsonResponse({"status": "fail", "msg": "无权限"})

    ban_user_by_id(user_id)
    return JsonResponse({"status": "success"})


# ======================================================
# 9️⃣ 管理员解封用户
# ======================================================
def admin_unban_user_view(request, user_id):
    if request.session.get("user_role") != 3:
        return JsonResponse({"status": "fail", "msg": "无权限"})

    unban_user_by_id(user_id)
    return JsonResponse({"status": "success"})
