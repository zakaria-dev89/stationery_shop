from datetime import datetime
from mysql.connector import Error
from database.db_connection import get_connection, close_connection
from backend.warehouse_service import compute_stock_status


def get_all_sales():
    """جلب جميع سطور المبيعات من جدول sales"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                id,
                invoice_no,
                client_name,
                item_name,
                quantity,
                sell_price,
                subtotal,
                sale_date
            FROM sales
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        return True, rows, ""
    except (Error, ConnectionError) as err:
        return False, [], f"خطأ أثناء جلب المبيعات:\n{err}"
    finally:
        close_connection(conn, cursor)


def checkout_sale_invoice(invoice_no, client_name, sale_date, items):
    """
    إتمام فاتورة بيع:
    1. التحقق من توفر الكميات المطلوبة في جدول warehouse
    2. خصم الكميات وتحديث حالة المخزون
    3. إدراج سطور الفاتورة في جدول sales
    """
    clean_inv = (invoice_no or "").strip() or f"SAL-{datetime.now().strftime('%H%M%S')}"
    clean_client = (client_name or "").strip() or "زبون نقدي"
    clean_date = (sale_date or "").strip() or datetime.now().strftime("%Y-%m-%d")

    if not items:
        return False, "لا توجد أصناف في الفاتورة لإتمام البيع.", 0.0

    # تجميع الكميات المطلوبة لكل صنف (في حال تكرار نفس الصنف في الفاتورة)
    requested_qty = {}
    normalized_items = []

    for row in items:
        name = (row.get("item_name") or "").strip()
        if not name:
            return False, "يوجد سطر بدون اسم صنف.", 0.0
        try:
            qty = int(row.get("quantity", 0))
            price = float(row.get("sell_price", 0))
        except (ValueError, TypeError):
            return False, f"الكمية أو سعر البيع غير صالح للصنف ({name}).", 0.0

        if qty <= 0 or price < 0:
            return False, f"الكمية يجب أن تكون أكبر من صفر والسعر غير سالب للصنف ({name}).", 0.0

        subtotal = round(qty * price, 2)
        normalized_items.append({
            "item_name": name,
            "quantity": qty,
            "sell_price": price,
            "subtotal": subtotal
        })
        key = name.lower()
        requested_qty[key] = requested_qty.get(key, 0) + qty

    grand_total = round(sum(x["subtotal"] for x in normalized_items), 2)

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1) فحص المخزون لجميع الأصناف المطلوبة قبل الخصم
        warehouse_map = {}
        for key, req_q in requested_qty.items():
            cursor.execute(
                "SELECT id, product_name, quantity FROM warehouse WHERE LOWER(product_name) = %s",
                (key,)
            )
            w_row = cursor.fetchone()
            if not w_row:
                return False, f"الصنف ({key}) غير موجود في المخزون.", 0.0

            avail_q = int(w_row["quantity"])
            if req_q > avail_q:
                return (
                    False,
                    f"الكمية المتوفرة من ({w_row['product_name']}) هي ({avail_q}) فقط، "
                    f"والمطلوب ({req_q}).",
                    0.0
                )
            warehouse_map[key] = {
                "id": w_row["id"],
                "current_qty": avail_q
            }

        # 2) خصم الكميات وتحديث حالة المخزون
        for key, req_q in requested_qty.items():
            new_qty = warehouse_map[key]["current_qty"] - req_q
            new_status = compute_stock_status(new_qty)
            cursor.execute(
                "UPDATE warehouse SET quantity = %s, status = %s WHERE id = %s",
                (new_qty, new_status, warehouse_map[key]["id"])
            )

        # 3) إدراج سطور الفاتورة في جدول sales
        for entry in normalized_items:
            cursor.execute("""
                INSERT INTO sales (
                    invoice_no,
                    client_name,
                    item_name,
                    quantity,
                    sell_price,
                    subtotal,
                    sale_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                clean_inv,
                clean_client,
                entry["item_name"],
                entry["quantity"],
                entry["sell_price"],
                entry["subtotal"],
                clean_date
            ))

        conn.commit()
        return True, f"تم إتمام فاتورة البيع رقم ({clean_inv}) بنجاح.", grand_total
    except (Error, ConnectionError) as err:
        if conn and conn.is_connected():
            conn.rollback()
        return False, f"خطأ أثناء حفظ فاتورة المبيعات:\n{err}", 0.0
    finally:
        close_connection(conn, cursor)