import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


class WarehouseFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # عنوان القسم
        title_lbl = ctk.CTkLabel(
            self,
            text="🏭 إدارة المخازن وجرد الكميات",
            font=("Arial", 22, "bold")
        )
        title_lbl.pack(anchor="e", pady=(0, 12), padx=10)

        # شريط علوي: بطاقات ملخص سريعة + بحث + إخراج تقرير
        top_bar = ctk.CTkFrame(self, corner_radius=10)
        top_bar.pack(fill="x", pady=(0, 10), padx=5)

        # بطاقات ملخص المخزون (واجهة عرض فقط)
        stats_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.total_items_lbl = ctk.CTkLabel(
            stats_frame,
            text="عدد الأصناف: 0",
            font=("Arial", 13, "bold"),
            text_color="#3498db"
        )
        self.total_items_lbl.pack(side="right", padx=15)

        self.total_qty_lbl = ctk.CTkLabel(
            stats_frame,
            text="إجمالي الكميات: 0",
            font=("Arial", 13, "bold"),
            text_color="#2ecc71"
        )
        self.total_qty_lbl.pack(side="right", padx=15)

        self.low_stock_lbl = ctk.CTkLabel(
            stats_frame,
            text="أصناف منخفضة الكمية (<= 5): 0",
            font=("Arial", 13, "bold"),
            text_color="#e67e22"
        )
        self.low_stock_lbl.pack(side="right", padx=15)

        # صف البحث والتقارير
        controls_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=(5, 10))

        lbl_search = ctk.CTkLabel(
            controls_frame,
            text="🔍 بحث (اسم المنتج / النوع / رقم الفاتورة):",
            font=("Arial", 13, "bold")
        )
        lbl_search.pack(side="right", padx=(5, 8))

        self.search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="اكتب اسم المنتج للبحث...",
            justify="right",
            width=280,
            height=35
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_stock)

        # فلتر سريع حسب الكمية
        self.filter_var = ctk.StringVar(value="الكل")
        self.filter_combo = ctk.CTkComboBox(
            controls_frame,
            values=["الكل", "متوفر", "منخفض (<= 5)", "منتهي (0)"],
            variable=self.filter_var,
            justify="right",
            width=150,
            height=35,
            command=lambda _: self.filter_stock()
        )
        self.filter_combo.pack(side="right", padx=8)

        # أزرار إخراج التقارير
        btn_report = ctk.CTkButton(
            controls_frame,
            text="📊 تقرير الكميات والتفاصيل",
            fg_color="#2980b9",
            hover_color="#1f618d",
            height=35,
            font=("Arial", 13, "bold"),
            command=self.open_stock_report_window
        )
        btn_report.pack(side="left", padx=5)

        btn_export = ctk.CTkButton(
            controls_frame,
            text="💾 تصدير تقرير CSV",
            fg_color="#27ae60",
            hover_color="#219653",
            height=35,
            font=("Arial", 13, "bold"),
            command=self.export_stock_csv
        )
        btn_export.pack(side="left", padx=5)

        # جدول عرض المخزون (التركيز على الاسم والكمية وباقي التفاصيل)
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = (
            "م",
            "اسم المنتج",
            "الكمية",
            "النوع",
            "آخر سعر شراء",
            "آخر رقم فاتورة",
            "آخر تاريخ دخول",
            "الحالة"
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        col_widths = {
            "م": 60,
            "اسم المنتج": 180,
            "الكمية": 100,
            "النوع": 140,
            "آخر سعر شراء": 120,
            "آخر رقم فاتورة": 130,
            "آخر تاريخ دخول": 130,
            "الحالة": 110
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=col_widths.get(col, 120), anchor="center")

        self.tree.pack(fill="both", expand=True, side="right", padx=10, pady=10)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _parse_int(self, text):
        return int(str(text).replace(",", "").strip())

    def _parse_float(self, text):
        return float(str(text).replace(",", "").strip())

    def _get_status(self, qty):
        if qty <= 0:
            return "منتهي"
        elif qty <= 5:
            return "منخفض"
        return "متوفر"

    def receive_purchase_item(self, name, prod_type, buy_price, qty, invoice_no, entry_date):
        """
        واجهة استقبال منتج قادم من المشتريات:
        إذا كان المنتج موجوداً بنفس الاسم يتم جمع الكمية وتحديث آخر سعر شراء/فاتورة/تاريخ،
        وإذا لم يكن موجوداً يتم إضافته كصف جديد في المخزون.
        """
        buy_val = self._parse_float(buy_price)
        qty_val = self._parse_int(qty)
        clean_name = str(name).strip()

        existing_row = None
        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            if vals[1].strip().lower() == clean_name.lower():
                existing_row = row
                break

        if existing_row:
            vals = self.tree.item(existing_row, "values")
            new_qty = self._parse_int(vals[2]) + qty_val
            status = self._get_status(new_qty)
            self.tree.item(
                existing_row,
                values=(
                    vals[0],
                    clean_name,
                    f"{new_qty:,}",
                    prod_type,
                    f"{buy_val:,.2f}",
                    invoice_no,
                    entry_date,
                    status
                )
            )
        else:
            row_num = str(len(self.tree.get_children()) + 1)
            status = self._get_status(qty_val)
            self.tree.insert(
                "",
                "end",
                values=(
                    row_num,
                    clean_name,
                    f"{qty_val:,}",
                    prod_type,
                    f"{buy_val:,.2f}",
                    invoice_no,
                    entry_date,
                    status
                )
            )

        self.refresh_summary()
        self.filter_stock()

    def refresh_summary(self):
        total_items = 0
        total_qty = 0
        low_count = 0

        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            qty = self._parse_int(vals[2])
            total_items += 1
            total_qty += qty
            if qty <= 5:
                low_count += 1

        self.total_items_lbl.configure(text=f"عدد الأصناف: {total_items:,}")
        self.total_qty_lbl.configure(text=f"إجمالي الكميات: {total_qty:,}")
        self.low_stock_lbl.configure(text=f"أصناف منخفضة الكمية (<= 5): {low_count:,}")

    def filter_stock(self, event=None):
        query = self.search_entry.get().strip().lower()
        status_filter = self.filter_var.get()

        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            name_match = query in vals[1].lower()
            type_match = query in vals[3].lower()
            inv_match = query in vals[5].lower()
            text_ok = (not query) or name_match or type_match or inv_match

            qty = self._parse_int(vals[2])
            if status_filter == "الكل":
                status_ok = True
            elif status_filter == "متوفر":
                status_ok = qty > 5
            elif status_filter == "منخفض (<= 5)":
                status_ok = 0 < qty <= 5
            elif status_filter == "منتهي (0)":
                status_ok = qty == 0
            else:
                status_ok = True

            if text_ok and status_ok:
                self.tree.reattach(row, "", "end")
            else:
                self.tree.detach(row)

    def build_report_text(self):
        """تجهيز نص تقرير الكميات وباقي التفاصيل للعرض أو النسخ"""
        lines = []
        lines.append("=" * 65)
        lines.append(f"تقرير جرد المخزون والكميات - التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 65)

        total_qty = 0
        total_cost_value = 0.0
        count = 0

        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            count += 1
            name = vals[1]
            qty = self._parse_int(vals[2])
            prod_type = vals[3]
            buy_price = self._parse_float(vals[4])
            inv_no = vals[5]
            entry_date = vals[6]
            status = vals[7]

            line_cost = qty * buy_price
            total_qty += qty
            total_cost_value += line_cost

            lines.append(
                f"{count}. المنتج: {name} | الكمية: {qty:,} | النوع: {prod_type} | "
                f"سعر الشراء: {buy_price:,.2f} | إجمالي التكلفة: {line_cost:,.2f} | "
                f"آخر فاتورة: {inv_no} | آخر دخول: {entry_date} | الحالة: {status}"
            )

        lines.append("-" * 65)
        lines.append(f"إجمالي عدد الأصناف: {count:,}")
        lines.append(f"إجمالي الكميات في المخزون: {total_qty:,}")
        lines.append(f"إجمالي قيمة المخزون بسعر الشراء: {total_cost_value:,.2f}")
        lines.append("=" * 65)
        return "\n".join(lines)

    def open_stock_report_window(self):
        """فتح نافذة معاينة تقرير الكميات والتفاصيل"""
        report_win = ctk.CTkToplevel(self)
        report_win.title("تقرير جرد المخزون والكميات")
        report_win.geometry("820x520")

        lbl = ctk.CTkLabel(
            report_win,
            text="📋 تقرير الكميات وتفاصيل المخزون",
            font=("Arial", 18, "bold")
        )
        lbl.pack(anchor="e", padx=15, pady=(12, 6))

        textbox = ctk.CTkTextbox(report_win, font=("Arial", 13), wrap="word")
        textbox.pack(fill="both", expand=True, padx=15, pady=8)
        textbox.insert("1.0", self.build_report_text())
        textbox.configure(state="disabled")

        btn_close = ctk.CTkButton(
            report_win,
            text="إغلاق",
            fg_color="#7f8c8d",
            hover_color="#62686f",
            command=report_win.destroy
        )
        btn_close.pack(pady=(0, 12))

        
    def deduct_sale_item(self, name, qty):
        """
        خصم كمية مباعة من المخزون في الواجهة:
        - يتحقق من وجود الصنف في المخزون.
        - يتحقق أن الكمية المطلوبة لا تتجاوز الرصيد المتوفر.
        - ينقص الكمية ويحدث حالة الصنف وبطاقات الملخص والفلترة.
        """
        clean_name = str(name).strip()
        qty_val = self._parse_int(qty)

        if qty_val <= 0:
            return False, "الكمية المباعة يجب أن تكون أكبر من صفر."

        target_row = None
        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            if vals[1].strip().lower() == clean_name.lower():
                target_row = row
                break

        if not target_row:
            return False, f"الصنف ({clean_name}) غير موجود في المخزون."

        vals = self.tree.item(target_row, "values")
        current_qty = self._parse_int(vals[2])

        if qty_val > current_qty:
            return (
                False,
                f"الكمية المتوفرة من ({vals[1]}) هي ({current_qty:,}) فقط، ولا تكفي لبيع ({qty_val:,})."
            )

        new_qty = current_qty - qty_val
        new_status = self._get_status(new_qty)

        self.tree.item(
            target_row,
            values=(
                vals[0],
                vals[1],
                f"{new_qty:,}",
                vals[3],
                vals[4],
                vals[5],
                vals[6],
                new_status
            )
        )

        self.refresh_summary()
        self.filter_stock()
        return True, f"تم خصم ({qty_val:,}) من ({vals[1]})؛ المتبقي: ({new_qty:,})."   

    
    def export_stock_csv(self):
        """تصدير تقرير الكميات وتفاصيل المخزون إلى ملف CSV"""
        if not self.tree.get_children():
            messagebox.showwarning("تنبيه", "لا توجد بيانات في المخزون لتصديرها.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"warehouse_report_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path:
            return

        try:
            headers = [
                "م",
                "اسم المنتج",
                "الكمية",
                "النوع",
                "آخر سعر شراء",
                "آخر رقم فاتورة",
                "آخر تاريخ دخول",
                "الحالة"
            ]
            with open(file_path, "w", encoding="utf-8-sig") as f:
                f.write(",".join(headers) + "\n")
                for row in self.tree.get_children():
                    vals = self.tree.item(row, "values")
                    escaped = [f'"{str(v).replace(chr(34), chr(34)*2)}"' for v in vals]
                    f.write(",".join(escaped) + "\n")

            messagebox.showinfo("تم التصدير", "تم تصدير تقرير المخزون بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ في التصدير", f"تعذر تصدير التقرير:\n{e}")