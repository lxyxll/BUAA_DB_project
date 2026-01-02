from pathlib import Path
import sys

# =========================================================
# 项目根目录配置（保证 common / accounts / market 可导入）
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# =========================================================
# 基础配置
# =========================================================

SECRET_KEY = "django-insecure-trade-dev-secret-key-change-me"
DEBUG = True
ALLOWED_HOSTS = ["*"]

ADMIN_REGISTER_CODE = "your-strong-admin-code"

# =========================================================
# 应用注册
# ⚠️ 不使用 Django 内置 auth / admin
# =========================================================

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "market",
]

# =========================================================
# 中间件
# ⚠️ 移除 AuthenticationMiddleware（不用 Django 用户系统）
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================================================
# URL / WSGI
# =========================================================

ROOT_URLCONF = "tradeDjango.urls"
WSGI_APPLICATION = "tradeDjango.wsgi.application"

# =========================================================
# 模板配置
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "trade_django_project" / "templates",
        ],  # 使用 app 内 templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR  / "trade_django_project" / 'static',   # 你的 static 目录
]

# =========================================================
# 数据库配置（保持你原来的 MySQL / 云数据库）
# =========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "h_db23371251",
        "USER": "u23371251",
        "PASSWORD": "Aa233317",
        "HOST": "124.70.86.207",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "ssl": {
                "ca": BASE_DIR / "Certificate Download" / "ca-bundle.pem",
            },
        },
    }
}

# =========================================================
# 国际化
# =========================================================

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# =========================================================
# 静态 / 媒体文件
# =========================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =========================================================
# 其他
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
