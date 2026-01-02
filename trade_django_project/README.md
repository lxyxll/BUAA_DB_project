# trade 北航跳蚤市场 - Django 版本

本项目是基于 Django 的校园跳蚤市场示例，实现了基本的用户系统、帖子与商品展示、购物车与下单等功能，使用 MySQL 作为数据库，并提供了 Docker 化部署方案。

## 开发环境运行

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 配置数据库（在 MySQL 中创建 `trade_market` 数据库，并在 `tradeDjango/settings.py` 或环境变量中填写正确的连接信息）。

3. 执行数据库迁移：

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. 创建超级用户（可选）：

   ```bash
   python manage.py createsuperuser
   ```

5. 启动开发服务器：

   ```bash
   python manage.py runserver
   ```

在浏览器中访问 http://127.0.0.1:8000/ 即可查看。

## Docker 部署

确保已安装 Docker 和 docker-compose，然后在项目根目录执行：

```bash
docker-compose up -d --build
```

首次启动可能会花费一些时间来拉取镜像和初始化数据库。启动完成后，在浏览器访问服务器 80 端口。

## 注意事项

- 本项目为通用 Django 跳蚤市场骨架，并未完全复刻原 Rails 项目的所有细节逻辑，您可以在此基础上继续扩展。
- 请务必修改 `DJANGO_SECRET_KEY` 等敏感配置，避免在生产环境中使用默认值。
- 若需要迁移原有数据，可根据原数据库结构调整各模型的 `db_table` 和字段配置，然后通过 SQL 或脚本导入数据。
