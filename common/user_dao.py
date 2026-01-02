# common/user_dao.py
# ======================================================
# 用户模块 DAO：注册、登录、资料修改、寝室绑定、管理员管理
# ======================================================

from common.db import query_one, query_all, execute


# ======================================================
# 1️⃣ 注册：检查 email / student_id / username 是否重复
# ======================================================
def check_user_exists(email, student_id, username):
    sql = """
        SELECT COUNT(*)
        FROM user
        WHERE email = %s OR student_id = %s OR username = %s
    """
    row = query_one(sql, [email, student_id, username])
    return row[0] > 0


# ======================================================
# 2️⃣ 注册：插入新用户
#    role = 0（普通用户）
#    user_role = 1（普通权限）
#    status = '正常'
# ======================================================
def insert_user(username, password, email, wechat, student_id, room_id, role=0, user_role=1):
    sql = """
        INSERT INTO user(username, password, email, wechat, student_id, role, user_role, status, room_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, '正常', %s)
    """
    execute(sql, [username, password, email, wechat, student_id, role, user_role, room_id])


# ======================================================
# 3️⃣ 登录：根据 student_id 查找用户（用于密码比对）
# ======================================================
def get_user_by_student_id(student_id):
    sql = """
        SELECT user_id, username, password, status, role, user_role
        FROM user
        WHERE student_id = %s
    """
    row = query_one(sql, [student_id])
    return row  # (user_id, username, password, status, role, user_role)



# ======================================================
# 4️⃣ 获取完整用户信息（用于 profile 显示）
# ======================================================
def get_user_by_id(user_id):
    sql = """
        SELECT u.user_id, u.username, u.email, u.wechat, u.student_id,
               u.role, u.user_role, u.status,
               u.room_id, r.floor, r.building
        FROM user u
        LEFT JOIN room r ON u.room_id = r.room_id
        WHERE u.user_id = %s
    """
    return query_one(sql, [user_id], as_dict=True)


# ======================================================
# 5️⃣ 修改个人资料（邮箱、微信、寝室）
# ======================================================
def update_user_profile(email, wechat, room_id, user_id):
    sql = """
        UPDATE user
        SET email = %s,
            wechat = %s,
            room_id = %s
        WHERE user_id = %s
    """
    execute(sql, [email, wechat, room_id, user_id])


# ======================================================
# 6️⃣ 修改密码
# ======================================================
def update_user_password(user_id, new_password):
    sql = """
        UPDATE user
        SET password = %s
        WHERE user_id = %s
    """
    execute(sql, [new_password, user_id])


# ======================================================
# 7️⃣ 获取所有寝室信息，用于注册/个人资料绑定
# ======================================================
def get_room_list():
    sql = """
        SELECT room_id, floor, building, room_no
        FROM room
        ORDER BY building, floor
    """
    return query_all(sql, as_dict=True)


# ======================================================
# 8️⃣ 绑定寝室（如果提供了绑定入口）
# ======================================================
def bind_room(user_id, room_id):
    sql = """
        UPDATE user
        SET room_id = %s
        WHERE user_id = %s
    """
    execute(sql, [room_id, user_id])


# ======================================================
# 9️⃣ 管理员：获取所有用户列表
# ======================================================
def admin_get_all_users():
    sql = """
        SELECT u.user_id, u.username, u.email, u.student_id,
               u.status, u.user_role, u.room_id,
               r.floor, r.building
        FROM user u
        LEFT JOIN room r ON u.room_id = r.room_id
        ORDER BY u.user_id
    """
    return query_all(sql, as_dict=True)


# ======================================================
# 🔟 管理员：封禁用户
# ======================================================
def ban_user_by_id(user_id):
    sql = """
        UPDATE user
        SET status = '封禁'
        WHERE user_id = %s
    """
    execute(sql, [user_id])


# ======================================================
# 1️⃣1️⃣ 管理员：解封用户
# ======================================================
def unban_user_by_id(user_id):
    sql = """
        UPDATE user
        SET status = '正常'
        WHERE user_id = %s
    """
    execute(sql, [user_id])
