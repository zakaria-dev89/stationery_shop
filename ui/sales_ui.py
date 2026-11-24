import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime


class SalesFrame(ctk.CTkFrame):
    def __init__(self, parent, warehouse_frame=None):
        super().__init__(parent, fg_color="transparent")
        self.warehouse_frame = warehouse_frame

        # قائمة أصناف قرطاسية افتراضية للواجهة فقط
        self.default_items = [
            "قلم جاف أزرق",
            "قلم رصاص HB",
            "دفتر مسطرة 100 ورقة",
            "دفتر مربعات 200 ورقة",
            "مسطرة هندسية 30 سم",
            "ممحاة ومبراة",
            "علبة ألوان خشبية",
            "ملف حفظ مستندات A4"
        ]

        title_lbl = ctk.CTkLabel(
            self,
            text="💰 نقطة البيع وفواتير القرطاسيات",
            font=("Arial", 22, "bold")
        )
        title_lbl.pack(anchor="e", pady=(0, 12), padx=10)

        # 1) إطار بيانات الفاتورة والعميل
        invoice_frame = ctk.CTkFrame(self, corner_radius=10)
        invoice_frame.pack(fill="x", pady=(0, 10), padx=5)

        lbl_inv_no = ctk.CTkLabel(invoice_frame, text="رقم الفاتورة:", font=("Arial", 13, "bold"))
        lbl_inv_no.grid(row=0, column=2, padx=12, pady=(10, 0), sticky="e")
        self.invoice_no_entry = ctk.CTkEntry(
            invoice_frame,
            placeholder_text="مثال: SAL-1001",
            justify="right",
            height=35,
            font=("Arial", 13)
        )
        self.invoice_no_entry.insert(0, f"SAL-{datetime.now().strftime('%H%M%S')}")
        self.invoice_no_entry.grid(row=1, column=2, padx=12, pady=(0, 10), sticky="ew")

        lbl_client = ctk.CTkLabel(invoice_frame, text="اسم الزبون / العميل:", font=("Arial", 13, "bold"))
        lbl_client.grid(row=0, column=1, padx=12, pady=(10, 0), sticky="e")
        self.client_entry = ctk.CTkEntry(
            invoice_frame,
            placeholder_text="زبون نقدي",
            justify="right",
            height=35,
            font=("Arial", 13)
        )
        self.client_entry.insert(0, "زبون نقدي")
        self.client_entry.grid(row=1, column=1, padx=12, pady=(0, 10), sticky="ew")

        lbl_date = ctk.CTkLabel(invoice_frame, text="تاريخ الفاتورة:", font=("Arial", 13, "bold"))
        lbl_date.grid(row=0, column=0, padx=12, pady=(10, 0), sticky="e")
        self.date_entry = ctk.CTkEntry(
            invoice_frame,
            placeholder_text="YYYY-MM-DD",
            justify="right",
            height=35,
            font=("Arial", 13)
        )
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

        invoice_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # 2) إطار إضافة الأصناف إلى فاتورة البيع
        items_input_frame = ctk.CTkFrame(self, corner_radius=10)
        items_input_frame.pack(fill="x", pady=(0, 10), padx=5)

        self.qty_var = ctk.StringVar()
        self.sell_price_var = ctk.StringVar()

        self.qty_var.trace_add("write", lambda *args: self.format_number_input(self.qty_var))
        self.sell_price_var.trace_add("write", lambda *args: self.format_number_input(self.sell_price_var))

        lbl_item = ctk.CTkLabel(items_input_frame, text="الصنف المباع:", font=("Arial", 13, "bold"))
        lbl_item.grid(row=0, column=2, padx=12, pady=(10, 0), sticky="e")
        self.item_combo = ctk.CTkComboBox(
            items_input_frame,
            values=self.default_items,
            justify="right",
            height=35,
            font=("Arial", 13),
            dropdown_font=("Arial", 13)
        )
        self.item_combo.set(self.default_items[0])
        self.item_combo.grid(row=1, column=2, padx=12, pady=(0, 10), sticky="ew")

        lbl_qty = ctk.CTkLabel(items_input_frame, text="الكمية:", font=("Arial", 13, "bold"))
        lbl_qty.grid(row=0, column=1, padx=12, pady=(10, 0), sticky="e")
        self.item_qty_entry = ctk.CTkEntry(
            items_input_frame,
            textvariable=self.qty_var,
            placeholder_text="0",
            justify="right",
            height=35,
            font=("Arial", 13)
        )
        self.item_qty_entry.grid(row=1, column=1, padx=12, pady=(0, 10), sticky="ew")

        lbl_sell = ctk.CTkLabel(items_input_frame, text="سعر البيع:", font=("Arial", 13, "bold"))
        lbl_sell.grid(row=0, column=0, padx=12, pady=(10, 0), sticky="e")
        self.sell_price_entry = ctk.CTkEntry(
            items_input_frame,
            textvariable=self.sell_price_var,
            placeholder_text="0.00",
            justify="right",
            height=35,
            font=("Arial", 13)
        )
        self.sell_price_entry.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

        items_input_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # أزرار التحكم بأصناف الفاتورة
        btn_bar = ctk.CTkFrame(items_input_frame, fg_color="transparent")
        btn_bar.grid(row=2, column=0, columnspan=3, pady=(0, 12))

        btn_add_item = ctk.CTkButton(
            btn_bar,
            text="➕ إضافة للفاتورة",
            fg_color="#e67e22",
            hover_color="#d35400",
            height=36,
            font=("Arial", 13, "bold"),
            command=self.add_sale_item_to_table
        )
        btn_add_item.pack(side="left", padx=8)

        btn_remove_item = ctk.CTkButton(
            btn_bar,
            text="🗑️ حذف السطر المحدد",
            fg_color="#c0392b",
            hover_color="#962d22",
            height=36,
            font=("Arial", 13, "bold"),
            command=self.remove_selected_item
        )
        btn_remove_item.pack(side="left", padx=8)

        btn_sync_items = ctk.CTkButton(
            btn_bar,
            text="🔄 تحديث أصناف المخزون",
            fg_color="#2980b9",
            hover_color="#1f618d",
            height=36,
            font=("Arial", 13),
            command=self.refresh_items_from_warehouse
        )
        btn_sync_items.pack(side="left", padx=8)

        btn_clear_item = ctk.CTkButton(
            btn_bar,
            text="🧹 تفريغ حقول الصنف",
            fg_color="#7f8c8d",
            hover_color="#62686f",
            height=36,
            font=("Arial", 13),
            command=self.clear_item_fields
        )
        btn_clear_item.pack(side="left", padx=8)

        # 3) جدول سطور فاتورة البيع
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("اسم الصنف", "الكمية", "سعر البيع", "الإجمالي الجزئي")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, side="right", padx=10, pady=10)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 4) شريط الإجمالي وإتمام البيع
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=5, pady=10)

        self.lbl_grand_total = ctk.CTkLabel(
            bottom_frame,
            text="إجمالي الفاتورة: 0.00",
            font=("Arial", 17, "bold"),
            text_color="#2980b9"
        )
        self.lbl_grand_total.pack(side="right", padx=15)

        btn_checkout = ctk.CTkButton(
            bottom_frame,
            text="💰 إتمام البيع وخصم المخزون",
            fg_color="#27ae60",
            hover_color="#219653",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.checkout_sale
        )
        btn_checkout.pack(side="left", padx=15)

    def refresh_items_from_warehouse(self):
        """جلب أسماء الأصناف الموجودة في شاشة المخزون إلى القائمة المنسدلة"""
        if self.warehouse_frame and hasattr(self.warehouse_frame, "tree"):
            stock_names = []
            for row in self.warehouse_frame.tree.get_children():
                vals = self.warehouse_frame.tree.item(row, "values")
                if vals and vals[1].strip():
                    stock_names.append(vals[1].strip())
            if stock_names:
                self.item_combo.configure(values=stock_names)
                self.item_combo.set(stock_names[0])
                return
        self.item_combo.configure(values=self.default_items)
        self.item_combo.set(self.default_items[0])

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

    def clear_item_fields(self):
        current_values = self.item_combo.cget("values")
        if current_values:
            self.item_combo.set(current_values[0])
        self.qty_var.set("")
        self.sell_price_var.set("")

    def add_sale_item_to_table(self):
        name = self.item_combo.get().strip()
        qty_str = self.qty_var.get().replace(",", "").strip()
        sell_str = self.sell_price_var.get().replace(",", "").strip()

        if not (name and qty_str and sell_str):
            messagebox.showwarning("تنبيه", "الرجاء إدخال الصنف، الكمية، وسعر البيع.")
            return

        try:
            qty = int(qty_str)
            sell_price = float(sell_str)

            if qty <= 0 or sell_price < 0:
                messagebox.showwarning("تنبيه", "الكمية يجب أن تكون أكبر من صفر وسعر البيع غير سالب.")
                return

            subtotal = qty * sell_price

            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    f"{qty:,}",
                    f"{sell_price:,.2f}",
                    f"{subtotal:,.2f}"
                )
            )
            self.clear_item_fields()
            self.calculate_totals()
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء التأكد من صحة الأرقام المدخلة.")

    def remove_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد السطر المراد حذفه من الفاتورة أولاً.")
            return

        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا الصنف من فاتورة البيع؟"):
            self.tree.delete(selected[0])
            self.calculate_totals()

    def calculate_totals(self):
        total_amount = 0.0
        for row_id in self.tree.get_children():
            item = self.tree.item(row_id)
            vals = item["values"]
            subtotal = float(str(vals[3]).replace(",", ""))
            total_amount += subtotal

        self.lbl_grand_total.configure(text=f"إجمالي الفاتورة: {total_amount:,.2f}")

    def _validate_stock_before_checkout(self):
        """التحقق من توفر جميع أصناف الفاتورة في المخزون قبل خصم أي كمية"""
        if not self.warehouse_frame or not hasattr(self.warehouse_frame, "tree"):
            return True, ""

        # تجميع الكميات المطلوبة لكل صنف في الفاتورة (في حال تكرار الصنف في أكثر من سطر)
        requested_totals = {}
        for row_id in self.tree.get_children():
            vals = self.tree.item(row_id, "values")
            name = str(vals[0]).strip().lower()
            qty = int(str(vals[1]).replace(",", "").strip())
            requested_totals[name] = requested_totals.get(name, 0) + qty

        # مطابقة الكميات المطلوبة مع المتوفر في جدول المخزون
        available_stock = {}
        display_names = {}
        for row in self.warehouse_frame.tree.get_children():
            w_vals = self.warehouse_frame.tree.item(row, "values")
            w_name = str(w_vals[1]).strip().lower()
            w_qty = int(str(w_vals[2]).replace(",", "").strip())
            available_stock[w_name] = w_qty
            display_names[w_name] = str(w_vals[1]).strip()

        for name_key, req_qty in requested_totals.items():
            if name_key not in available_stock:
                return False, f"الصنف ({name_key}) غير موجود في المخزون."
            if req_qty > available_stock[name_key]:
                return (
                    False,
                    f"الكمية المتوفرة من ({display_names[name_key]}) هي ({available_stock[name_key]:,}) فقط، "
                    f"والمطلوب في الفاتورة ({req_qty:,})."
                )

        return True, ""

    def checkout_sale(self):
        if not self.tree.get_children():
            messagebox.showwarning("تنبيه", "لا توجد أصناف في الفاتورة لإتمام البيع.")
            return

        inv_no = self.invoice_no_entry.get().strip() or "-"
        client = self.client_entry.get().strip() or "زبون نقدي"
        inv_date = self.date_entry.get().strip() or datetime.now().strftime("%Y-%m-%d")

        # التحقق من المخزون أولاً
        is_valid, error_msg = self._validate_stock_before_checkout()
        if not is_valid:
            messagebox.showwarning("نقص في المخزون", error_msg)
            return

        if messagebox.askyesno("تأكيد البيع", f"هل تريد إتمام فاتورة البيع رقم ({inv_no}) وخصم الكميات من المخزون؟"):
            # تنفيذ الخصم الفعلي لكل سطر في المخزون
            if self.warehouse_frame and hasattr(self.warehouse_frame, "deduct_sale_item"):
                for row_id in self.tree.get_children():
                    vals = self.tree.item(row_id, "values")
                    item_name = str(vals[0]).strip()
                    item_qty = int(str(vals[1]).replace(",", "").strip())
                    ok, msg = self.warehouse_frame.deduct_sale_item(item_name, item_qty)
                    if not ok:
                        messagebox.showerror("خطأ أثناء الخصم", msg)
                        return

            messagebox.showinfo(
                "تم البيع",
                f"تم إتمام فاتورة البيع رقم ({inv_no}) بتاريخ ({inv_date}) للعميل ({client}) وخصم الكميات من المخزون."
            )

            for row_id in self.tree.get_children():
                self.tree.delete(row_id)

            self.client_entry.delete(0, "end")
            self.client_entry.insert(0, "زبون نقدي")
            self.invoice_no_entry.delete(0, "end")
            self.invoice_no_entry.insert(0, f"SAL-{datetime.now().strftime('%H%M%S')}")
            self.calculate_totals()