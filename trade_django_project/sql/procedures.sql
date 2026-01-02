-- ================================
-- procedures.sql（修改版）
-- 完成订单 / 取消订单 都补齐 notice 逻辑
-- ================================

DELIMITER $$

-- 1) 创建订单：不改（你原来就是正确的）
DROP PROCEDURE IF EXISTS create_order_proc $$
CREATE PROCEDURE create_order_proc(
    IN p_posting_id INT,
    IN p_buyer_id INT,
    IN p_quantity INT
)
BEGIN
    DECLARE p_seller_id INT;
    DECLARE p_stock INT;

    SELECT owner_id, quantity INTO p_seller_id, p_stock
    FROM posting
    WHERE posting_id = p_posting_id;

    IF p_stock < p_quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '库存不足';
    END IF;

    INSERT INTO `order`(posting_id, buyer_id, seller_id, num)
    VALUES(p_posting_id, p_buyer_id, p_seller_id, p_quantity);
END $$


-- 2) 确认交接：不改（你原来正确：卖家确认 → 买家收到通知）
DROP PROCEDURE IF EXISTS confirm_order_proc $$
CREATE PROCEDURE confirm_order_proc(
    IN p_order_id INT
)
BEGIN
    UPDATE `order`
    SET status = '已交接',
        confirmed_at = CURRENT_TIMESTAMP
    WHERE order_id = p_order_id;

    INSERT INTO notice(type, content, receiver_id, related_order_id)
    SELECT '交接提醒',
           '您的订单已确认交接，请及时完成线下交接。',
           buyer_id,
           order_id
    FROM `order`
    WHERE order_id = p_order_id;
END $$


-- 3) 完成订单：新增（或改造）
--    由买家/卖家任一方发起完成 → 通知对方
DROP PROCEDURE IF EXISTS complete_order_proc $$
CREATE PROCEDURE complete_order_proc(
    IN p_order_id INT,
    IN p_user_id INT
)
BEGIN
    DECLARE v_buyer INT;
    DECLARE v_seller INT;
    DECLARE v_other INT;
    DECLARE v_name VARCHAR(150);

    SELECT buyer_id, seller_id INTO v_buyer, v_seller
    FROM `order`
    WHERE order_id = p_order_id;

    IF v_buyer IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '订单不存在';
    END IF;

    IF p_user_id <> v_buyer AND p_user_id <> v_seller THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '无权限完成该订单';
    END IF;

    -- 只能从“已交接”变成“完成”
    UPDATE `order`
    SET status = '完成'
    WHERE order_id = p_order_id
      AND status = '已交接';

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '订单状态不允许完成（必须先已交接）';
    END IF;

    -- 找到对方
    SET v_other = IF(p_user_id = v_buyer, v_seller, v_buyer);

    -- 发起者名字（可选但更友好）
    SELECT username INTO v_name FROM user WHERE user_id = p_user_id;

    INSERT INTO notice(type, content, receiver_id, related_order_id)
    VALUES(
        '系统',
        CONCAT('订单已完成（由 ', v_name, ' 完成确认）。'),
        v_other,
        p_order_id
    );
END $$


-- 4) 取消订单：改造（关键：取消者通知对方，而不是固定通知 buyer）
DROP PROCEDURE IF EXISTS cancel_order_proc $$
CREATE PROCEDURE cancel_order_proc(
    IN p_order_id INT,
    IN p_reason VARCHAR(200),
    IN p_user_id INT
)
BEGIN
    DECLARE v_buyer INT;
    DECLARE v_seller INT;
    DECLARE v_other INT;
    DECLARE v_name VARCHAR(150);

    SELECT buyer_id, seller_id INTO v_buyer, v_seller
    FROM `order`
    WHERE order_id = p_order_id;

    IF v_buyer IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '订单不存在';
    END IF;

    IF p_user_id <> v_buyer AND p_user_id <> v_seller THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '无权限取消该订单';
    END IF;

    -- 只允许取消未完成的订单（你也可以只允许“待交接”）
    UPDATE `order`
    SET status = '取消',
        cancel_reason = p_reason
    WHERE order_id = p_order_id
      AND status <> '完成'
      AND status <> '取消';

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '订单状态不允许取消（已取消/已完成）';
    END IF;

    SET v_other = IF(p_user_id = v_buyer, v_seller, v_buyer);
    SELECT username INTO v_name FROM user WHERE user_id = p_user_id;

    INSERT INTO notice(type, content, receiver_id, related_order_id)
    VALUES(
        '系统',
        CONCAT('订单已被 ', v_name, ' 取消，原因：', p_reason),
        v_other,
        p_order_id
    );
END $$

DELIMITER ;
