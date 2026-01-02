# market/posting_views.py
import os
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from common.tag_dao import get_all_tags
from common.posting_dao import is_favorite

# DAO 接口（后续在 posting_dao.py 中实现）
from common.posting_dao import (
    get_my_postings,
    get_posting_list,
    get_posting_detail,
    create_posting,
    update_posting,
    soft_delete_posting,
    add_posting_image,
    delete_posting_image,
    change_scope,
    add_favorite,
    remove_favorite,
    get_user_favorites
)

# =========================================================
# 1. 帖子列表（首页展示 & 帖子中心展示）
# =========================================================
def posting_list(request):
    """
    展示所有上架的帖子（按时间倒序）
    可后续增加分页、范围过滤
    """
    postings = get_posting_list()   # DAO 接口
    return render(request, "market/posting_list.html", {"postings": postings})

# =========================================================
# 2. 帖子详情（包含图片、标签、库存等）
# =========================================================
def posting_detail(request, posting_id):
    posting = get_posting_detail(posting_id)

    if not posting:
        messages.error(request, "帖子不存在")
        return redirect("market:posting_list")

    user_id = request.session.get("user_id")

    # ⭐ 是否已收藏
    favorited = False
    if user_id:
        favorited = is_favorite(user_id, posting_id)

    return render(request, "market/posting_detail.html", {
        "posting": posting,
        "favorited": favorited
    })

# =========================================================
# 3. 发布帖子（出物/求物）
# =========================================================
@csrf_exempt
def create_posting_view(request):
    if request.method == "POST":
        owner_id = request.session.get("user_id")
        if not owner_id:
            return redirect("accounts:login")

        title = request.POST.get("title")
        content = request.POST.get("content")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        brand = request.POST.get("brand")
        condition = request.POST.get("condition")
        tag_id = request.POST.get("tag_id")
        scope = request.POST.get("scope")

        # ====== 新增：封面图处理（上传 or 手填URL）======
        image_url = None

        image_file = request.FILES.get("image")
        image_url_input = (request.POST.get("image_url") or "").strip()

        try:
            if image_file:
                image_url = _save_cover_image_to_media(image_file)
            elif image_url_input:
                # 例如：/static/images/demo.jpg 或 /media/postings/xxx.jpg
                image_url = image_url_input
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("market:create_posting")

        create_posting(
            title, content, price, quantity,
            brand, image_url, condition, tag_id, scope, owner_id
        )
        messages.success(request, "发布成功")
        return redirect("market:posting_list")

    tags = get_all_tags()
    return render(request, "market/create_posting.html", {"tags": tags})


# =========================================================
# 4. 修改帖子（只能修改自己的）
# =========================================================
def edit_posting(request, posting_id):
    owner_id = request.session.get("user_id")
    if not owner_id:
        return redirect("accounts:login")

    posting = get_posting_detail(posting_id)
    if posting["owner_id"] != owner_id:
        messages.error(request, "无权限修改该帖子")
        return redirect("market:posting_detail", posting_id=posting_id)

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        brand = request.POST.get("brand")
        condition = request.POST.get("condition")
        tag_id = request.POST.get("tag_id")
        scope = request.POST.get("scope")

        update_posting(posting_id, title, content, price, quantity, brand, condition, tag_id, scope, owner_id)
        messages.success(request, "修改成功")
        return redirect("market:posting_detail", posting_id=posting_id)

    return render(request, "market/edit_posting.html", {"posting": posting})


# =========================================================
# 5. 删除帖子（软删除：status = '下架'）
# =========================================================
def delete_posting(request, posting_id):
    owner_id = request.session.get("user_id")
    if not owner_id:
        return redirect("accounts:login")

    soft_delete_posting(posting_id, owner_id)
    messages.success(request, "已删除（下架）")
    return redirect("market:posting_list")


# =========================================================
# 6. 图片上传
# =========================================================
@csrf_exempt
def upload_posting_image(request, posting_id):
    if request.method == "POST":
        owner_id = request.session.get("user_id")
        if not owner_id:
            return redirect("accounts:login")

        # 假设文件上传后路径为 file_url
        image_file = request.FILES["image"]
        file_url = "/media/uploads/" + image_file.name  # 你后面可以改成真实路径

        add_posting_image(posting_id, owner_id, file_url, "物品照片")
        return JsonResponse({"status": "success", "path": file_url})

    return JsonResponse({"status": "fail"})


# =========================================================
# 7. 图片删除
# =========================================================
def delete_posting_image_view(request, image_id):
    owner_id = request.session.get("user_id")
    delete_posting_image(image_id, owner_id)
    return JsonResponse({"status": "success"})


# =========================================================
# 8. 修改帖子可见范围（scope：寝室/楼层/楼栋/全楼）
# =========================================================
def change_posting_scope_view(request, posting_id):
    owner_id = request.session.get("user_id")
    new_scope = request.POST.get("scope")  # 寝室/楼层/楼栋/全楼

    change_scope(posting_id, owner_id, new_scope)
    return JsonResponse({"status": "success"})


# =========================================================
# 9. 收藏帖子
# =========================================================
from django.shortcuts import redirect

def add_favorite_view(request, posting_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    add_favorite(user_id, posting_id)

    # ⭐ 跳转到“我的收藏”
    return redirect("market:favorite_list")


# =========================================================
# 10. 取消收藏
# =========================================================
def remove_favorite_view(request, posting_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    remove_favorite(user_id, posting_id)

    # 回到商品详情页
    return redirect("market:posting_detail", posting_id=posting_id)

# =========================================================
# 11. 收藏列表
# =========================================================
def favorite_list_view(request):
    user_id = request.session.get("user_id")
    favorites = get_user_favorites(user_id)
    return render(request, "market/favorite_list.html", {"favorites": favorites})

# =========================================================
# 12. 我的出物（当前用户发布的帖子）
# =========================================================
def my_postings_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    postings = get_my_postings(user_id)
    return render(request, "market/my_postings.html", {
        "postings": postings
    })


def _save_cover_image_to_media(image_file):
    ext = os.path.splitext(image_file.name)[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    if ext not in allowed:
        raise ValueError("仅支持 jpg/jpeg/png/gif/webp 格式图片")

    upload_dir = os.path.join(settings.MEDIA_ROOT, "postings")
    os.makedirs(upload_dir, exist_ok=True)

    fs = FileSystemStorage(
        location=upload_dir,
        base_url=settings.MEDIA_URL + "postings/",
    )
    filename = f"{uuid.uuid4().hex}{ext}"
    saved_name = fs.save(filename, image_file)
    return fs.url(saved_name)  # /media/postings/xxxx.jpg

