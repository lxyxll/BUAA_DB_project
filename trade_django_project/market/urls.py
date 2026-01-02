# market/urls.py
from django.urls import path

from .views import index, dashboard, admin_panel

from .posting_views import (
    my_postings_view,
    posting_list,
    posting_detail,
    create_posting_view,
    edit_posting,
    delete_posting,
    add_favorite_view,
    remove_favorite_view,
    favorite_list_view,
)

from .order_views import (
    create_order_view,
    order_buyer_list,
    order_seller_list,
    order_detail_view,
    confirm_order_view,
    complete_order_view,
    cancel_order_view,
)

from .search_views import (
    search,
    tag_list,
    search_by_tag_view,
    search_tag_suggestion,
)

from .notice_views import (
    notice_list_view,
    unread_notice_view,
    mark_read_view,
    announcement_list_view,
    announcement_detail_view,
    admin_publish_announcement_view,
    admin_delete_announcement_view,
)

from .complaint_views import (
    complaint_detail_view,
    submit_complaint_view,
    my_complaints_view,
    admin_complaint_list_view,
    admin_handle_complaint_view,
)

from .stats_views import (
    stats_overview_view,
    stats_user_view,
    stats_monthly_orders_view,
)

app_name = "market"

urlpatterns = [
    # ===== 首页 / 汇总 =====
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
    path("admin/", admin_panel, name="admin_panel"),

    # ===== 出物 Posting =====
    path("postings/", posting_list, name="posting_list"),
    path("my_postings/", my_postings_view, name="my_postings"),
    path("posting/<int:posting_id>/", posting_detail, name="posting_detail"),
    path("posting/create/", create_posting_view, name="create_posting"),
    path("posting/<int:posting_id>/edit/", edit_posting, name="edit_posting"),
    path("posting/<int:posting_id>/delete/", delete_posting, name="delete_posting"),

    # 收藏
    path("favorite/<int:posting_id>/add/", add_favorite_view, name="add_favorite"),
    path("favorite/<int:posting_id>/remove/", remove_favorite_view, name="remove_favorite"),
    path("favorites/", favorite_list_view, name="favorite_list"),

    # ===== 订单 Order =====
    path("order/create/<int:posting_id>/", create_order_view, name="create_order"),
    path("orders/buyer/", order_buyer_list, name="order_buyer_list"),
    path("orders/seller/", order_seller_list, name="order_seller_list"),
    path("order/<int:order_id>/", order_detail_view, name="order_detail"),
    path("order/<int:order_id>/confirm/", confirm_order_view, name="confirm_order"),
    path("order/<int:order_id>/complete/", complete_order_view, name="complete_order"),
    path("order/<int:order_id>/cancel/", cancel_order_view, name="cancel_order"),

    # ===== 搜索 Search =====
    path("search/", search, name="search"),
    path("tags/", tag_list, name="tag_list"),
    path("tag/<int:tag_id>/", search_by_tag_view, name="search_by_tag"),
    path("tag/suggest/", search_tag_suggestion, name="search_tag_suggestion"),

    # ===== 消息 / 公告 Notice =====
    path("notices/", notice_list_view, name="notice_list"),
    path("notices/unread/", unread_notice_view, name="unread_notice"),
    path("notice/read/<int:notice_id>/", mark_read_view, name="mark_read"),
    path("announcements/", announcement_list_view, name="announcement_list"),
    path("announcement/<int:notice_id>/", announcement_detail_view, name="announcement_detail"),
    path("announcement/publish/", admin_publish_announcement_view, name="admin_publish_announcement"),
    path("announcement/<int:notice_id>/delete/", admin_delete_announcement_view, name="admin_delete_announcement"),

    # ===== 投诉 Complaint =====
    path("complaint/submit/<int:order_id>/", submit_complaint_view, name="submit_complaint"),
    path("complaints/my/", my_complaints_view, name="my_complaints"),
    path("complaints/admin/", admin_complaint_list_view, name="admin_complaint_list"),
    path("complaint/<int:complaint_id>/handle/", admin_handle_complaint_view, name="admin_handle_complaint"),
    path("complaint/<int:complaint_id>/", complaint_detail_view, name="complaint_detail"),

    # ===== 统计 Stats =====
    path("stats/", stats_overview_view, name="stats_overview"),
    path("stats/me/", stats_user_view, name="stats_user"),
    path("stats/monthly-orders/", stats_monthly_orders_view, name="stats_monthly_orders"),
]