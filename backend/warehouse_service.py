from datetime import datetime
from mysql.connector import Error, IntegrityError
from database.db_connection import get_connection, close_connection


def compute_stock_status(quantity):
    """تحديد حالة الصنف بناءً على الكمية المتوفرة"""
    qty = int(quantity or 0)
    if qty <= 0:
        return "منتهي"
    if qty <= 5:
        return "منخفض"
    return "متوفر"


def get_all_warehouse_items():
    """جلب جميع الأصناف من جدول warehouse"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                id,
                product_name,
                quantity,
                product_type,
                buy_price,
                invoice_no,
                entry_date,
                status
            FROM warehouse
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        return True, rows, ""
    except (Error, ConnectionError) as err:
        return False, [], f"خطأ أثناء جلب بيانات المخزون:\n{err}"
    finally:
        close_connection(conn, cursor)


def add_or_update_warehouse_item(
    product_name,
    quantity,
    product_type,
    buy_price,
    invoice_no="-",
    entry_date=None
):
    """إضافة صنف جديد أو زيادة كميته إذا كان موجوداً مسبقاً في المخزون"""
    clean_name = (product_name or "").strip()
    clean_type = (product_type or "").strip() or "أخرى"
    clean_inv = (invoice_no or "").strip() or "-"
    clean_date = (entry_date or "").strip() or datetime.now().strftime("%Y-%m-%d")

    if not clean_name:
        return False, "اسم المنتج مطلوب."

    try:
        qty = int(quantity)
        price = float(buy_price)
        if qty <= 0 or price < 0:
            return False, "الكمية يجب أن تكون أكبر من صفر وسعر الشراء غير سالب."
    except (ValueError, TypeError):
        return False, "الكمية أو سعر الشراء غير صالح."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, quantity FROM warehouse WHERE LOWER(product_name) = LOWER(%s)",
            (clean_name,)
        )
        existing = cursor.fetchone()

        if existing:
            new_qty = int(existing["quantity"]) + qty
            new_status = compute_stock_status(new_qty)
            cursor.execute("""
                UPDATE warehouse
                SET
                    quantity = %s,
                    product_type = %s,
                    buy_price = %s,
                    invoice_no = %s,
                    entry_date = %s,
                    status = %s
                WHERE id = %s
            """, (new_qty, clean_type, price, clean_inv, clean_date, new_status, existing["id"]))
        else:
            status = compute_stock_status(qty)
            cursor.execute("""
                INSERT INTO warehouse (
                    product_name,
                    quantity,
                    product_type,
                    buy_price,
                    invoice_no,
                    entry_date,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (clean_name, qty, clean_type, price, clean_inv, clean_date, status))

        conn.commit()
        return True, "تم تحديث المخزون بنجاح."
    except IntegrityError:
        return False, f"الصنف ({clean_name}) موجود مسبقاً."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء تحديث المخزون:\n{err}"
    finally:
        close_connection(conn, cursor)


def update_warehouse_item(
    item_id,
    product_name,
    quantity,
    product_type,
    buy_price,
    invoice_no="-",
    entry_date=None
):
    """تعديل بيانات صنف محدد في جدول warehouse حسب id"""
    clean_name = (product_name or "").strip()
    clean_type = (product_type or "").strip() or "أخرى"
    clean_inv = (invoice_no or "").strip() or "-"
    clean_date = (entry_date or "").strip() or datetime.now().strftime("%Y-%m-%d")

    if not item_id:
        return False, "لم يتم تحديد الصنف المراد تعديله."
    if not clean_name:
        return False, "اسم المنتج مطلوب."

    try:
        qty = int(quantity)
        price = float(buy_price)
        if qty < 0 or price < 0:
            return False, "الكمية وسعر الشراء يجب ألا يكونا سالبين."
    except (ValueError, TypeError):
        return False, "الكمية أو سعر الشراء غير صالح."

    status = compute_stock_status(qty)

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE warehouse
            SET
                product_name = %s,
                quantity = %s,
                product_type = %s,
                buy_price = %s,
                invoice_no = %s,
                entry_date = %s,
                status = %s
            WHERE id = %s
        """, (clean_name, qty, clean_type, price, clean_inv, clean_date, status, item_id))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "الصنف المحدد غير موجود."
        return True, "تم تعديل بيانات الصنف بنجاح."
    except IntegrityError:
        return False, f"يوجد صنف آخر مسجل بالاسم ({clean_name})."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء تعديل الصنف:\n{err}"
    finally:
        close_connection(conn, cursor)


def delete_warehouse_item(item_id):
    """حذف صنف من جدول warehouse حسب id"""
    if not item_id:
        return False, "لم يتم تحديد الصنف المراد حذفه."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warehouse WHERE id = %s", (item_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "الصنف المحدد غير موجود."
        return True, "تم حذف الصنف من المخزون بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء حذف الصنف:\n{err}"
    finally:
        close_connection(conn, cursor)


def deduct_stock(product_name, qty):
    """خصم كمية مباعة من المخزون مع التحقق من توفر الكمية"""
    clean_name = (product_name or "").strip()
    if not clean_name:
        return False, "اسم الصنف مطلوب."

    try:
        deduct_qty = int(qty)
        if deduct_qty <= 0:
            return False, "الكمية المراد خصمها يجب أن تكون أكبر من صفر."
    except (ValueError, TypeError):
        return False, "الكمية غير صالحة."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, product_name, quantity FROM warehouse WHERE LOWER(product_name) = LOWER(%s)",
            (clean_name,)
        )
        item = cursor.fetchone()
        if not item:
            return False, f"الصنف ({clean_name}) غير موجود في المخزون."

        current_qty = int(item["quantity"])
        if deduct_qty > current_qty:
            return (
                False,
                f"الكمية المتوفرة من ({item['product_name']}) هي ({current_qty}) فقط، "
                f"والمطلوب خصمه ({deduct_qty})."
            )

        new_qty = current_qty - deduct_qty
        new_status = compute_stock_status(new_qty)

        cursor.execute(
            "UPDATE warehouse SET quantity = %s, status = %s WHERE id = %s",
            (new_qty, new_status, item["id"])
        )
        conn.commit()
        return True, "تم خصم الكمية من المخزون بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء خصم الكمية من المخزون:\n{err}"
    finally:
        close_connection(conn, cursor)