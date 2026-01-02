### 一、posting_views.py（出物 / 收藏）
| View 方法                | 功能   | 对应 HTML 页面            |
| ---------------------- | ---- | --------------------- |
| `posting_list`         | 出物大厅 | `posting_list.html`   |
| `posting_detail`       | 出物详情 | `post_detail.html`    |
| `create_posting_view`  | 发布出物 | `create_posting.html` |
| `edit_posting`         | 编辑出物 | `edit_posting.html`   |
| `delete_posting`       | 删除出物 | 【无页面】→ redirect       |
| `add_favorite_view`    | 收藏   | 【无页面】→ Ajax/redirect  |
| `remove_favorite_view` | 取消收藏 | 【无页面】→ Ajax/redirect  |
| `favorite_list_view`   | 我的收藏 | `favorite_list.html`  |

### 二、order_views.py（订单）
| View 方法               | 功能     | 对应 HTML 页面               |
| --------------------- | ------ | ------------------------ |
| `create_order_view`   | 创建订单   | `create_order.html`      |
| `order_buyer_list`    | 买家订单列表 | `order_buyer_list.html`  |
| `order_seller_list`   | 卖家订单列表 | `order_seller_list.html` |
| `order_detail_view`   | 订单详情   | `order_detail.html`      |
| `confirm_order_view`  | 确认交接   | 【无页面】→ redirect          |
| `complete_order_view` | 完成订单   | 【无页面】→ redirect          |
| `cancel_order_view`   | 取消订单   | 【无页面】→ redirect          |

### 三、search_views.py（搜索 / 标签）
| View 方法                 | 功能    | 对应 HTML 页面                |
| ----------------------- | ----- | ------------------------- |
| `search`                | 关键词搜索 | `search_results.html`     |
| `tag_list`              | 标签列表  | `tag_list.html`           |
| `search_by_tag_view`    | 标签搜索  | `search_results.html`（复用） |
| `search_tag_suggestion` | 标签联想  | 【无页面】→ Ajax(JSON)         |

### notice_views.py（通知 / 公告）
| View 方法                           | 功能   | 对应 HTML 页面                        |
| --------------------------------- | ---- | --------------------------------- |
| `notice_list_view`                | 我的通知 | `notice_list.html`                |
| `unread_notice_view`              | 未读通知 | `unread_notice.html`              |
| `mark_read_view`                  | 标记已读 | 【无页面】→ Ajax                       |
| `announcement_list_view`          | 公告列表 | `announcement_list.html`          |
| `announcement_detail_view`        | 公告详情 | `announcement_detail.html`        |
| `admin_publish_announcement_view` | 发布公告 | `admin_publish_announcement.html` |
| `admin_delete_announcement_view`  | 删除公告 | 【无页面】→ redirect                   |

### 五、complaint_views.py（投诉）
| View 方法                       | 功能        | 对应 HTML 页面                    |
| ----------------------------- | --------- | ----------------------------- |
| `submit_complaint_view`       | 提交投诉      | `submit_complaint.html`       |
| `my_complaints_view`          | 我的投诉      | `my_complaints.html`          |
| `admin_complaint_list_view`   | 投诉列表（管理员） | `admin_complaint_list.html`   |
| `admin_handle_complaint_view` | 处理投诉      | `admin_handle_complaint.html` |

### 六、stats_views.py（统计）
| View 方法               | 功能        | 对应 HTML 页面                  |
| --------------------- | --------- | --------------------------- |
| `stats_overview_view` | 系统统计（管理员） | `stats_overview.html`（目前未建） |
| `stats_user_view`     | 我的统计      | `stats_user.html`（目前未建）     |

### 七、accounts / views.py（用户）
| View 方法                 | 功能   | 对应 HTML 页面                                      |
| ----------------------- | ---- | ----------------------------------------------- |
| `register`              | 注册   | `accounts/register.html`                        |
| `login_view`            | 登录   | `accounts/login.html`                           |
| `logout_view`           | 登出   | 【无页面】→ redirect                                 |
| `profile`               | 个人信息 | `accounts/profile.html`                         |
| `update_profile_view`   | 修改资料 | `accounts/profile.html`（或拆 `edit_profile.html`） |
| `change_password_view`  | 修改密码 | `accounts/change_password.html`（未建）             |
| `admin_user_list_view`  | 用户管理 | `accounts/admin_user_list.html`（未建）             |
| `admin_ban_user_view`   | 封禁用户 | 【无页面】→ Ajax                                     |
| `admin_unban_user_view` | 解封用户 | 【无页面】→ Ajax                                     |

##　最小页面集
login.html
register.html
index.html
posting_list.html
post_detail.html
create_posting.html
create_order.html
order_buyer_list.html
order_seller_list.html
order_detail.html
submit_complaint.html
my_complaints.html
admin_complaint_list.html

## 后续要打的补丁
my_posting_list