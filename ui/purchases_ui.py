import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime


class PurchasesFrame(ctk.CTkFrame):
    def __init__(self, parent, warehouse_frame=None):
        super().__init__(parent, fg_color="transparent")
        self.warehouse_frame = warehouse_frame

        # قوائم افتراضية للواجهة (فرونت إند فقط)
        self.suppliers = [
            "مورد عام",
            "مؤسسة النور للقرطاسية",
            "شركة القلم والمكتبة",
            "مكتبة الأفق التجارية",
            "مورد آخر"
        ]

        self.product_types = [
            "أقلام",
            "دفاتر وكراسات",
            "أوراق وملفات",
            "أدوات هندسية ومكتبية",
            "ألوان وفنون",
            "مستلزمات مدرسية",
            "أخرى"
        ]

        # عنوان القسم
        title_lbl = ctk.CTkLabel(
            self,
            text="🧾 إدارة المشتريات وفواتير التوريد",
            font=("Arial", 22, "bold")
        )
        title_lbl.pack(anchor="e", pady=(0, 12), padx=10)

        # 1) إطار بيانات الفاتورة (رقم الفاتورة - المورد - تاريخ الفاتورة)
        invoice_frame = ctk.CTkFrame(self, corner_radius=10)
        invoice_frame.pack(fill="x", pady=(0, 10), padx=5)

        lbl_inv = ctk.CTkLabel(invoice_frame, text="رقم الفاتورة:", font=("Arial", 13, "bold"))
        lbl_inv.grid(row=0, column=3, padx=15, pady=(10, 0), sticky="e")
        self.invoice_entry = ctk.CTkEntry(
            invoice_frame,
            placeholder_text="مثال: INV-2026-01",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.invoice_entry.grid(row=1, column=3, padx=15, pady=(0, 12), sticky="ew")

        lbl_supplier = ctk.CTkLabel(invoice_frame, text="المورد:", font=("Arial", 13, "bold"))
        lbl_supplier.grid(row=0, column=2, padx=15, pady=(10, 0), sticky="e")
        self.supplier_combo = ctk.CTkComboBox(
            invoice_frame,
            values=self.suppliers,
            justify="right",
            height=35,
            font=("Arial", 13),
            dropdown_font=("Arial", 13)
        )
        self.supplier_combo.set(self.suppliers[0])
        self.supplier_combo.grid(row=1, column=2, padx=15, pady=(0, 12), sticky="ew")

        lbl_date = ctk.CTkLabel(invoice_frame, text="تاريخ الفاتورة:", font=("Arial", 13, "bold"))
        lbl_date.grid(row=0, column=1, padx=15, pady=(10, 0), sticky="e")
        self.invoice_date_entry = ctk.CTkEntry(
            invoice_frame,
            placeholder_text="YYYY-MM-DD",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.invoice_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.invoice_date_entry.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        # إجمالي الفاتورة المحددة أو الحالية (عرض بصري في الواجهة)
        lbl_total = ctk.CTkLabel(invoice_frame, text="إجمالي الفاتورة:", font=("Arial", 13, "bold"))
        lbl_total.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="e")
        self.invoice_total_lbl = ctk.CTkLabel(
            invoice_frame,
            text="0.00",
            font=("Arial", 15, "bold"),
            text_color="#2ecc71"
        )
        self.invoice_total_lbl.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="e")

        invoice_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 2) إطار إضافة منتجات الفاتورة
        items_frame = ctk.CTkFrame(self, corner_radius=10)
        items_frame.pack(fill="x", pady=(0, 10), padx=5)

        self.buy_price_var = ctk.StringVar()
        self.qty_var = ctk.StringVar()
        self.buy_price_var.trace_add("write", lambda *args: self.format_number_input(self.buy_price_var))
        self.qty_var.trace_add("write", lambda *args: self.format_number_input(self.qty_var))

        lbl_name = ctk.CTkLabel(items_frame, text="اسم المنتج:", font=("Arial", 13, "bold"))
        lbl_name.grid(row=0, column=3, padx=15, pady=(10, 0), sticky="e")
        self.name_entry = ctk.CTkEntry(
            items_frame,
            placeholder_text="مثال: دفتر 100 ورقة",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.name_entry.grid(row=1, column=3, padx=15, pady=(0, 12), sticky="ew")

        lbl_type = ctk.CTkLabel(items_frame, text="نوع المنتج:", font=("Arial", 13, "bold"))
        lbl_type.grid(row=0, column=2, padx=15, pady=(10, 0), sticky="e")
        self.type_combo = ctk.CTkComboBox(
            items_frame,
            values=self.product_types,
            justify="right",
            height=35,
            font=("Arial", 13),
            dropdown_font=("Arial", 13)
        )
        self.type_combo.set(self.product_types[0])
        self.type_combo.grid(row=1, column=2, padx=15, pady=(0, 12), sticky="ew")

        lbl_buy = ctk.CTkLabel(items_frame, text="سعر الشراء:", font=("Arial", 13, "bold"))
        lbl_buy.grid(row=0, column=1, padx=15, pady=(10, 0), sticky="e")
        self.buy_price_entry = ctk.CTkEntry(
            items_frame,
            textvariable=self.buy_price_var,
            placeholder_text="0.00",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.buy_price_entry.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        lbl_qty = ctk.CTkLabel(items_frame, text="الكمية:", font=("Arial", 13, "bold"))
        lbl_qty.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="e")
        self.qty_entry = ctk.CTkEntry(
            items_frame,
            textvariable=self.qty_var,
            placeholder_text="0",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.qty_entry.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        items_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # أزرار التحكم بالسطور والفاتورة
        btn_frame = ctk.CTkFrame(items_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(0, 12))

        btn_add_item = ctk.CTkButton(
            btn_frame,
            text="➕ إضافة منتج للفاتورة",
            fg_color="#27ae60",
            hover_color="#219653",
            height=38,
            font=("Arial", 13, "bold"),
            command=self.add_item_to_invoice
        )
        btn_add_item.pack(side="left", padx=8)

        btn_update_item = ctk.CTkButton(
            btn_frame,
            text="✏️ تعديل السطر المحدد",
            fg_color="#d35400",
            hover_color="#ba4a00",
            height=38,
            font=("Arial", 13, "bold"),
            command=self.update_selected_item
        )
        btn_update_item.pack(side="left", padx=8)

        btn_delete_item = ctk.CTkButton(
            btn_frame,
            text="🗑️ حذف السطر المحدد",
            fg_color="#c0392b",
            hover_color="#962d22",
            height=38,
            font=("Arial", 13, "bold"),
            command=self.delete_selected_item
        )
        btn_delete_item.pack(side="left", padx=8)

        btn_new_inv = ctk.CTkButton(
            btn_frame,
            text="🆕 فاتورة جديدة / تفريغ",
            fg_color="#7f8c8d",
            hover_color="#62686f",
            height=38,
            font=("Arial", 13),
            command=self.reset_invoice_form
        )
        btn_new_inv.pack(side="left", padx=8)

        # 3) شريط البحث والفلترة
        search_frame = ctk.CTkFrame(self, corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 8), padx=5)

        lbl_search = ctk.CTkLabel(
            search_frame,
            text="🔍 بحث (رقم فاتورة / مورد / منتج / نوع):",
            font=("Arial", 13, "bold")
        )
        lbl_search.pack(side="right", padx=10, pady=8)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="اكتب للبحث في سطور المشتريات...",
            justify="right",
            width=350,
            height=34
        )
        self.search_entry.pack(side="right", padx=10, pady=8)
        self.search_entry.bind("<KeyRelease>", self.filter_rows)

        # 4) جدول تفاصيل فواتير المشتريات
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = (
            "م",
            "رقم الفاتورة",
            "المورد",
            "اسم المنتج",
            "النوع",
            "سعر الشراء",
            "الكمية",
            "إجمالي السطر",
            "تاريخ الفاتورة"
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=115, anchor="center")

        self.tree.pack(fill="both", expand=True, side="right", padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def update_suppliers_list(self, new_suppliers):
        """تحديث قائمة الموردين المنسدلة في الواجهة"""
        if new_suppliers:
            self.suppliers = list(new_suppliers)
            current = self.supplier_combo.get()
            self.supplier_combo.configure(values=self.suppliers)
            if current not in self.suppliers:
                self.supplier_combo.set(self.suppliers[0])

    def format_number_input(self, var):
        value = var.get().replace(",", "")
        if value.isdigit():
            var.set(f"{int(value):,}")
        elif value == "":
            pass
        else:
            clean_val = "".join([c for c in value if c.isdigit()])
            if clean_val:
                var.set(f"{int(clean_val):,}")
            else:
                var.set("")

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def parse_float(self, text):
        return float(str(text).replace(",", "").strip())

    def parse_int(self, text):
        return int(str(text).replace(",", "").strip())

    def add_item_to_invoice(self):
        invoice_no = self.invoice_entry.get().strip()
        supplier = self.supplier_combo.get().strip()
        inv_date = self.invoice_date_entry.get().strip()
        name = self.name_entry.get().strip()
        prod_type = self.type_combo.get().strip()
        buy_str = self.buy_price_var.get().replace(",", "").strip()
        qty_str = self.qty_var.get().replace(",", "").strip()

        if not (invoice_no and supplier and inv_date and name and prod_type and buy_str and qty_str):
            messagebox.showwarning("تنبيه", "الرجاء إدخال بيانات الفاتورة والمنتج كاملة!")
            return

        if not self.validate_date(inv_date):
            messagebox.showerror("خطأ في التاريخ", "صيغة التاريخ يجب أن تكون YYYY-MM-DD (مثال: 2026-11-24)")
            return

        try:
            buy = float(buy_str)
            qty = int(qty_str)
            if qty <= 0 or buy < 0:
                messagebox.showwarning("تنبيه", "الكمية يجب أن تكون أكبر من صفر وسعر الشراء غير سالب.")
                return

            line_total = buy * qty
            row_num = str(len(self.tree.get_children()) + 1)

            # نُبقي رقم الفاتورة والمورد والتاريخ لسهولة إضافة منتجات أخرى لنفس الفاتورة
            self.tree.insert(
                "",
                "end",
                values=(
                    row_num,
                    invoice_no,
                    supplier,
                    name,
                    prod_type,
                    f"{buy:,.2f}",
                    f"{qty:,}",
                    f"{line_total:,.2f}",
                    inv_date
                )
            )

            # إرسال المنتج المضاف إلى واجهة المخزون لتحديث الكميات والملخص
            if self.warehouse_frame and hasattr(self.warehouse_frame, "receive_purchase_item"):
                self.warehouse_frame.receive_purchase_item(
                    name=name,
                    prod_type=prod_type,
                    buy_price=buy,
                    qty=qty,
                    invoice_no=invoice_no,
                    entry_date=inv_date
                )

            self.clear_item_fields()
            self.update_invoice_total(invoice_no)
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء التأكد من صحة الأرقام في سعر الشراء والكمية.")

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            vals = self.tree.item(selected[0], "values")
            self.invoice_entry.delete(0, "end")
            self.invoice_entry.insert(0, vals[1])
            self.supplier_combo.set(vals[2])

            self.clear_item_fields()
            self.name_entry.insert(0, vals[3])
            self.type_combo.set(vals[4])
            self.buy_price_var.set(vals[5].replace(".00", ""))
            self.qty_var.set(vals[6])

            self.invoice_date_entry.delete(0, "end")
            self.invoice_date_entry.insert(0, vals[8])

            self.update_invoice_total(vals[1])

    def update_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد السطر المراد تعديله من الجدول أولاً.")
            return

        if not messagebox.askyesno("تأكيد التعديل", "هل أنت متأكد من حفظ التعديلات على هذا السطر؟"):
            return

        invoice_no = self.invoice_entry.get().strip()
        supplier = self.supplier_combo.get().strip()
        inv_date = self.invoice_date_entry.get().strip()
        name = self.name_entry.get().strip()
        prod_type = self.type_combo.get().strip()
        buy_str = self.buy_price_var.get().replace(",", "").strip()
        qty_str = self.qty_var.get().replace(",", "").strip()

        if not (invoice_no and supplier and inv_date and name and prod_type and buy_str and qty_str):
            messagebox.showwarning("تنبيه", "جميع الحقول مطلوبة لتعديل السطر.")
            return

        if not self.validate_date(inv_date):
            messagebox.showerror("خطأ في التاريخ", "صيغة التاريخ يجب أن تكون YYYY-MM-DD")
            return

        try:
            buy = float(buy_str)
            qty = int(qty_str)
            if qty <= 0 or buy < 0:
                messagebox.showwarning("تنبيه", "الكمية يجب أن تكون أكبر من صفر وسعر الشراء غير سالب.")
                return

            line_total = buy * qty
            current_vals = self.tree.item(selected[0], "values")
            self.tree.item(
                selected[0],
                values=(
                    current_vals[0],
                    invoice_no,
                    supplier,
                    name,
                    prod_type,
                    f"{buy:,.2f}",
                    f"{qty:,}",
                    f"{line_total:,.2f}",
                    inv_date
                )
            )
            self.clear_item_fields()
            self.update_invoice_total(invoice_no)
            messagebox.showinfo("نجاح", "تم تحديث السطر بنجاح.")
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء التأكد من صحة المدخلات الرقمية.")

    def delete_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد السطر المراد حذفه من الجدول أولاً.")
            return

        if messagebox.askyesno(
            "تحذير الحذف",
            "هل أنت متأكد من حذف هذا السطر من الفاتورة؟ لا يمكن التراجع عن هذا الإجراء."
        ):
            inv_no = self.tree.item(selected[0], "values")[1]
            self.tree.delete(selected[0])
            self.clear_item_fields()
            self.update_invoice_total(inv_no)
            messagebox.showinfo("تم الحذف", "تم حذف السطر بنجاح.")

    def update_invoice_total(self, invoice_no):
        """حساب إجمالي الفاتورة المحددة في الواجهة"""
        total = 0.0
        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            if vals[1] == invoice_no:
                total += self.parse_float(vals[7])
        self.invoice_total_lbl.configure(text=f"{total:,.2f}")

    def filter_rows(self, event):
        query = self.search_entry.get().strip().lower()
        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            matched = (
                query in vals[1].lower()
                or query in vals[2].lower()
                or query in vals[3].lower()
                or query in vals[4].lower()
            )
            if matched:
                self.tree.reattach(row, "", "end")
            else:
                self.tree.detach(row)

    def clear_item_fields(self):
        self.name_entry.delete(0, "end")
        self.type_combo.set(self.product_types[0])
        self.buy_price_var.set("")
        self.qty_var.set("")

    def reset_invoice_form(self):
        self.invoice_entry.delete(0, "end")
        self.supplier_combo.set(self.suppliers[0])
        self.invoice_date_entry.delete(0, "end")
        self.invoice_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.clear_item_fields()
        self.invoice_total_lbl.configure(text="0.00")