# common/search_dao.py
# ======================================================
# 搜索模块 DAO：关键字搜索、标签搜索、范围过滤、标签联想
# ======================================================

from common.db import query_one, query_all


# ======================================================
# 内部工具：根据用户 ID 获取所在寝室/楼层/楼栋（必要时可复用）
# ======================================================
def _get_user_location(user_id):
    sql = """
        SELECT r.room_id, r.floor, r.building
        FROM user u
        JOIN room r ON u.room_id = r.room_id
        WHERE u.user_id = %s
    """
    return query_one(sql, [user_id], as_dict=True)


# ======================================================
# 生成“帖子可见性” SQL 过滤条件（基于 p.scope + 发帖人位置 vs 查看者位置）
# ======================================================
def _scope_filter_sql():
    return """
        (
            p.scope = '全楼'
            OR (p.scope = '楼栋' AND poster.building = viewer.building)
            OR (p.scope = '楼层' AND poster.building = viewer.building AND poster.floor = viewer.floor)
            OR (p.scope = '寝室' AND poster.room_id = viewer.room_id)
        )
    """


# ======================================================
# 生成“用户选择的地理范围过滤”SQL（只看同楼栋/同楼层/同寝室的发帖人）
# 注意：这是额外过滤，不等于 p.scope
# ======================================================
def _range_filter_sql(scope: str) -> str:
    if not scope or scope in ("全部", "全楼"):
        return ""

    if scope == "楼栋":
        return " AND poster.building = viewer.building"

    if scope == "楼层":
        return " AND poster.building = viewer.building AND poster.floor = viewer.floor"

    if scope == "寝室":
        return " AND poster.room_id = viewer.room_id"

    # 未知值：不额外过滤（避免把数据过滤光）
    return ""


# ======================================================
# 1️⃣ 综合搜索（关键字 + 标签 + 帖子可见性 + 用户选择范围过滤）
# ======================================================
def search_postings(keyword, tag_id, scope, user_id):
    if not user_id:
        return []

    sql = f"""
        SELECT 
            p.posting_id, p.title, p.content, p.price, p.quantity,
            p.brand, p.`condition`, p.tag_id, t.tag_name, p.status, p.scope,
            p.created_at,
            poster.username AS owner_name,
            poster.room_id AS owner_room,
            poster.floor AS owner_floor,
            poster.building AS owner_building
        FROM posting p
        LEFT JOIN tag t ON p.tag_id = t.tag_id
        JOIN (
            SELECT u.user_id, u.username, r.room_id, r.floor, r.building
            FROM user u
            JOIN room r ON u.room_id = r.room_id
        ) AS poster ON p.owner_id = poster.user_id
        JOIN (
            SELECT r.room_id, r.floor, r.building
            FROM room r
            JOIN user u ON u.room_id = r.room_id
            WHERE u.user_id = %s
        ) AS viewer
        WHERE p.status = '上架'
          AND { _scope_filter_sql() }
    """

    params = [user_id]

    # keyword 搜索：title/content/brand/tag_name
    keyword = (keyword or "").strip()
    if keyword:
        like = f"%{keyword}%"
        sql += " AND (p.title LIKE %s OR p.content LIKE %s OR p.brand LIKE %s OR t.tag_name LIKE %s)"
        params.extend([like, like, like, like])

    # tag_id 精确过滤
    if tag_id:
        sql += " AND p.tag_id = %s"
        params.append(tag_id)

    # 用户选择的“地理范围过滤”（不是p.scope）
    sql += _range_filter_sql(scope)

    sql += " ORDER BY p.created_at DESC"

    return query_all(sql, params, as_dict=True)


# ======================================================
# 2️⃣ 按标签搜索（自动包含帖子可见性 + 支持用户选择范围过滤）
# ======================================================
def search_by_tag(tag_id, user_id, scope="全部"):
    if not user_id:
        return []

    sql = f"""
        SELECT 
            p.posting_id, p.title, p.content, p.price, p.quantity,
            p.tag_id, t.tag_name, p.scope, p.status, p.created_at,
            poster.username AS owner_name,
            poster.room_id AS owner_room,
            poster.floor AS owner_floor,
            poster.building AS owner_building
        FROM posting p
        LEFT JOIN tag t ON p.tag_id = t.tag_id
        JOIN (
            SELECT u.user_id, u.username, r.room_id, r.floor, r.building
            FROM user u
            JOIN room r ON u.room_id = r.room_id
        ) AS poster ON p.owner_id = poster.user_id
        JOIN (
            SELECT r.room_id, r.floor, r.building
            FROM room r
            JOIN user u ON u.room_id = r.room_id
            WHERE u.user_id = %s
        ) AS viewer
        WHERE p.status = '上架'
          AND p.tag_id = %s
          AND { _scope_filter_sql() }
    """

    params = [user_id, tag_id]

    sql += _range_filter_sql(scope)
    sql += " ORDER BY p.created_at DESC"

    return query_all(sql, params, as_dict=True)


# ======================================================
# 3️⃣ 标签模糊搜索（输入框自动提示）
# ======================================================
def search_tags_fuzzy(query):
    sql = """
        SELECT tag_id, tag_name
        FROM tag
        WHERE tag_name LIKE %s
        ORDER BY ref_count DESC
        LIMIT 10
    """
    return query_all(sql, [f"%{query}%"], as_dict=True)


# ======================================================
# 4️⃣ 获取全部标签
# ======================================================
def get_all_tags():
    sql = "SELECT tag_id, tag_name, ref_count FROM tag ORDER BY ref_count DESC"
    return query_all(sql, as_dict=True)
