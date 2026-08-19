import os
from database import get_history

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))


def is_admin(user_id):
    return user_id == ADMIN_ID


def admin_stats():
    return "پنل مدیریت آماده است."
