from datetime import datetime
from mysql.connector import Error
from database.db_connection import get_connection, close_connection


def get_all_purchases():
    """جلب جميع سطور المشتريات من جدول purchases"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                id,
                invoice_no,
                supplier_name,
                product_name,
                product_type,
                buy_price,
                quantity,
                line_total,
                invoice_date
            FROM purchases
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        return True, rows, ""
    except (Error, ConnectionError) as err:
        return False, [], f"خطأ أثناء جلب المشتريات:\n{err}"
    finally:
        close_connection(conn, cursor)


def add_purchase_item(
    invoice_no,
    supplier_name,
    product_name,
    product_type,
    buy_price,
    quantity,
    invoice_date=None
):
    """إضافة سطر جديد إلى جدول purchases"""
    clean_inv = (invoice_no or "").strip()
    clean_sup = (supplier_name or "").strip()
    clean_prod = (product_name or "").strip()
    clean_type = (product_type or "").strip() or "أخرى"
    clean_date = (invoice_date or "").strip() or datetime.now().strftime("%Y-%m-%d")

    if not (clean_inv and clean_sup and clean_prod):
        return False, "رقم الفاتورة، المورد، واسم المنتج مطلوبة."

    try:
        price = float(buy_price)
        qty = int(quantity)
        if qty <= 0 or price < 0:
            return False, "الكمية يجب أن تكون أكبر من صفر وسعر الشراء غير سالب."
    except (ValueError, TypeError):
        return False, "سعر الشراء أو الكمية غير صالح."

    line_total = round(price * qty, 2)

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO purchases (
                invoice_no,
                supplier_name,
                product_name,
                product_type,
                buy_price,
                quantity,
                line_total,
                invoice_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (clean_inv, clean_sup, clean_prod, clean_type, price, qty, line_total, clean_date))
        conn.commit()
        return True, "تمت إضافة سطر المشتريات بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء إضافة سطر المشتريات:\n{err}"
    finally:
        close_connection(conn, cursor)


def update_purchase_item(
    purchase_id,
    invoice_no,
    supplier_name,
    product_name,
    product_type,
    buy_price,
    quantity,
    invoice_date=None
):
    """تعديل سطر موجود في جدول purchases حسب id"""
    clean_inv = (invoice_no or "").strip()
    clean_sup = (supplier_name or "").strip()
    clean_prod = (product_name or "").strip()
    clean_type = (product_type or "").strip() or "أخرى"
    clean_date = (invoice_date or "").strip() or datetime.now().strftime("%Y-%m-%d")

    if not purchase_id:
        return False, "لم يتم تحديد السطر المراد تعديله."
    if not (clean_inv and clean_sup and clean_prod):
        return False, "رقم الفاتورة، المورد، واسم المنتج مطلوبة."

    try:
        price = float(buy_price)
        qty = int(quantity)
        if qty <= 0 or price < 0:
            return False, "الكمية يجب أن تكون أكبر من صفر وسعر الشراء غير سالب."
    except (ValueError, TypeError):
        return False, "سعر الشراء أو الكمية غير صالح."

    line_total = round(price * qty, 2)

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE purchases
            SET
                invoice_no = %s,
                supplier_name = %s,
                product_name = %s,
                product_type = %s,
                buy_price = %s,
                quantity = %s,
                line_total = %s,
                invoice_date = %s
            WHERE id = %s
        """, (clean_inv, clean_sup, clean_prod, clean_type, price, qty, line_total, clean_date, purchase_id))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "السطر المحدد غير موجود."
        return True, "تم تعديل سطر المشتريات بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء تعديل سطر المشتريات:\n{err}"
    finally:
        close_connection(conn, cursor)


def delete_purchase_item(purchase_id):
    """حذف سطر من جدول purchases حسب id"""
    if not purchase_id:
        return False, "لم يتم تحديد السطر المراد حذفه."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM purchases WHERE id = %s", (purchase_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "السطر المحدد غير موجود."
        return True, "تم حذف سطر المشتريات بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء حذف سطر المشتريات:\n{err}"
    finally:
        close_connection(conn, cursor)