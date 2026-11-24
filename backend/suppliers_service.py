from mysql.connector import Error, IntegrityError
from database.db_connection import get_connection, close_connection


def get_all_suppliers():
    """جلب جميع الموردين من جدول suppliers"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, phone, address FROM suppliers ORDER BY name ASC")
        rows = cursor.fetchall()
        return True, rows, ""
    except (Error, ConnectionError) as err:
        return False, [], f"خطأ أثناء جلب الموردين:\n{err}"
    finally:
        close_connection(conn, cursor)


def add_supplier(name, phone="", address=""):
    """إضافة مورد جديد إلى جدول suppliers"""
    clean_name = (name or "").strip()
    clean_phone = (phone or "").strip() or "-"
    clean_address = (address or "").strip() or "-"

    if not clean_name:
        return False, "اسم المورد مطلوب."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO suppliers (name, phone, address) VALUES (%s, %s, %s)",
            (clean_name, clean_phone, clean_address)
        )
        conn.commit()
        return True, "تمت إضافة المورد بنجاح."
    except IntegrityError:
        return False, f"المورد ({clean_name}) مسجل مسبقاً."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء إضافة المورد:\n{err}"
    finally:
        close_connection(conn, cursor)


def update_supplier(supplier_id, name, phone="", address=""):
    """تعديل بيانات مورد موجود حسب id"""
    clean_name = (name or "").strip()
    clean_phone = (phone or "").strip() or "-"
    clean_address = (address or "").strip() or "-"

    if not supplier_id:
        return False, "لم يتم تحديد المورد المراد تعديله."
    if not clean_name:
        return False, "اسم المورد مطلوب."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE suppliers SET name = %s, phone = %s, address = %s WHERE id = %s",
            (clean_name, clean_phone, clean_address, supplier_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "المورد المحدد غير موجود."
        return True, "تم تحديث بيانات المورد بنجاح."
    except IntegrityError:
        return False, f"يوجد مورد آخر مسجل بالاسم ({clean_name})."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء تعديل المورد:\n{err}"
    finally:
        close_connection(conn, cursor)


def delete_supplier(supplier_id):
    """حذف مورد من جدول suppliers حسب id"""
    if not supplier_id:
        return False, "لم يتم تحديد المورد المراد حذفه."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "المورد المحدد غير موجود."
        return True, "تم حذف المورد بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء حذف المورد:\n{err}"
    finally:
        close_connection(conn, cursor)