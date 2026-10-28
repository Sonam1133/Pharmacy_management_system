"""
Pharmacy Management System — Main application entry point.

Stack:
    - Tkinter  : GUI (standard library)
    - SQLite3  : database (standard library)
    - hashlib  : password hashing (standard library)

Tabs:
    - Inventory : add / view / low-stock alerts
    - Sales     : record sales (atomically updates stock)
    - Reports   : KPI strip + top-selling / daily-revenue charts
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from database.db_setup import initialize_database
from modules import auth, inventory, sales, reports
from modules.chart import BarChart


APP_TITLE = "Pharmacy Management System"


class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1150x720")
        self.root.minsize(950, 600)
        self.current_user = None
        self._apply_style()
        self.show_login()

    # ------------------------------------------------------------------ #
    #  Styling
    # ------------------------------------------------------------------ #
    def _apply_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TNotebook.Tab", padding=(16, 8), font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 20, "bold"))
        style.configure("Sub.TLabel",    font=("Helvetica", 11))
        style.configure("KPI.TLabel",    font=("Helvetica", 16, "bold"))
        style.configure("Treeview", rowheight=24, font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------ #
    #  LOGIN SCREEN
    # ------------------------------------------------------------------ #
    def show_login(self):
        self.clear_root()

        # Centre card
        card = ttk.Frame(self.root, padding=40, relief="ridge", borderwidth=2)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Pharmacy Management System",
                  style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 5))
        ttk.Label(card, text="Please sign in to continue",
                  style="Sub.TLabel", foreground="gray").grid(
            row=1, column=0, columnspan=2, pady=(0, 25))

        ttk.Label(card, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=6)
        self.login_user = ttk.Entry(card, width=28)
        self.login_user.grid(row=2, column=1, pady=6)

        ttk.Label(card, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=6)
        self.login_pass = ttk.Entry(card, width=28, show="*")
        self.login_pass.grid(row=3, column=1, pady=6)

        # Bind <Return> on password field to trigger login
        self.login_pass.bind("<Return>", lambda _e: self.do_login())
        self.login_user.focus_set()

        ttk.Button(card, text="Login", command=self.do_login, width=22).grid(
            row=4, column=0, columnspan=2, pady=(20, 6))
        ttk.Button(card, text="Register New Staff", command=self.do_register,
                   width=22).grid(row=5, column=0, columnspan=2)

    def do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        if not username or not password:
            messagebox.showwarning("Missing Input", "Please enter username and password.")
            return

        user = auth.authenticate(username, password)
        if user:
            self.current_user = user
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.login_pass.delete(0, tk.END)

    def do_register(self):
        uname = simpledialog.askstring("Register", "New username:", parent=self.root)
        if not uname:
            return
        pwd = simpledialog.askstring("Register", "New password:", show="*", parent=self.root)
        if not pwd:
            return

        if auth.register_user(uname.strip(), pwd, role="staff"):
            messagebox.showinfo("Success", "Staff account created. You may now log in.")
        else:
            messagebox.showerror("Error", "That username is already taken.")

    # ------------------------------------------------------------------ #
    #  DASHBOARD
    # ------------------------------------------------------------------ #
    def show_dashboard(self):
        self.clear_root()

        # Header bar
        header = ttk.Frame(self.root, padding=(10, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Dashboard", style="Header.TLabel").pack(side="left")
        ttk.Button(header, text="Logout", command=self.logout).pack(side="right")

        # Notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        inv_tab     = ttk.Frame(self.notebook)
        sales_tab   = ttk.Frame(self.notebook)
        reports_tab = ttk.Frame(self.notebook)

        self.notebook.add(inv_tab,     text="  Inventory  ")
        self.notebook.add(sales_tab,   text="  Sales  ")
        self.notebook.add(reports_tab, text="  Reports  ")

        self.build_inventory_tab(inv_tab)
        self.build_sales_tab(sales_tab)
        self.build_reports_tab(reports_tab)

        # Status bar
        status = ttk.Label(
            self.root,
            text=f"Logged in as: {self.current_user['username']}  ({self.current_user['role']})",
            relief="sunken", anchor="w", padding=(8, 4)
        )
        status.pack(side="bottom", fill="x")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.current_user = None
            self.show_login()

    # ------------------------------------------------------------------ #
    #  INVENTORY TAB
    # ------------------------------------------------------------------ #
    def build_inventory_tab(self, parent):
        top = ttk.Frame(parent, padding=(8, 8))
        top.pack(fill="x")

        ttk.Button(top, text="Add Medicine",
                   command=self.add_medicine_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh",
                   command=lambda: self.refresh_inventory(self.inv_tree)).pack(side="left", padx=4)
        ttk.Button(top, text="Low Stock Alert",
                   command=self.show_low_stock).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Selected",
                   command=self.delete_selected_medicine).pack(side="left", padx=4)

        # Search box
        ttk.Label(top, text="Search:").pack(side="left", padx=(20, 4))
        self.inv_search = ttk.Entry(top, width=24)
        self.inv_search.pack(side="left")
        self.inv_search.bind("<KeyRelease>", lambda _e: self.filter_inventory())

        # Table
        cols = ("ID", "Name", "Company", "Category", "Batch", "Expiry", "Price", "Stock", "Rx")
        self.inv_tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        widths = {"ID": 50, "Name": 160, "Company": 120, "Category": 110,
                  "Batch": 90, "Expiry": 100, "Price": 80, "Stock": 70, "Rx": 50}
        for c in cols:
            self.inv_tree.heading(c, text=c)
            self.inv_tree.column(c, width=widths[c], anchor="center" if c != "Name" else "w")
        self.inv_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Row tags for low-stock highlight
        self.inv_tree.tag_configure("low", background="#fff3cd")
        self.inv_tree.tag_configure("zero", background="#f8d7da")

        self.refresh_inventory(self.inv_tree)

    def refresh_inventory(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        for med in inventory.get_all_medicines():
            tag = ""
            if med["stock"] == 0:
                tag = "zero"
            elif med["stock"] <= inventory.LOW_STOCK_THRESHOLD:
                tag = "low"
            tree.insert("", "end", values=(
                med["id"], med["name"], med["company"] or "", med["category"] or "",
                med["batch_no"] or "", med["expiry_date"] or "",
                f"{med['price']:.2f}", med["stock"],
                "Yes" if med["prescription_required"] else "No"
            ), tags=(tag,) if tag else ())

    def filter_inventory(self):
        term = self.inv_search.get().strip().lower()
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        for med in inventory.get_all_medicines():
            if term and term not in (med["name"] or "").lower() \
                    and term not in (med["company"] or "").lower() \
                    and term not in (med["category"] or "").lower():
                continue
            tag = ""
            if med["stock"] == 0:
                tag = "zero"
            elif med["stock"] <= inventory.LOW_STOCK_THRESHOLD:
                tag = "low"
            self.inv_tree.insert("", "end", values=(
                med["id"], med["name"], med["company"] or "", med["category"] or "",
                med["batch_no"] or "", med["expiry_date"] or "",
                f"{med['price']:.2f}", med["stock"],
                "Yes" if med["prescription_required"] else "No"
            ), tags=(tag,) if tag else ())

    def add_medicine_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("Add Medicine")
        d.transient(self.root)
        d.grab_set()
        d.resizable(False, False)

        fields = [
            ("Name",                    "Paracetamol 500mg"),
            ("Company",                 "GSK"),
            ("Category",                "Analgesic"),
            ("Batch No",                "B2024A"),
            ("Expiry (YYYY-MM-DD)",     "2027-06-30"),
            ("Price",                   "5.50"),
            ("Stock",                   "100"),
            ("Prescription (0/1)",      "0"),
        ]
        entries = {}
        for i, (label, hint) in enumerate(fields):
            ttk.Label(d, text=label + ":").grid(row=i, column=0, sticky="e", padx=8, pady=4)
            e = ttk.Entry(d, width=30)
            e.grid(row=i, column=1, padx=8, pady=4)
            e.insert(0, "")   # leave empty; hint shown as placeholder via label below
            entries[label] = e

        ttk.Label(d, text="Tip: date format is YYYY-MM-DD", foreground="gray").grid(
            row=len(fields), column=0, columnspan=2, pady=(4, 0))

        def save():
            name = entries["Name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Medicine name is required.", parent=d)
                return
            try:
                price = float(entries["Price"].get())
                stock = int(entries["Stock"].get())
                rx    = int(entries["Prescription (0/1)"].get() or 0)
            except ValueError:
                messagebox.showerror("Error", "Price, Stock, and Rx must be numeric.", parent=d)
                return

            inventory.add_medicine(
                name,
                entries["Company"].get().strip(),
                entries["Category"].get().strip(),
                entries["Batch No"].get().strip(),
                entries["Expiry (YYYY-MM-DD)"].get().strip(),
                price, stock, rx
            )
            messagebox.showinfo("Success", f"'{name}' added to inventory.", parent=d)
            d.destroy()
            self.refresh_inventory(self.inv_tree)

        ttk.Button(d, text="Save", command=save, width=18).grid(
            row=len(fields) + 1, column=0, columnspan=2, pady=14)

    def show_low_stock(self):
        low = inventory.get_low_stock_medicines()
        if not low:
            messagebox.showinfo("Low Stock", "All medicines have sufficient stock.")
            return
        lines = [f"• {m['name']}  —  {m['stock']} left" for m in low]
        messagebox.showwarning(
            "Low Stock Alert",
            f"{len(low)} medicine(s) need restocking:\n\n" + "\n".join(lines)
        )

    def delete_selected_medicine(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a medicine row first.")
            return
        values = self.inv_tree.item(sel[0], "values")
        med_id, med_name = values[0], values[1]
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete '{med_name}' (ID {med_id})?\n"
                                   "Historical sales will be kept."):
            return
        inventory.delete_medicine(int(med_id))
        self.refresh_inventory(self.inv_tree)

    # ------------------------------------------------------------------ #
    #  SALES TAB
    # ------------------------------------------------------------------ #
    def build_sales_tab(self, parent):
        form = ttk.LabelFrame(parent, text="Record a Sale", padding=12)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Medicine ID:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.sale_med_id = ttk.Entry(form, width=12)
        self.sale_med_id.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Quantity:").grid(row=0, column=2, sticky="e", padx=4, pady=4)
        self.sale_qty = ttk.Entry(form, width=12)
        self.sale_qty.grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(form, text="Customer:").grid(row=0, column=4, sticky="e", padx=4, pady=4)
        self.sale_customer = ttk.Entry(form, width=22)
        self.sale_customer.grid(row=0, column=5, padx=4, pady=4)

        ttk.Button(form, text="Record Sale", command=self.record_sale, width=18).grid(
            row=0, column=6, padx=(20, 4), pady=4)

        ttk.Label(form, text="Tip: check the Inventory tab for medicine IDs.",
                  foreground="gray").grid(row=1, column=0, columnspan=7, sticky="w",
                                          padx=4, pady=(6, 0))

        # Sales table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("Sale ID", "Medicine", "Qty", "Unit Price", "Total", "Date", "Customer")
        self.sales_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        widths = {"Sale ID": 70, "Medicine": 180, "Qty": 60, "Unit Price": 100,
                  "Total": 100, "Date": 160, "Customer": 150}
        for c in cols:
            self.sales_tree.heading(c, text=c)
            self.sales_tree.column(c, width=widths[c],
                                   anchor="center" if c not in ("Medicine", "Date", "Customer") else "w")
        self.sales_tree.pack(fill="both", expand=True)

        ttk.Button(parent, text="Refresh Sales",
                   command=self.refresh_sales).pack(pady=(0, 10))

        self.refresh_sales()

    def record_sale(self):
        try:
            med_id = int(self.sale_med_id.get())
            qty    = int(self.sale_qty.get())
        except ValueError:
            messagebox.showerror("Error", "Medicine ID and Quantity must be integers.")
            return

        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than zero.")
            return

        customer = self.sale_customer.get().strip()

        if sales.record_sale(med_id, qty, customer):
            messagebox.showinfo("Success", "Sale recorded and stock updated.")
            self.sale_med_id.delete(0, tk.END)
            self.sale_qty.delete(0, tk.END)
            self.sale_customer.delete(0, tk.END)
            self.refresh_sales()
            self.refresh_inventory(self.inv_tree)
        else:
            messagebox.showerror(
                "Sale Failed",
                "Could not record sale.\n"
                "Check that the Medicine ID exists and stock is sufficient."
            )

    def refresh_sales(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        for s in sales.get_all_sales():
            self.sales_tree.insert("", "end", values=(
                s["id"], s["medicine_name"], s["quantity"],
                f"{s['unit_price']:.2f}", f"{s['total_amount']:.2f}",
                s["sale_date"], s["customer_name"] or ""
            ))

    # ------------------------------------------------------------------ #
    #  REPORTS TAB
    # ------------------------------------------------------------------ #
    def build_reports_tab(self, parent):
        # KPI strip
        kpi_frame = ttk.Frame(parent)
        kpi_frame.pack(fill="x", padx=10, pady=(12, 6))

        s = reports.get_summary()
        kpis = [
            ("Total Revenue",  f"{s['revenue']:.2f}"),
            ("Sales Recorded", str(s["sales_count"])),
            ("Medicines",      str(s["medicines"])),
            ("Low Stock",      str(s["low_stock"])),
        ]
        for i, (label, value) in enumerate(kpis):
            box = ttk.LabelFrame(kpi_frame, text=label, padding=10)
            box.grid(row=0, column=i, padx=6, sticky="nsew")
            ttk.Label(box, text=value, style="KPI.TLabel").pack()
            kpi_frame.columnconfigure(i, weight=1)

        # Chart container (kept for reuse)
        self.chart_frame = ttk.Frame(parent)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=6)

        # Controls
        controls = ttk.Frame(parent)
        controls.pack(fill="x", padx=10, pady=(4, 12))

        ttk.Button(controls, text="Top-Selling Medicines",
                   command=self.show_top_selling_chart).pack(side="left", padx=4)
        ttk.Button(controls, text="Last 7 Days Revenue",
                   command=self.show_daily_chart).pack(side="left", padx=4)
        ttk.Button(controls, text="Refresh KPIs",
                   command=lambda: self.rebuild_reports(parent)).pack(side="left", padx=4)

        # Show default chart
        self.show_top_selling_chart()

    def rebuild_reports(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        self.build_reports_tab(parent)

    def _render_chart(self, data, title):
        for w in self.chart_frame.winfo_children():
            w.destroy()
        chart = BarChart(self.chart_frame, data, title=title)
        chart.pack(fill="both", expand=True)

    def show_top_selling_chart(self):
        rows = reports.get_top_selling(5)
        data = [(name, qty) for name, qty, _ in rows]
        self._render_chart(data, "Top 5 Best-Selling Medicines")

    def show_daily_chart(self):
        rows = reports.get_daily_totals(7)
        # row = (YYYY-MM-DD, revenue) newest-first; reverse so oldest is on the left
        data = [(day[5:], rev) for day, rev in rows]
        data.reverse()
        self._render_chart(data, "Revenue — Last 7 Days")


# ---------------------------------------------------------------------- #
#  Entry point
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()
