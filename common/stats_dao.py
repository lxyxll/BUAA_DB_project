# common/stats_dao.py
# ======================================================
# 统计模块 DAO：系统、用户、寝室、楼层、楼栋、月度统计
# ======================================================

from common.db import query_one, query_all


# ======================================================
# 1️⃣ 系统总览统计（管理员）
# ======================================================
def get_system_overview_stats():
    stats = {}

    # 用户总数
    stats["user_count"] = query_one("SELECT COUNT(*) FROM user")[0]

    # 上架帖子总数
    stats["posting_count"] = query_one("SELECT COUNT(*) FROM posting WHERE status='上架'")[0]

    # 完成订单
    stats["order_completed"] = query_one(
        "SELECT COUNT(*) FROM `order` WHERE status='完成'"
    )[0]

    # 取消订单
    stats["order_canceled"] = query_one(
        "SELECT COUNT(*) FROM `order` WHERE status='取消'"
    )[0]

    # 投诉数量
    stats["complaint_count"] = query_one(
        "SELECT COUNT(*) FROM complaint"
    )[0]

    # 已处理投诉数量
    stats["complaint_resolved"] = query_one(
        "SELECT COUNT(*) FROM complaint WHERE status='已处理'"
    )[0]

    # 投诉处理率
    if stats["complaint_count"] == 0:
        stats["complaint_resolve_rate"] = 1.0
    else:
        stats["complaint_resolve_rate"] = (
            stats["complaint_resolved"] / stats["complaint_count"]
        )

    return stats


# ======================================================
# 2️⃣ 用户个人统计（出物量、订单、投诉）
# ======================================================
def get_user_stats(user_id):
    stats = {}

    # 用户发布的帖子数量
    stats["posting_count"] = query_one(
        "SELECT COUNT(*) FROM posting WHERE owner_id=%s", [user_id]
    )[0]

    # 卖家完成订单数量
    stats["seller_orders_completed"] = query_one(
        "SELECT COUNT(*) FROM `order` WHERE seller_id=%s AND status='完成'",
        [user_id],
    )[0]

    # 买家完成订单数量
    stats["buyer_orders_completed"] = query_one(
        "SELECT COUNT(*) FROM `order` WHERE buyer_id=%s AND status='完成'",
        [user_id],
    )[0]

    # 用户订单总数（买家+卖家）
    stats["total_orders"] = query_one(
        "SELECT COUNT(*) FROM `order` WHERE buyer_id=%s OR seller_id=%s",
        [user_id, user_id],
    )[0]

    # 用户被投诉次数
    stats["complaint_received"] = query_one(
        "SELECT COUNT(*) FROM complaint WHERE accused_id=%s",
        [user_id],
    )[0]

    # 用户投诉被处理次数（成立）
    stats["complaint_resolved"] = query_one(
        "SELECT COUNT(*) FROM complaint WHERE accused_id=%s AND status='已处理'",
        [user_id],
    )[0]

    # 投诉成立率
    if stats["seller_orders_completed"] == 0:
        stats["complaint_resolve_rate"] = 0.0
    elif stats["complaint_received"] == 0:
        stats["complaint_resolve_rate"] = 0.0
    else:
        stats["complaint_resolve_rate"] = (
            stats["complaint_resolved"] / stats["seller_orders_completed"]
        )

    return stats


# ======================================================
# 3️⃣ 寝室统计（按 room_id）
# ======================================================
def get_room_stats(room_id):
    stats = {}

    # 寝室用户数量
    stats["user_count"] = query_one(
        "SELECT COUNT(*) FROM user WHERE room_id=%s",
        [room_id],
    )[0]

    # 寝室用户发布的帖子数量
    stats["posting_count"] = query_one(
        """
        SELECT COUNT(*)
        FROM posting p
        JOIN user u ON p.owner_id = u.user_id
        WHERE u.room_id = %s
        """,
        [room_id],
    )[0]

    # 寝室完成订单数量（卖家为寝室用户）
    stats["orders_completed"] = query_one(
        """
        SELECT COUNT(*)
        FROM `order` o
        JOIN user u ON o.seller_id = u.user_id
        WHERE u.room_id = %s AND o.status='完成'
        """,
        [room_id],
    )[0]

    # 寝室投诉次数
    stats["complaint_count"] = query_one(
        """
        SELECT COUNT(*)
        FROM complaint c
        JOIN user u ON c.accused_id = u.user_id
        WHERE u.room_id = %s
        """,
        [room_id],
    )[0]

    return stats


# ======================================================
# 4️⃣ 楼层统计（按 floor）
# ======================================================
def get_floor_stats(floor):
    stats = {}

    # 楼层用户数量
    stats["user_count"] = query_one(
        """
        SELECT COUNT(*)
        FROM user u
        JOIN room r ON u.room_id = r.room_id
        WHERE r.floor = %s
        """,
        [floor],
    )[0]

    # 楼层帖子数量
    stats["posting_count"] = query_one(
        """
        SELECT COUNT(*)
        FROM posting p
        JOIN user u ON p.owner_id = u.user_id
        JOIN room r ON u.room_id = r.room_id
        WHERE r.floor = %s
        """,
        [floor],
    )[0]

    # 完成订单
    stats["orders_completed"] = query_one(
        """
        SELECT COUNT(*)
        FROM `order` o
        JOIN user u ON o.seller_id = u.user_id
        JOIN room r ON u.room_id = r.room_id
        WHERE r.floor = %s AND o.status='完成'
        """,
        [floor],
    )[0]

    return stats


# ======================================================
# 5️⃣ 楼栋统计（building）
# ======================================================
def get_building_stats(building):
    stats = {}

    stats["user_count"] = query_one(
        """
        SELECT COUNT(*)
        FROM user u
        JOIN room r ON u.room_id = r.room_id
        WHERE r.building = %s
        """,
        [building],
    )[0]

    stats["posting_count"] = query_one(
        """
        SELECT COUNT(*)
        FROM posting p
        JOIN user u ON p.owner_id = u.user_id
        JOIN room r ON u.room_id = r.room_id
        WHERE r.building = %s
        """,
        [building],
    )[0]

    stats["orders_completed"] = query_one(
        """
        SELECT COUNT(*)
        FROM `order` o
        JOIN user u ON o.seller_id = u.user_id
        JOIN room r ON u.room_id = r.room_id
        WHERE r.building = %s AND o.status='完成'
        """,
        [building],
    )[0]

    return stats


# ======================================================
# 6️⃣ 按天统计订单量（折线图）
# ======================================================
def get_monthly_order_stats():
    sql = """
        SELECT
            DATE(created_at) AS day,
            COUNT(*) AS order_count
        FROM `order`
        WHERE status='完成'
            AND created_at >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
        GROUP BY day
        ORDER BY day
    """
    return query_all(sql, as_dict=True)
