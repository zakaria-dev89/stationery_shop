import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Zakri@123",
    "database": "stationery_shop_db",
    "charset": "utf8mb4",
    "use_unicode": True,
}


def get_connection():
    """إنشاء وإرجاع اتصال بقاعدة بيانات stationery_shop_db في MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
        return None
    except Error as err:
        raise ConnectionError(f"تعذر الاتصال بقاعدة البيانات MySQL: {err}")


def close_connection(conn, cursor=None):
    """إغلاق المؤشر والاتصال بشكل آمن"""
    if cursor is not None:
        try:
            cursor.close()
        except Error:
            pass
    if conn is not None:
        try:
            if conn.is_connected():
                conn.close()
        except Error:
            pass