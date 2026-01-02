SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE image;
TRUNCATE TABLE complaint;
TRUNCATE TABLE notice;
TRUNCATE TABLE `order`;
TRUNCATE TABLE favorite;
TRUNCATE TABLE posting;
TRUNCATE TABLE tag;
TRUNCATE TABLE user;
TRUNCATE TABLE room;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 1. 插入寝室（Room）
-- ============================================
INSERT INTO room (building, floor, room_no)
VALUES
('1号楼', 3, '301'),
('1号楼', 3, '302'),
('1号楼', 4, '401'),
('2号楼', 5, '501');

-- ============================================
-- 2. 插入用户（User）
-- ============================================
INSERT INTO user (username, password, email, wechat, student_id, role, user_role, status, room_id)
VALUES
('alice', '123456', 'alice@example.com', 'wx_alice', '20220001', 0, 1, '正常', 1),
('bob', '123456', 'bob@example.com', 'wx_bob', '20220002', 0, 1, '正常', 1),
('charlie', '123456', 'charlie@example.com', 'wx_charlie', '20220003', 1, 2, '正常', 2),
('admin', 'admin', 'admin@example.com', 'wx_admin', '99999999', 1, 3, '正常', 3);

-- ============================================
-- 3. 标签（Tag）
-- ============================================
INSERT INTO tag (tag_name, ref_count)
VALUES
('电子产品', 0),
('学习用品', 0),
('生活用品', 0),
('体育用品', 0);

-- ============================================
-- 4. 出物帖（Posting）
--    注意：condition 必须写成 `condition`
-- ============================================
INSERT INTO posting
(title, content, price, quantity, brand, `condition`, tag_id, status, scope, owner_id)
VALUES
('二手耳机出让', '成色很好，音质不错', 50.00, 3, 'Sony', '几乎全新', 1, '上架', '全楼', 1),
('九成新台灯', '适合学习，亮度可调', 20.00, 5, 'MI', '轻微使用痕迹', 2, '上架', '楼层', 1),
('保温杯', '无磕碰，容量大', 10.00, 2, 'Fuguang', '全新', 3, '上架', '寝室', 2),
('篮球', '标准尺寸，弹性好', 30.00, 1, 'LiNing', '几乎全新', 4, '上架', '楼栋', 3);

UPDATE tag SET ref_count = ref_count + 1 WHERE tag_id IN (1,2,3,4);

-- ============================================
-- 5. 收藏（Favorite）
-- ============================================
INSERT INTO favorite(user_id, posting_id)
VALUES
(1, 1),
(1, 2),
(2, 1);

-- ============================================
-- 6. 订单（Order）
-- ============================================
INSERT INTO `order`
(posting_id, buyer_id, seller_id, num, status)
VALUES
(1, 2, 1, 1, '待交接'),
(2, 2, 1, 2, '已交接'),
(3, 3, 2, 1, '完成');

-- ============================================
-- 7. 消息通知（Notice）
-- ============================================
INSERT INTO notice(type, content, receiver_id, related_order_id, status)
VALUES
('系统', '欢迎使用 DormSwap 系统', 1, NULL, '未读'),
('交接提醒', '您的订单 #2 已交接', 2, 2, '未读'),
('公告', '今晚 10 点后宿舍停电维护', 1, NULL, '未读');

-- ============================================
-- 8. 投诉（Complaint）
-- ============================================
INSERT INTO complaint(order_id, complainant_id, accused_id, content, status)
VALUES
(2, 2, 1, '卖家迟到很久', '待处理');

-- ============================================
-- 9. 图片（Image）
-- ============================================
INSERT INTO image(posting_id, uploader_id, path, category)
VALUES
(1, 1, '/uploads/earphone.jpg', '物品照片'),
(2, 1, '/uploads/lamp.jpg', '物品照片'),
(3, 2, '/uploads/cup.jpg', '物品照片');
