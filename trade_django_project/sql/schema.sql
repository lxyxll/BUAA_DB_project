-- ================================
-- schema.sql
-- 大作业数据库建表脚本（GaussDB for MySQL）
-- ================================

DROP TABLE IF EXISTS complaint;
DROP TABLE IF EXISTS notice;
DROP TABLE IF EXISTS `order`;
DROP TABLE IF EXISTS favorite;
DROP TABLE IF EXISTS image;
DROP TABLE IF EXISTS posting;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS room;

-- ================================
-- 1. Room 寝室房间
-- ================================
CREATE TABLE room (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    building VARCHAR(50) NOT NULL,
    floor INT NOT NULL,
    room_no VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_room (building, floor, room_no),
    INDEX idx_room (building, floor, room_no)
);

-- ================================
-- 2. User 用户（融合系统 + Django + 大作业字段）
-- ================================
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(150) NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(150),
    wechat VARCHAR(30) UNIQUE,
    student_id VARCHAR(20) UNIQUE,

    role TINYINT NOT NULL DEFAULT 0 CHECK (role IN (0,1)),
    user_role TINYINT NOT NULL DEFAULT 1 CHECK (user_role IN (1,2,3)),
    status ENUM('正常','封禁') NOT NULL DEFAULT '正常',

    room_id INT NOT NULL,

    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (room_id) REFERENCES room(room_id),
    INDEX idx_wechat (wechat),
    INDEX idx_room (room_id),
    INDEX idx_status (status)
);

-- ================================
-- 3. Tag 标签
-- ================================
CREATE TABLE tag (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL UNIQUE,
    ref_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ================================
-- 4. Posting 出物帖（修正版：保留字段名但用反引号避免冲突）
-- ================================
CREATE TABLE posting (
    posting_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    price DECIMAL(10,2) UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL DEFAULT 0,
    brand VARCHAR(50),
    image_url VARCHAR(255) DEFAULT NULL COMMENT '封面图片URL(演示/展示用)',

    `condition` ENUM('全新','几乎全新','轻微使用痕迹','空'),  

    tag_id INT,
    status ENUM('上架','下架','已约满') NOT NULL DEFAULT '上架',
    scope ENUM('寝室','楼层','楼栋','全楼') NOT NULL DEFAULT '全楼',

    owner_id INT NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (tag_id) REFERENCES tag(tag_id),
    FOREIGN KEY (owner_id) REFERENCES user(user_id),

    INDEX idx_owner (owner_id),
    INDEX idx_tag (tag_id),
    INDEX idx_status_scope (status, scope)
);


-- ================================
-- 5. Favorite 收藏
-- ================================
CREATE TABLE favorite (
    f_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    posting_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_favorite (user_id, posting_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (posting_id) REFERENCES posting(posting_id),
    INDEX idx_posting (posting_id)
);

-- ================================
-- 6. Order 订单
-- ================================
CREATE TABLE `order` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    posting_id INT NOT NULL,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    num INT NOT NULL CHECK (num > 0),

    status ENUM('待交接','已交接','完成','取消') NOT NULL DEFAULT '待交接',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at DATETIME,
    cancel_reason VARCHAR(200),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (posting_id) REFERENCES posting(posting_id),
    FOREIGN KEY (buyer_id) REFERENCES user(user_id),
    FOREIGN KEY (seller_id) REFERENCES user(user_id),

    INDEX idx_posting (posting_id),
    INDEX idx_buyer (buyer_id),
    INDEX idx_seller (seller_id)
);

-- ================================
-- 7. Notice 消息通知
-- ================================
CREATE TABLE notice (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('系统','交接提醒','公告') NOT NULL,
    content TEXT NOT NULL,
    receiver_id INT NOT NULL,
    related_order_id INT,

    status ENUM('未读','已读') NOT NULL DEFAULT '未读',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (receiver_id) REFERENCES user(user_id),
    FOREIGN KEY (related_order_id) REFERENCES `order`(order_id),

    INDEX idx_receiver (receiver_id),
    INDEX idx_related_order (related_order_id)
);

-- ================================
-- 8. Complaint 投诉
-- ================================
CREATE TABLE complaint (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    complainant_id INT NOT NULL,
    accused_id INT NOT NULL,

    content TEXT NOT NULL,
    status ENUM('待处理','已处理','驳回','处理中') NOT NULL DEFAULT '待处理',
    result VARCHAR(200),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    handled_at DATETIME,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id) REFERENCES `order`(order_id),
    FOREIGN KEY (complainant_id) REFERENCES user(user_id),
    FOREIGN KEY (accused_id) REFERENCES user(user_id),

    INDEX idx_order (order_id),
    INDEX idx_users (complainant_id, accused_id)
);

-- ================================
-- 9. Image 图片表（弱实体）
-- ================================
CREATE TABLE image (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    posting_id INT,
    uploader_id INT NOT NULL,
    path VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (posting_id) REFERENCES posting(posting_id),
    FOREIGN KEY (uploader_id) REFERENCES user(user_id)
);
