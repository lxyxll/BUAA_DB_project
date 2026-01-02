# common/order_dao.py
# ======================================================
# 订单 Order 的数据访问层（下单、查询、状态流转）
# ======================================================

from common.db import query_one, query_all, execute, call_proc


# ======================================================
# 1. 下单（调用存储过程 create_order_proc）
# ======================================================
def create_order_by_proc(posting_id, buyer_id, quantity):
    """
    调用存储过程：
        CALL create_order_proc(p_posting_id, p_buyer_id, p_quantity)
    内部已检查库存是否足够，不足会抛出异常。
    """
    try:
        call_proc("create_order_proc", [posting_id, buyer_id, quantity])
        return True
    except Exception as e:
        # 存储过程库存不足会触发 SIGNAL
        print("下单失败:", e)
        return False


# ======================================================
# 2. 获取买家订单（查询 buyer_id）
# ======================================================
def get_buyer_orders(user_id):
    sql = """
        SELECT o.order_id, o.num, o.status, o.created_at,
               p.title, p.price, u.username AS seller_name
        FROM `order` o
        JOIN posting p ON o.posting_id = p.posting_id
        JOIN user u ON o.seller_id = u.user_id
        WHERE o.buyer_id = %s
        ORDER BY o.created_at DESC
    """
    return query_all(sql, [user_id], as_dict=True)


# ======================================================
# 3. 获取卖家订单（查询 seller_id）
# ======================================================
def get_seller_orders(user_id):
    sql = """
        SELECT o.order_id, o.num, o.status, o.created_at,
               p.title, p.price, u.username AS buyer_name
        FROM `order` o
        JOIN posting p ON o.posting_id = p.posting_id
        JOIN user u ON o.buyer_id = u.user_id
        WHERE o.seller_id = %s
        ORDER BY o.created_at DESC
    """
    return query_all(sql, [user_id], as_dict=True)


# ======================================================
# 4. 订单详情
# ======================================================
def get_order_detail(order_id):
    sql = """
        SELECT o.*, 
               p.title, p.price, p.brand, p.quantity AS posting_quantity,
               ub.username AS buyer_name,
               us.username AS seller_name
        FROM `order` o
        JOIN posting p ON o.posting_id = p.posting_id
        JOIN user ub ON o.buyer_id = ub.user_id
        JOIN user us ON o.seller_id = us.user_id
        WHERE o.order_id = %s
    """
    return query_one(sql, [order_id], as_dict=True)


# ======================================================
# 5. 卖家确认交接（调用 confirm_order_proc）
#    状态：待交接 → 已交接
# ======================================================
def confirm_order_by_proc(order_id):
    try:
        call_proc("confirm_order_proc", [order_id])
        return True
    except Exception as e:
        print("确认订单失败:", e)
        return False


# ======================================================
# 6. 完成订单（状态：已交接 → 完成）
# ======================================================
def complete_order_by_proc(order_id, user_id):
    try:
        call_proc("complete_order_proc", [order_id, user_id])
        return True
    except Exception as e:
        print("完成订单失败:", e)
        return False


# ======================================================
# 7. 取消订单（调用 cancel_order_proc）
# ======================================================
def cancel_order_by_proc(order_id, reason, user_id):
    try:
        call_proc("cancel_order_proc", [order_id, reason, user_id])
        return True
    except Exception as e:
        print("取消订单失败:", e)
        return False

