import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.suppliers_service import (
    get_all_suppliers,
    add_supplier as db_add_supplier,
    update_supplier as db_update_supplier,
    delete_supplier as db_delete_supplier,
)


class SuppliersFrame(ctk.CTkFrame):
    def __init__(self, parent, on_suppliers_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.on_suppliers_changed = on_suppliers_changed

        # عنوان القسم
        title_lbl = ctk.CTkLabel(
            self,
            text="🚚 إدارة الموردين",
            font=("Arial", 22, "bold")
        )
        title_lbl.pack(anchor="e", pady=(0, 12), padx=10)

        # شريط البحث
        search_frame = ctk.CTkFrame(self, corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 10), padx=5)

        lbl_search = ctk.CTkLabel(
            search_frame,
            text="🔍 بحث (اسم المورد / الهاتف / العنوان):",
            font=("Arial", 13, "bold")
        )
        lbl_search.pack(side="right", padx=10, pady=8)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="اكتب للبحث عن مورد...",
            justify="right",
            width=320,
            height=34
        )
        self.search_entry.pack(side="right", padx=10, pady=8)
        self.search_entry.bind("<KeyRelease>", self.filter_suppliers)

        # نموذج إدخال وتعديل بيانات المورد
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 12), padx=5)

        lbl_name = ctk.CTkLabel(form_frame, text="اسم المورد:", font=("Arial", 13, "bold"))
        lbl_name.grid(row=0, column=2, padx=15, pady=(10, 0), sticky="e")
        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="مثال: مؤسسة النور للقرطاسية",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.name_entry.grid(row=1, column=2, padx=15, pady=(0, 12), sticky="ew")

        lbl_phone = ctk.CTkLabel(form_frame, text="رقم الهاتف:", font=("Arial", 13, "bold"))
        lbl_phone.grid(row=0, column=1, padx=15, pady=(10, 0), sticky="e")
        self.phone_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="مثال: 771234567",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.phone_entry.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        lbl_address = ctk.CTkLabel(form_frame, text="العنوان / ملاحظات:", font=("Arial", 13, "bold"))
        lbl_address.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="e")
        self.address_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="مثال: صنعاء - شارع جمال",
            justify="right",
            height=35,
            font=("Arial", 14)
        )
        self.address_entry.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        form_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # أزرار التحكم
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=(0, 12))

        btn_add = ctk.CTkButton(
            btn_frame,
            text="➕ إضافة مورد",
            fg_color="#27ae60",
            hover_color="#219653",
            height=38,
            font=("Arial", 13, "bold"),
            command=self.add_supplier
        )
        btn_add.pack(side="left", padx=8)

        btn_update = ctk.CTkButton(
            btn_frame,
            text="✏️ تعديل المحدد",
            fg_color="#d35400",
            hover_color="#ba4a00",
            height=38,
            font=("Arial", 13, "bold"),
            command=self.update_supplier
        )
        btn_update.pack(side="left", padx=8)

        btn_delete = ctk.CTkButton(
            btn_frame,
            text="🗑️ حذف المحدد",
            fg_color="#c0392b",
            hover_color="#962d22",
            height=38,
            font=("Arial", 13, "bold"),
            command=self.delete_supplier
        )
        btn_delete.pack(side="left", padx=8)

        btn_clear = ctk.CTkButton(
            btn_frame,
            text="🧹 تفريغ الحقول",
            fg_color="#7f8c8d",
            hover_color="#62686f",
            height=38,
            font=("Arial", 13),
            command=self.clear_entries
        )
        btn_clear.pack(side="left", padx=8)

        # جدول الموردين
        table_frame = ctk.CTkFrame(self, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("م", "اسم المورد", "رقم الهاتف", "العنوان / ملاحظات")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        widths = {"م": 70, "اسم المورد": 220, "رقم الهاتف": 150, "العنوان / ملاحظات": 250}
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=widths.get(col, 140), anchor="center")

        self.tree.pack(fill="both", expand=True, side="right", padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.load_suppliers()

    def load_suppliers(self):
        """جلب الموردين من قاعدة البيانات MySQL وتحديث الجدول"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        ok, rows, err_msg = get_all_suppliers()
        if not ok:
            messagebox.showerror("خطأ قاعدة البيانات", err_msg)
            self._notify_suppliers_changed()
            return

        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    str(r["id"]),
                    r["name"],
                    r["phone"] or "-",
                    r["address"] or "-"
                )
            )
        self._notify_suppliers_changed()

    def _notify_suppliers_changed(self):
        if callable(self.on_suppliers_changed):
            self.on_suppliers_changed(self.get_supplier_names())

    def get_supplier_names(self):
        """إرجاع قائمة أسماء الموردين الحالية في الجدول"""
        names = []
        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            if vals and vals[1].strip():
                names.append(vals[1].strip())
        return names if names else ["مورد عام"]

    def add_supplier(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم المورد.")
            return

        ok, msg = db_add_supplier(name, phone, address)
        if not ok:
            messagebox.showwarning("تنبيه", msg)
            return

        self.clear_entries()
        self.load_suppliers()
        messagebox.showinfo("نجاح", msg)

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            vals = self.tree.item(selected[0], "values")
            self.clear_entries()
            self.name_entry.insert(0, vals[1])
            if vals[2] != "-":
                self.phone_entry.insert(0, vals[2])
            if vals[3] != "-":
                self.address_entry.insert(0, vals[3])

    def update_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد المورد المراد تعديله من الجدول أولاً.")
            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning("تنبيه", "اسم المورد مطلوب.")
            return

        if messagebox.askyesno("تأكيد التعديل", "هل أنت متأكد من حفظ التعديلات على بيانات المورد؟"):
            current_vals = self.tree.item(selected[0], "values")
            supplier_id = current_vals[0]
            ok, msg = db_update_supplier(supplier_id, name, phone, address)
            if not ok:
                messagebox.showwarning("تنبيه", msg)
                return

            self.clear_entries()
            self.load_suppliers()
            messagebox.showinfo("نجاح", msg)

    def delete_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء تحديد المورد المراد حذفه من الجدول أولاً.")
            return

        if messagebox.askyesno(
            "تحذير الحذف",
            "هل أنت متأكد من حذف هذا المورد؟ لا يمكن التراجع عن هذا الإجراء."
        ):
            current_vals = self.tree.item(selected[0], "values")
            supplier_id = current_vals[0]
            ok, msg = db_delete_supplier(supplier_id)
            if not ok:
                messagebox.showwarning("تنبيه", msg)
                return

            self.clear_entries()
            self.load_suppliers()
            messagebox.showinfo("تم الحذف", msg)

    def filter_suppliers(self, event):
        query = self.search_entry.get().strip().lower()
        for row in self.tree.get_children():
            vals = self.tree.item(row, "values")
            matched = (
                query in vals[1].lower()
                or query in vals[2].lower()
                or query in vals[3].lower()
            )
            if matched:
                self.tree.reattach(row, "", "end")
            else:
                self.tree.detach(row)

    def clear_entries(self):
        self.name_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.address_entry.delete(0, "end")