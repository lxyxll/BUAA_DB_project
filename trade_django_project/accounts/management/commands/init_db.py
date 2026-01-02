import os
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Execute SQL files (schema + sample data) in sql/ directory to initialize database structure and basic data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="sql",
            help="Directory containing SQL files (default: sql/)",
        )

    def handle(self, *args, **kwargs):
        sql_dir = kwargs["path"]

        # 这里只执行不会包含触发器/存储过程的文件
        files = [
            "schema.sql",
            "sample_data.sql",  # 如果不想自动插入样例数据，可以先注释掉这一行
        ]

        for sql_file in files:
            filepath = os.path.join(sql_dir, sql_file)

            if not os.path.exists(filepath):
                self.stdout.write(self.style.ERROR(f"File not found: {filepath}"))
                continue

            self.stdout.write(self.style.WARNING(f"Executing {sql_file} ..."))

            with open(filepath, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # 用分号切分“简单语句”：建表/插入/更新/删除
            statements = [
                stmt.strip()
                for stmt in sql_content.split(";")
                if stmt.strip()
            ]

            with connection.cursor() as cursor:
                for stmt in statements:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error executing SQL from {sql_file}:\n{stmt}\nError: {e}"
                            )
                        )
                        raise e

        self.stdout.write(self.style.SUCCESS("Schema & sample data initialized successfully!"))
