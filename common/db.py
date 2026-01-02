# common/db.py
# ================================================
# 大作业数据库访问层（Raw SQL）
# 全项目统一使用此文件执行 SQL
# ================================================

from django.db import connection


# ---------------------------------------
# 辅助函数：将 cursor 返回结果转为 dict
# ---------------------------------------
def dict_fetch_all(cursor):
    """返回多行数据（dict 列表）"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dict_fetch_one(cursor):
    """返回单行数据（dict）"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


# ---------------------------------------
# 执行 SELECT（返回单条记录）
# ---------------------------------------
def query_one(sql, params=None, as_dict=False):
    """
    执行查询（返回一行）
    as_dict = True → 返回 dict
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])

        if as_dict:
            return dict_fetch_one(cursor)
        else:
            return cursor.fetchone()


# ---------------------------------------
# 执行 SELECT（返回多条记录）
# ---------------------------------------
def query_all(sql, params=None, as_dict=False):
    """
    执行查询（返回多行）
    as_dict = True → 返回 dict 列表
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])

        if as_dict:
            return dict_fetch_all(cursor)
        else:
            return cursor.fetchall()


# ---------------------------------------
# 执行写操作（INSERT / UPDATE / DELETE）
# ---------------------------------------
def execute(sql, params=None):
    """
    执行 INSERT / UPDATE / DELETE
    返回 True 表示成功
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
    return True


# ---------------------------------------
# 调用存储过程（你已有 create_order_proc/confirm/cancel）
# ---------------------------------------
def call_proc(proc_name, params=None, as_dict=False):
    """
    调用存储过程：
        CALL proc_name(param1, param2);

    返回结果（如果过程有 SELECT）
    """
    with connection.cursor() as cursor:
        cursor.callproc(proc_name, params or [])

        # GaussDB/MySQL 中，存储过程执行后 cursor 会返回结果
        try:
            if as_dict:
                return dict_fetch_all(cursor)
            else:
                return cursor.fetchall()
        except:
            return None
