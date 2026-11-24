import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        title_lbl = ctk.CTkLabel(
            self,
            text="📊 التقارير المالية والأرباح العامة",
            font=("Arial", 22, "bold")
        )
        title_lbl.pack(anchor="e", pady=(0, 12), padx=10)

        # 1) بطاقات الملخص المالي والأرباح
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 12), padx=5)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        sales_card = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#2980b9")
        sales_card.grid(row=0, column=2, padx=8, sticky="nsew")
        ctk.CTkLabel(
            sales_card,
            text="إجمالي المبيعات",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(pady=(10, 4))
        self.lbl_total_sales = ctk.CTkLabel(
            sales_card,
            text="0.00",
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        self.lbl_total_sales.pack(pady=(0, 10))

        purchases_card = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#d35400")
        purchases_card.grid(row=0, column=1, padx=8, sticky="nsew")
        ctk.CTkLabel(
            purchases_card,
            text="إجمالي المشتريات",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(pady=(10, 4))
        self.lbl_total_purchases = ctk.CTkLabel(
            purchases_card,
            text="0.00",
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        self.lbl_total_purchases.pack(pady=(0, 10))

        profit_card = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#27ae60")
        profit_card.grid(row=0, column=0, padx=8, sticky="nsew")
        ctk.CTkLabel(
            profit_card,
            text="صافي الأرباح",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).pack(pady=(10, 4))
        self.lbl_net_profit = ctk.CTkLabel(
            profit_card,
            text="0.00",
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        self.lbl_net_profit.pack(pady=(0, 10))

        # 2) شريط البحث والفلترة وأزرار التقارير
        filter_bar = ctk.CTkFrame(self, corner_radius=10)
        filter_bar.pack(fill="x", pady=(0, 10), padx=5)

        lbl_search = ctk.CTkLabel(
            filter_bar,
            text="🔍 بحث (رقم العملية / التفاصيل):",
            font=("Arial", 13, "bold")
        )
        lbl_search.pack(side="right", padx=(5, 8), pady=8)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="اكتب للبحث في سجل التقارير...",
            justify="right",
            width=260,
            height=34
        )
        self.search_entry.pack(side="right", padx=5, pady=8)
        self.search_entry.bind("<KeyRelease>", self.filter_rows)

        self.type_filter_var = ctk.StringVar(value="الكل")
        self.type_combo = ctk.CTkComboBox(
            filter_bar,
            values=["الكل", "مبيعات", "مشتريات"],
            variable=self.type_filter_var,
            justify="right",
            width=140,
            height=34,
            command=lambda _: self.filter_rows()
        )
        self.type_combo.pack(side="right", padx=8, pady=8)

        btn_preview = ctk.CTkButton(
            filter_bar,
            text="📋 معاينة التقرير",
            fg_color="#2980b9",
            hover_color="#1f618d",
            height=34,
            font=("Arial", 13, "bold"),
            command=self.open_report_preview
        )
        btn_preview.pack(side="left", padx=5, pady=8)

        btn_export = ctk.CTkButton(
            filter_bar,
            text="💾 تصدير CSV",
            fg_color="#27ae60",
            hover_color="#219653",
            height=34,
            font=("Arial", 13, "bold"),
            command=self.export_report_csv
        )
        btn_export.pack(side="left", padx=5, pady=8)

        # 3) جدول سجل حركات المبيعات والمشتريات والأرباح
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        table_title = ctk.CTkLabel(
            table_frame,
            text="سجل حركات الأرباح والمبيعات والمشتريات المفصلة",
            font=("Arial", 15, "bold")
        )
        table_title.pack(anchor="e", padx=15, pady=(10, 4))

        grid_holder = ctk.CTkFrame(table_frame, fg_color="transparent")
        grid_holder.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = (
            "رقم العملية",
            "نوع الحركة",
            "التفاصيل",
            "المبلغ الإجمالي",
            "الربح الصافي",
            "التاريخ والوقت"
        )
        self.tree = ttk.Treeview(grid_holder, columns=columns, show="headings", height=10)

        col_widths = {
            "رقم العملية": 110,
            "نوع الحركة": 110,
            "التفاصيل": 230,
            "المبلغ الإجمالي": 130,
            "الربح الصافي": 130,
            "التاريخ والوقت": 150
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=col_widths.get(col, 130), anchor="center")

        self.tree.pack(fill="both", expand=True, side="right")

        scrollbar = ttk.Scrollbar(grid_holder, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self._load_sample_data()

    def _parse_amount(self, val):
        clean = str(val).replace(",", "").replace("ر.ي", "").strip()
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def _load_sample_data(self):
        """بيانات تجريبية للواجهة فقط قبل ربط قاعدة البيانات"""
        sample_rows = [
            ("101", "مبيعات", "فاتورة زبون نقدي - قرطاسية", "12,500.00", "4,200.00", "2026-11-14 10:30"),
            ("102", "مشتريات", "توريد دفاتر وأقلام - مؤسسة النور", "95,000.00", "0.00", "2026-11-14 09:00"),
            ("103", "مبيعات", "فاتورة عميل - مستلزمات مكتبية", "141,800.00", "55,100.00", "2026-11-15 16:15"),
        ]
        for row_vals in sample_rows:
            self.tree.insert("", "end", values=row_vals)
        self.recalculate_summary()

    def add_report_entry(self, op_id, move_type, details, total_amount, net_profit, timestamp=None):
        """إضافة سجل جديد إلى واجهة التقارير وتحديث البطاقات تلقائياً"""
        ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.tree.insert(
            "",
            "end",
            values=(
                str(op_id),
                str(move_type),
                str(details),
                f"{self._parse_amount(total_amount):,.2f}",
                f"{self._parse_amount(net_profit):,.2f}",
                ts
            )
        )
        self.recalculate_summary()
        self.filter_rows()

    def recalculate_summary(self):
        total_sales = 0.0
        total_purchases = 0.0
        total_profit = 0.0

        for row_id in self.tree.get_children():
            vals = self.tree.item(row_id, "values")
            move_type = str(vals[1]).strip()
            amount = self._parse_amount(vals[3])
            profit = self._parse_amount(vals[4])

            if move_type == "مبيعات":
                total_sales += amount
                total_profit += profit
            elif move_type == "مشتريات":
                total_purchases += amount
                total_profit += profit
            else:
                total_profit += profit

        self.lbl_total_sales.configure(text=f"{total_sales:,.2f}")
        self.lbl_total_purchases.configure(text=f"{total_purchases:,.2f}")
        self.lbl_net_profit.configure(text=f"{total_profit:,.2f}")

    def filter_rows(self, event=None):
        query = self.search_entry.get().strip().lower()
        selected_type = self.type_filter_var.get()

        for row_id in self.tree.get_children():
            vals = self.tree.item(row_id, "values")
            op_match = query in str(vals[0]).lower()
            details_match = query in str(vals[2]).lower()
            text_ok = (not query) or op_match or details_match
            type_ok = (selected_type == "الكل") or (str(vals[1]).strip() == selected_type)

            if text_ok and type_ok:
                self.tree.reattach(row_id, "", "end")
            else:
                self.tree.detach(row_id)

    def build_report_text(self):
        lines = []
        lines.append("=" * 65)
        lines.append(f"التقرير المالي والأرباح - التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 65)
        lines.append(f"إجمالي المبيعات: {self.lbl_total_sales.cget('text')}")
        lines.append(f"إجمالي المشتريات: {self.lbl_total_purchases.cget('text')}")
        lines.append(f"صافي الأرباح: {self.lbl_net_profit.cget('text')}")
        lines.append("-" * 65)

        idx = 0
        for row_id in self.tree.get_children():
            vals = self.tree.item(row_id, "values")
            idx += 1
            lines.append(
                f"{idx}. رقم: {vals[0]} | النوع: {vals[1]} | التفاصيل: {vals[2]} | "
                f"المبلغ: {vals[3]} | الربح: {vals[4]} | الوقت: {vals[5]}"
            )

        lines.append("=" * 65)
        return "\n".join(lines)

    def open_report_preview(self):
        win = ctk.CTkToplevel(self)
        win.title("معاينة التقرير المالي والأرباح")
        win.geometry("800x500")

        lbl = ctk.CTkLabel(win, text="📋 معاينة التقرير المالي والأرباح", font=("Arial", 18, "bold"))
        lbl.pack(anchor="e", padx=15, pady=(12, 6))

        txt = ctk.CTkTextbox(win, font=("Arial", 13), wrap="word")
        txt.pack(fill="both", expand=True, padx=15, pady=8)
        txt.insert("1.0", self.build_report_text())
        txt.configure(state="disabled")

        btn_close = ctk.CTkButton(
            win,
            text="إغلاق",
            fg_color="#7f8c8d",
            hover_color="#62686f",
            command=win.destroy
        )
        btn_close.pack(pady=(0, 12))

    def export_report_csv(self):
        if not self.tree.get_children():
            messagebox.showwarning("تنبيه", "لا توجد بيانات لتصديرها.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"reports_profit_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path:
            return

        try:
            headers = [
                "رقم العملية",
                "نوع الحركة",
                "التفاصيل",
                "المبلغ الإجمالي",
                "الربح الصافي",
                "التاريخ والوقت"
            ]
            with open(file_path, "w", encoding="utf-8-sig") as f:
                f.write(",".join(headers) + "\n")
                for row_id in self.tree.get_children():
                    vals = self.tree.item(row_id, "values")
                    escaped = [f'"{str(v).replace(chr(34), chr(34)*2)}"' for v in vals]
                    f.write(",".join(escaped) + "\n")

            messagebox.showinfo("تم التصدير", "تم تصدير تقرير المبيعات والأرباح بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ في التصدير", f"تعذر تصدير التقرير:\n{e}")