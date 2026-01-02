# common/posting_dao.py
# ======================================================
# 出物帖 Posting + 图片 Image + 收藏 Favorite 的 DAO 层
# ======================================================

from common.db import query_one, query_all, execute


# ======================================================
# 1. 获取帖子列表（上架状态）
# ======================================================
def get_posting_list():
    sql = """
        SELECT posting_id, title, price, quantity, brand, image_url, `condition`, tag_id, status, scope, owner_id, created_at
        FROM posting
        WHERE status = '上架'
        ORDER BY created_at DESC
    """
    return query_all(sql, as_dict=True)

def get_my_postings(owner_id):
    sql = """
        SELECT
            posting_id,
            title,
            price,
            quantity,
            status,
            scope,
            created_at
        FROM posting
        WHERE owner_id = %s
        ORDER BY created_at DESC
    """
    return query_all(sql, [owner_id], as_dict=True)

# ======================================================
# 2. 获取帖子详情（含发布者、标签基本信息）
# ======================================================
def get_posting_detail(posting_id):
    sql = """
        SELECT p.*, u.username, u.room_id, t.tag_name
        FROM posting p
        LEFT JOIN user u ON p.owner_id = u.user_id
        LEFT JOIN tag t ON p.tag_id = t.tag_id
        WHERE posting_id = %s
    """
    return query_one(sql, [posting_id], as_dict=True)


# ======================================================
# 3. 发布帖子（INSERT INTO posting）
# ======================================================
def create_posting(title, content, price, quantity, brand, image_url, condition, tag_id, scope, owner_id):
    sql = """
        INSERT INTO posting
        (title, content, price, quantity, brand, image_url, `condition`, tag_id, status, scope, owner_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '上架', %s, %s)
    """
    execute(sql, [title, content, price, quantity, brand, image_url, condition, tag_id, scope, owner_id])



# ======================================================
# 4. 修改帖子（发布者校验在 views 中做）
# ======================================================
def update_posting(posting_id, title, content, price, quantity, brand, condition, tag_id, scope, owner_id):
    sql = """
        UPDATE posting
        SET title = %s,
            content = %s,
            price = %s,
            quantity = %s,
            brand = %s,
            image_url = %s,
            `condition` = %s,
            tag_id = %s,
            scope = %s
        WHERE posting_id = %s AND owner_id = %s
    """
    execute(sql, [title, content, price, quantity, brand, None, condition, tag_id, scope, posting_id, owner_id])



# ======================================================
# 5. 删除帖子（软删除：status='下架'）
# ======================================================
def soft_delete_posting(posting_id, owner_id):
    sql = """
        UPDATE posting
        SET status = '下架'
        WHERE posting_id = %s AND owner_id = %s
    """
    execute(sql, [posting_id, owner_id])


# ======================================================
# 6. 修改帖子可见范围（寝室/楼层/楼栋/全楼）
# ======================================================
def change_scope(posting_id, owner_id, new_scope):
    sql = """
        UPDATE posting
        SET scope = %s
        WHERE posting_id = %s AND owner_id = %s
    """
    execute(sql, [new_scope, posting_id, owner_id])


# ======================================================
# 7. 图片管理 —— 插入图片记录
# ======================================================
def add_posting_image(posting_id, uploader_id, path, category):
    sql = """
        INSERT INTO image(posting_id, uploader_id, path, category)
        VALUES (%s, %s, %s, %s)
    """
    execute(sql, [posting_id, uploader_id, path, category])


# ======================================================
# 8. 图片管理 —— 删除图片记录
# ======================================================
def delete_posting_image(image_id, uploader_id):
    sql = """
        DELETE FROM image
        WHERE image_id = %s AND uploader_id = %s
    """
    execute(sql, [image_id, uploader_id])


# ======================================================
# 9. 获取帖子所有图片
# ======================================================
def get_posting_images(posting_id):
    sql = """
        SELECT image_id, path, category
        FROM image
        WHERE posting_id = %s
    """
    return query_all(sql, [posting_id], as_dict=True)


# ======================================================
# 10. 收藏功能 —— 添加收藏
# ======================================================
def add_favorite(user_id, posting_id):
    sql = """
        INSERT INTO favorite(user_id, posting_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE created_at = CURRENT_TIMESTAMP
    """
    execute(sql, [user_id, posting_id])


# ======================================================
# 11. 收藏功能 —— 取消收藏
# ======================================================
def remove_favorite(user_id, posting_id):
    sql = """
        DELETE FROM favorite
        WHERE user_id = %s AND posting_id = %s
    """
    execute(sql, [user_id, posting_id])


# ======================================================
# 12. 收藏功能 —— 查看用户收藏列表
# ======================================================
def get_user_favorites(user_id):
    sql = """
        SELECT p.posting_id, p.title, p.price, p.brand, p.scope, f.created_at
        FROM posting p
        JOIN favorite f ON p.posting_id = f.posting_id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
    """
    return query_all(sql, [user_id], as_dict=True)


# ======================================================
# 13. 判断某帖子是否被某用户收藏（用于详情页）
# ======================================================
def is_favorite(user_id, posting_id):
    sql = """
        SELECT 1
        FROM favorite
        WHERE user_id = %s AND posting_id = %s
        LIMIT 1
    """
    row = query_one(sql, [user_id, posting_id])
    return row is not None
