# common/complaint_dao.py
# ======================================================
# 投诉模块 DAO：提交投诉、查询投诉、管理员处理
# ======================================================

from common.db import query_one, query_all, execute

# ====== 状态常量（统一管理）======
STATUS_PENDING = "待处理"
STATUS_PROCESSING = "处理中"
STATUS_RESOLVED = "已处理"
STATUS_REJECTED = "驳回"


def _has_open_complaint(order_id, complainant_id):
    """
    同一用户对同一订单是否已有未关闭投诉（待处理/处理中）
    """
    sql = """
        SELECT COUNT(*)
        FROM complaint
        WHERE order_id = %s
          AND complainant_id = %s
          AND status IN (%s, %s)
    """
    row = query_one(sql, [order_id, complainant_id, STATUS_PENDING, STATUS_PROCESSING])
    return (row and row[0] > 0)


# ======================================================
# 工具函数：根据订单 ID 获取被投诉者（通常为卖家）
# ======================================================
def _get_accused_id(order_id):
    """
    根据订单 ID 查询卖家 ID 作为被投诉者。
    """
    sql = """
        SELECT seller_id
        FROM `order`
        WHERE order_id = %s
    """
    row = query_one(sql, [order_id])
    if row:
        return row[0]
    return None


# ======================================================
# 1️⃣ 用户提交投诉
# ======================================================
def submit_complaint(order_id, complainant_id, content):
    """
    用户提交投诉：
    - accused_id（被投诉人）来自订单 seller_id
    - 状态初始为“待处理”
    - 防重复：同一用户同一订单若存在待处理/处理中投诉，禁止重复提交
    - 校验：内容不能为空；不能投诉自己
    """
    content = (content or "").strip()
    if not content:
        raise Exception("投诉内容不能为空")

    accused_id = _get_accused_id(order_id)
    if accused_id is None:
        raise Exception("订单不存在，无法提交投诉")

    if int(accused_id) == int(complainant_id):
        raise Exception("不能对自己发起投诉")

    if _has_open_complaint(order_id, complainant_id):
        raise Exception("该订单你已提交过投诉，管理员处理中，请勿重复提交")

    sql = """
        INSERT INTO complaint(order_id, complainant_id, accused_id, content, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    execute(sql, [order_id, complainant_id, accused_id, content, STATUS_PENDING])

# ======================================================
# 2️⃣ 用户查看自己的投诉记录
# ======================================================
def get_my_complaints(user_id):
    sql = """
        SELECT c.*, 
               o.posting_id,
               p.title AS posting_title,
               u.username AS accused_name
        FROM complaint c
        JOIN `order` o ON c.order_id = o.order_id
        JOIN posting p ON o.posting_id = p.posting_id
        JOIN user u ON c.accused_id = u.user_id
        WHERE c.complainant_id = %s
        ORDER BY c.created_at DESC
    """
    return query_all(sql, [user_id], as_dict=True)


# ======================================================
# 3️⃣ 按订单查看投诉（买家/卖家均可查看）
# ======================================================
def get_complaints_by_order(order_id):
    sql = """
        SELECT c.*, 
               u1.username AS complainant_name,
               u2.username AS accused_name
        FROM complaint c
        JOIN user u1 ON c.complainant_id = u1.user_id
        JOIN user u2 ON c.accused_id = u2.user_id
        WHERE c.order_id = %s
        ORDER BY c.created_at DESC
    """
    return query_all(sql, [order_id], as_dict=True)


# ======================================================
# 4️⃣ 投诉详情
# ======================================================
def get_complaint_detail(complaint_id):
    sql = """
        SELECT c.*, 
               u1.username AS complainant_name,
               u2.username AS accused_name,
               p.title AS posting_title
        FROM complaint c
        JOIN user u1 ON c.complainant_id = u1.user_id
        JOIN user u2 ON c.accused_id = u2.user_id
        JOIN `order` o ON c.order_id = o.order_id
        JOIN posting p ON o.posting_id = p.posting_id
        WHERE c.complaint_id = %s
    """
    return query_one(sql, [complaint_id], as_dict=True)


# ======================================================
# 5️⃣ 管理员查看所有“待处理”投诉
# ======================================================
def admin_get_pending_complaints():
    sql = """
        SELECT c.*, 
               u1.username AS complainant_name,
               u1.username AS user_name,
               u2.username AS accused_name,
               p.title AS posting_title
        FROM complaint c
        JOIN user u1 ON c.complainant_id = u1.user_id
        JOIN user u2 ON c.accused_id = u2.user_id
        JOIN `order` o ON c.order_id = o.order_id
        JOIN posting p ON o.posting_id = p.posting_id
        WHERE c.status = %s
        ORDER BY c.created_at DESC
    """
    return query_all(sql, [STATUS_PENDING], as_dict=True)

def admin_get_complaints(status=None):
    """
    管理员：投诉列表（全部/按状态过滤）
    返回字段至少包含：admin_complaint_list.html 需要的 complaint_id/order_id/user_name/status
    """
    sql = """
        SELECT c.*,
               u1.username AS user_name,
               u1.username AS complainant_name,
               u2.username AS accused_name,
               p.title AS posting_title
        FROM complaint c
        JOIN user u1 ON c.complainant_id = u1.user_id
        JOIN user u2 ON c.accused_id = u2.user_id
        JOIN `order` o ON c.order_id = o.order_id
        JOIN posting p ON o.posting_id = p.posting_id
    """
    if status:
        sql += " WHERE c.status = %s "
        return query_all(sql + " ORDER BY c.created_at DESC ", [status], as_dict=True)

    return query_all(sql + " ORDER BY c.created_at DESC ", as_dict=True)

# ======================================================
# 6️⃣ 管理员处理投诉（写入 result）
# ======================================================
def admin_handle_complaint(complaint_id, result, admin_user_id=None, new_status=STATUS_RESOLVED):
    """
    管理员处理投诉（增强版）：
    - 默认 new_status = 已处理
    - admin_user_id 可选：写入 handled_by（如果表字段存在）
    - 自动尝试写 handled_at=NOW()（如果表字段存在）
    - 兼容旧调用：admin_handle_complaint(complaint_id, result)
    """
    result = (result or "").strip()
    if not result:
        raise Exception("处理结果不能为空")

    # 投诉是否存在
    exists = query_one("SELECT complaint_id FROM complaint WHERE complaint_id = %s", [complaint_id])
    if not exists:
        raise Exception("投诉不存在")

    # 先尝试写入 handled_by/handled_at（若字段不存在则回退）
    try:
        sql = """
            UPDATE complaint
            SET status = %s,
                result = %s,
                handled_by = %s,
                handled_at = NOW()
            WHERE complaint_id = %s
        """
        execute(sql, [new_status, result, admin_user_id, complaint_id])
    except Exception:
        sql = """
            UPDATE complaint
            SET status = %s,
                result = %s
            WHERE complaint_id = %s
        """
        execute(sql, [new_status, result, complaint_id])

def admin_mark_processing(complaint_id):
    sql = """
        UPDATE complaint
        SET status = %s
        WHERE complaint_id = %s AND status = %s
    """
    execute(sql, [STATUS_PROCESSING, complaint_id, STATUS_PENDING])

