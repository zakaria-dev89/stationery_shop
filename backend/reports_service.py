from datetime import datetime
from mysql.connector import Error
from database.db_connection import get_connection, close_connection


def get_all_financial_logs():
    """جلب جميع سجلات التقارير من جدول financial_logs"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                id,
                operation_no,
                move_type,
                details,
                total_amount,
                net_profit,
                logged_at
            FROM financial_logs
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        return True, rows, ""
    except (Error, ConnectionError) as err:
        return False, [], f"خطأ أثناء جلب سجل التقارير:\n{err}"
    finally:
        close_connection(conn, cursor)


def add_financial_log(operation_no, move_type, details, total_amount, net_profit=0.0, logged_at=None):
    """إضافة سجل حركة مالية أو ربح إلى جدول financial_logs"""
    clean_op = str(operation_no or "").strip()
    clean_type = str(move_type or "").strip()
    clean_details = str(details or "").strip()
    clean_time = str(logged_at or "").strip() or datetime.now().strftime("%Y-%m-%d %H:%M")

    if not (clean_op and clean_type and clean_details):
        return False, "رقم العملية، نوع الحركة، والتفاصيل مطلوبة."

    try:
        amount = float(total_amount)
        profit = float(net_profit)
    except (ValueError, TypeError):
        return False, "المبلغ الإجمالي أو الربح الصافي غير صالح."

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financial_logs (
                operation_no,
                move_type,
                details,
                total_amount,
                net_profit,
                logged_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (clean_op, clean_type, clean_details, round(amount, 2), round(profit, 2), clean_time))
        conn.commit()
        return True, "تم تسجيل الحركة في التقارير بنجاح."
    except (Error, ConnectionError) as err:
        return False, f"خطأ أثناء حفظ الحركة في التقارير:\n{err}"
    finally:
        close_connection(conn, cursor)


def compute_reports_summary(logs):
    """حساب إجمالي المبيعات، إجمالي المشتريات، وصافي الأرباح"""
    total_sales = 0.0
    total_purchases = 0.0
    net_profit = 0.0

    for row in logs or []:
        move_type = str(row.get("move_type", "")).strip()
        amount = float(row.get("total_amount", 0.0) or 0.0)
        profit = float(row.get("net_profit", 0.0) or 0.0)

        if move_type == "مبيعات":
            total_sales += amount
            net_profit += profit
        elif move_type == "مشتريات":
            total_purchases += amount
            net_profit += profit
        else:
            net_profit += profit

    return {
        "total_sales": round(total_sales, 2),
        "total_purchases": round(total_purchases, 2),
        "net_profit": round(net_profit, 2),
    }