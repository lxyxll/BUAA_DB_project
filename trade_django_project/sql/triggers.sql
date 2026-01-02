DELIMITER $$

CREATE TRIGGER trg_order_check_seller
BEFORE INSERT ON `order`
FOR EACH ROW
BEGIN
    DECLARE real_seller INT;

    SELECT owner_id
    INTO real_seller
    FROM posting
    WHERE posting_id = NEW.posting_id;

    IF real_seller IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'posting 不存在';
    END IF;

    IF NEW.seller_id <> real_seller THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '订单 seller_id 与 posting.owner_id 不一致';
    END IF;
END $$


CREATE TRIGGER trg_order_confirm
AFTER UPDATE ON `order`
FOR EACH ROW
BEGIN
    IF NEW.status = '已交接'
       AND OLD.status <> '已交接' THEN

        UPDATE posting
        SET quantity = quantity - NEW.num
        WHERE posting_id = NEW.posting_id;

        UPDATE posting
        SET status = '已约满'
        WHERE posting_id = NEW.posting_id
          AND quantity <= 0;
    END IF;
END $$

DELIMITER ;
