# market/search_views.py

from django.shortcuts import render
from django.http import JsonResponse

from common.search_dao import (
    search_postings,
    search_by_tag,
    search_tags_fuzzy,
    get_all_tags,
)


# ======================================================
# 1. 综合搜索（关键字 + 标签 + 范围）
# ======================================================
def search(request):
    keyword = request.GET.get("keyword", "")
    tag_id = request.GET.get("tag_id")
    scope = request.GET.get("scope", "全楼")

    user_id = request.session.get("user_id")
    
    results = search_postings(keyword, tag_id, scope, user_id)

    return render(
        request,
        "market/search_results.html",
        {"results": results, "keyword": keyword}
    )


# ======================================================
# 2. 标签列表
# ======================================================
def tag_list(request):
    tags = get_all_tags()
    return render(request, "market/tag_list.html", {"tags": tags})


# ======================================================
# 3. 按标签搜索
# ======================================================
def search_by_tag_view(request, tag_id):
    user_id = request.session.get("user_id")
    results = search_by_tag(tag_id, user_id)
    return render(request, "market/search_results.html", {"results": results})


# ======================================================
# 4. 标签模糊搜索（输入框自动联想）
# ======================================================
def search_tag_suggestion(request):
    query = request.GET.get("q", "")
    suggestions = search_tags_fuzzy(query)
    return JsonResponse({"tags": suggestions})
