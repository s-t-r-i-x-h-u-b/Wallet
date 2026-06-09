[app]

# Название и идентификатор приложения
title = Wallet
package.name = wallet
package.domain = org.wallet

# Исходники
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
source.exclude_dirs = tests, .git, .pytest_cache, __pycache__, bin, .buildozer
source.exclude_patterns = *.db, *.db.enc, wallet.salt

version = 0.1.0

# Зависимости рантайма.
# ВНИМАНИЕ: matplotlib намеренно не включён в первую сборку — он тяжёлый и
# капризный для python-for-android. Приложение работает без него (диаграммы
# в этом случае недоступны). Добавим позже, когда базовая сборка заработает.
requirements = python3,kivy==2.3.1,kivymd==1.2.0,pillow,plyer,cryptography

orientation = portrait
fullscreen = 0

# Разрешения: локальные уведомления о платежах (Android 13+)
android.permissions = POST_NOTIFICATIONS

# Версии Android API
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = 1

# Автопринятие лицензий Android SDK (нужно для неинтерактивной сборки в Docker)
android.accept_sdk_license = True

[buildozer]

log_level = 2
# В контейнере Buildozer работает от root; отключаем интерактивный вопрос,
# иначе неинтерактивный запуск падает с EOFError.
warn_on_root = 0
