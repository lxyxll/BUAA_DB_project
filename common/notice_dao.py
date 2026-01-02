# common/notice_dao.py
# ======================================================
# 消息 / 公告 Notice 模块 DAO
# ======================================================

from common.db import query_one, query_all, execute


# ======================================================
# 获取用户全部消息
# ======================================================
def get_user_notices(user_id):
    sql = """
        SELECT notice_id, type, content, status, created_at, related_order_id
        FROM notice
        WHERE receiver_id = %s
        ORDER BY created_at DESC
    """
    return query_all(sql, [user_id], as_dict=True)


# ======================================================
# 获取用户未读消息
# ======================================================
def get_unread_notices(user_id):
    sql = """
        SELECT notice_id, type, content, status, created_at, related_order_id
        FROM notice
        WHERE receiver_id = %s AND status = '未读'
        ORDER BY created_at DESC
    """
    return query_all(sql, [user_id], as_dict=True)


# ======================================================
# 标记消息为已读
# ======================================================
def mark_notice_read(notice_id, user_id):
    sql = """
        UPDATE notice
        SET status = '已读'
        WHERE notice_id = %s AND receiver_id = %s
    """
    execute(sql, [notice_id, user_id])

# ======================================================
# 创建用户消息（系统/交接提醒）
# ======================================================
def create_user_notice(receiver_id, content, notice_type="系统", related_order_id=None):
    """
    创建一条发给某个用户的消息通知：
    notice_type 只能是 '系统' 或 '交接提醒'
    """
    if notice_type not in ("系统", "交接提醒"):
        raise Exception("notice_type 只能是 '系统' 或 '交接提醒'")

    receiver_id = int(receiver_id)
    content = (content or "").strip()
    if not content:
        raise Exception("消息内容不能为空")

    sql = """
        INSERT INTO notice(type, content, receiver_id, related_order_id, status)
        VALUES (%s, %s, %s, %s, '未读')
    """
    execute(sql, [notice_type, content, receiver_id, related_order_id])


def create_notice_for_admins(content, notice_type="系统", related_order_id=None):
    """
    给所有管理员（user_role=3）发一条通知。
    说明：如果你库里管理员字段不是 user_role=3，请按你的实际字段改 SQL。
    """
    content = (content or "").strip()
    if not content:
        raise Exception("消息内容不能为空")

    admin_rows = query_all("SELECT user_id FROM user WHERE user_role = 3", as_dict=False)
    admin_ids = [r[0] for r in admin_rows] if admin_rows else []

    for admin_id in admin_ids:
        create_user_notice(admin_id, content, notice_type=notice_type, related_order_id=related_order_id)


# ======================================================
# 获取所有公告（type = '公告'）
# ======================================================
def get_announcements():
    sql = """
        SELECT notice_id, title, created_at
        FROM notice
        WHERE type = '公告'
        ORDER BY created_at DESC
    """
    return query_all(sql, as_dict=True)


# ======================================================
# 公告详情
# ======================================================
def get_announcement_detail(notice_id):
    sql = """
        SELECT notice_id, title, content, created_at
        FROM notice
        WHERE notice_id = %s AND type = '公告'
    """
    return query_one(sql, [notice_id], as_dict=True)

# ======================================================
# 管理员发布公告（插入 notice 表）
# ======================================================
def admin_publish_announcement(title, content):
    title = (title or "").strip()
    content = (content or "").strip()
    if not title:
        raise Exception("公告标题不能为空")
    if not content:
        raise Exception("公告内容不能为空")

    sql = """
        INSERT INTO notice(type, title, content, receiver_id, related_order_id, status)
        VALUES ('公告', %s, %s, NULL, NULL, '未读')
    """
    execute(sql, [title, content])



# ======================================================
# 管理员删除公告
# ======================================================
def admin_delete_announcement(notice_id):
    sql = """
        DELETE FROM notice
        WHERE notice_id = %s AND type = '公告'
    """
    execute(sql, [notice_id])
