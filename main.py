import customtkinter as ctk
from ui.purchases_ui import PurchasesFrame
from ui.sales_ui import SalesFrame
from ui.reports_ui import ReportsFrame

# دعم اسم الواجهة الجديد للمخازن مع إبقاء توافق احتياطي مع ProductsFrame
try:
    from ui.warehouse_ui import WarehouseFrame
except ImportError:
    from ui.warehouse_ui import ProductsFrame as WarehouseFrame

# استيراد شاشة إدارة الموردين (مع بديل آمن إذا لم يُنشأ الملف بعد)
try:
    from ui.suppliers_ui import SuppliersFrame
except ImportError:
    SuppliersFrame = None

# إعدادات المظهر العام (ثيم مريح للعين)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class StationeryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات نافذة التطبيق الرئيسية
        self.title("نظام إدارة محل القرطاسيات - النسخة الاحترافية")
        self.geometry("1150x720")

        # تخطيط النافذة الرئيسية (قائمة جانبية ومساحة عرض)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. إطار القائمة الجانبية (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#2c3e50")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # عنوان القائمة الجانبية
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="📚 إدارة القرطاسيات",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 25))

        # أزرار التنقل بين الأقسام
        self.btn_purchases = ctk.CTkButton(
            self.sidebar_frame,
            text="🛒 المشتريات",
            font=("Arial", 14, "bold"),
            fg_color="#34495e",
            hover_color="#1abc9c",
            height=40,
            command=self.show_purchases_frame
        )
        self.btn_purchases.grid(row=1, column=0, padx=15, pady=8, sticky="ew")

        self.btn_suppliers = ctk.CTkButton(
            self.sidebar_frame,
            text="🚚 إدارة الموردين",
            font=("Arial", 14, "bold"),
            fg_color="#34495e",
            hover_color="#1abc9c",
            height=40,
            command=self.show_suppliers_frame
        )
        self.btn_suppliers.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_warehouse = ctk.CTkButton(
            self.sidebar_frame,
            text="🏭 المخازن والكميات",
            font=("Arial", 14, "bold"),
            fg_color="#34495e",
            hover_color="#1abc9c",
            height=40,
            command=self.show_warehouse_frame
        )
        self.btn_warehouse.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_sales = ctk.CTkButton(
            self.sidebar_frame,
            text="💰 المبيعات والفواتير",
            font=("Arial", 14, "bold"),
            fg_color="#34495e",
            hover_color="#1abc9c",
            height=40,
            command=self.show_sales_frame
        )
        self.btn_sales.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_reports = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 التقارير والأرباح",
            font=("Arial", 14, "bold"),
            fg_color="#34495e",
            hover_color="#1abc9c",
            height=40,
            command=self.show_reports_frame
        )
        self.btn_reports.grid(row=5, column=0, padx=15, pady=8, sticky="ew")

        # 2. إطار المحتوى الرئيسي (Main Content Area)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # إنشاء وتخزين الشاشات في الواجهة للحفاظ على بيانات العرض عند التنقل
        self.frames = {}
        self._init_frames()

        # عرض شاشة المخازن افتراضياً عند فتح البرنامج
        self.show_warehouse_frame()

    def _on_suppliers_updated(self, supplier_names):
        """تحديث قائمة الموردين في شاشة المشتريات عند إضافة/تعديل/حذف مورد"""
        purchases_view = self.frames.get("purchases")
        if purchases_view and hasattr(purchases_view, "update_suppliers_list"):
            purchases_view.update_suppliers_list(supplier_names)
        elif purchases_view and hasattr(purchases_view, "supplier_combo"):
            current_val = purchases_view.supplier_combo.get()
            purchases_view.supplier_combo.configure(values=supplier_names)
            if supplier_names and current_val not in supplier_names:
                purchases_view.supplier_combo.set(supplier_names[0])

    def _init_frames(self):
        warehouse_view = WarehouseFrame(self.content_frame)
        warehouse_view.grid(row=0, column=0, sticky="nsew")
        self.frames["warehouse"] = warehouse_view

        try:
            purchases_view = PurchasesFrame(self.content_frame, warehouse_frame=warehouse_view)
        except TypeError:
            purchases_view = PurchasesFrame(self.content_frame)
        purchases_view.grid(row=0, column=0, sticky="nsew")
        self.frames["purchases"] = purchases_view

        try:
            sales_view = SalesFrame(self.content_frame, warehouse_frame=warehouse_view)
        except TypeError:
            sales_view = SalesFrame(self.content_frame)
        sales_view.grid(row=0, column=0, sticky="nsew")
        self.frames["sales"] = sales_view

        if SuppliersFrame is not None:
            suppliers_view = SuppliersFrame(
                self.content_frame,
                on_suppliers_changed=self._on_suppliers_updated
            )
            suppliers_view.grid(row=0, column=0, sticky="nsew")
            self.frames["suppliers"] = suppliers_view

        reports_view = ReportsFrame(self.content_frame)
        reports_view.grid(row=0, column=0, sticky="nsew")
        self.frames["reports"] = reports_view

    def _highlight_active_button(self, active_btn):
        buttons = [
            self.btn_purchases,
            self.btn_suppliers,
            self.btn_warehouse,
            self.btn_sales,
            self.btn_reports
        ]
        for btn in buttons:
            btn.configure(fg_color="#1abc9c" if btn is active_btn else "#34495e")

    def show_frame(self, key, active_btn):
        frame = self.frames.get(key)
        if frame:
            frame.tkraise()
            self._highlight_active_button(active_btn)

    def show_purchases_frame(self):
        self.show_frame("purchases", self.btn_purchases)

    def show_suppliers_frame(self):
        self.show_frame("suppliers", self.btn_suppliers)

    def show_warehouse_frame(self):
        self.show_frame("warehouse", self.btn_warehouse)

    def show_sales_frame(self):
        sales_view = self.frames.get("sales")
        if sales_view and hasattr(sales_view, "refresh_items_from_warehouse"):
            sales_view.refresh_items_from_warehouse()
        self.show_frame("sales", self.btn_sales)

    def show_reports_frame(self):
        self.show_frame("reports", self.btn_reports)


if __name__ == "__main__":
    app = StationeryApp()
    app.mainloop()