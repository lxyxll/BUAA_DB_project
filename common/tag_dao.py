from common.db import query_all

def get_all_tags():
    sql = """
        SELECT tag_id, tag_name
        FROM tag
        ORDER BY tag_name
    """
    return query_all(sql, as_dict=True)
