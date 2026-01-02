-- ============================================
-- init.sql
-- 一键初始化数据库（建表 + 触发器 + 存储过程）
-- ============================================

-- 推荐：使用事务避免部分失败
SET AUTOCOMMIT = 0;

-- 执行建表 SQL
SOURCE sql/schema.sql;

-- 执行触发器 SQL
SOURCE sql/triggers.sql;

-- 执行存储过程 SQL
SOURCE sql/procedures.sql;

-- 如需插入测试数据，可取消注释以下行
-- SOURCE sql/sample_data.sql;

COMMIT;

-- 显示所有表
SHOW TABLES;
