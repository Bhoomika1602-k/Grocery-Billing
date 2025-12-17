# main.py – Grocery Billing (FoodHills)
import sys
from pathlib import Path
from math import sin
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

# ---------------- DB IMPORT ----------------
THIS_DIR = Path(__file__).parent.resolve()
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from db import init_db, save_purchase
init_db()

# ---------------- COLORS ----------------
BG1 = "#FFE4EC"
BG2 = "#FFF9F4"
CARD = "#FFFFFF"
ACCENT = "#FF96B8"
ACCENT2 = "#FF6F91"
TEXT = "#523A41"

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("Grocery Billing (FoodHills)")
root.geometry("950x720")
root.config(bg=BG1)
root.resizable(False, False)

# ---------------- HEADER ----------------
header = tk.Canvas(root, width=950, height=120, bg=BG1, highlightthickness=0)
header.pack(fill="x")

header.create_text(
    475, 30,
    text="Grocery Billing (FoodHills)",
    font=("Comic Sans MS", 28, "bold"),
    fill=ACCENT2
)
header.create_text(
    475, 70,
    text="Smart grocery billing with AI suggestions",
    font=("Comic Sans MS", 14),
    fill="#7A4F57"
)

# ---------------- FLOATING FOOD ----------------
food_emojis = ["🍎", "🍞", "🥛", "🥚", "🍚", "🧈", "🍪"]
float_items = []

for i, emo in enumerate(food_emojis):
    t = header.create_text(80 + i * 120, 105, text=emo, font=("Segoe UI Emoji", 26))
    float_items.append((t, i))

wave = 0
def animate():
    global wave
    wave += 0.08
    for item, phase in float_items:
        header.coords(item, 80 + phase * 120, 105 + 6 * sin(wave + phase))
    header.after(60, animate)

animate()

# ---------------- MAIN CARD ----------------
main_card = tk.Frame(root, bg=CARD, bd=2, relief="ridge")
main_card.place(x=50, y=150, width=850, height=520)

# ---------------- STYLE ----------------
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background=CARD, foreground=TEXT,
                font=("Comic Sans MS", 12))
style.configure("TButton", background=ACCENT, foreground="white",
                font=("Comic Sans MS", 12, "bold"), padding=6)

# ================= LEFT PANEL =================
left = ttk.Frame(main_card)
left.place(x=20, y=20, width=520, height=480)

ttk.Label(left, text="Grocery Items",
          font=("Comic Sans MS", 16, "bold")).pack(pady=10)

# ---------------- SEARCH ----------------
search_var = tk.StringVar()
search_placeholder = "Search..."
search_entry = ttk.Entry(left, width=40, textvariable=search_var, foreground="grey")
search_entry.pack(pady=5)
search_var.set(search_placeholder)

def remove_placeholder(e=None):
    if search_var.get() == search_placeholder:
        search_entry.config(foreground="black")
        search_var.set("")

def add_placeholder(e=None):
    if search_var.get() == "":
        search_entry.config(foreground="grey")
        search_var.set(search_placeholder)

search_entry.bind("<FocusIn>", remove_placeholder)
search_entry.bind("<FocusOut>", add_placeholder)

suggestion_list = tk.Listbox(left, height=6, bg="#FFF0F5", fg=TEXT)
suggestion_list.pack(fill="x")
suggestion_list.pack_forget()

# ---------------- ITEMS CANVAS ----------------
canvas_items = tk.Canvas(left, bg=BG2, highlightthickness=0)
scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas_items.yview)
items_frame = ttk.Frame(canvas_items)
canvas_items.create_window((0, 0), window=items_frame, anchor="nw")
canvas_items.configure(yscrollcommand=scrollbar.set)
canvas_items.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------------- INITIAL ITEMS ----------------
items = {
    "Milk": 45,
    "Bread": 25,
    "Eggs (Dozen)": 60,
    "Rice (1kg)": 70,
    "Sugar (1kg)": 50,
    "Tea (250g)": 120,
    "Oil (1L)": 150
}

# ---------------- MASTER AI INGREDIENTS (A–Z FULL) ----------------
master_ingredients = {
    "Apple": 120, "Atta (1kg)": 55,
    "Banana": 40, "Bread": 25, "Butter": 55, "Biscuit": 30,
    "Cheese": 80, "Curd": 35, "Coffee": 150,
    "Dal (1kg)": 90,
    "Eggs (Dozen)": 60,
    "Flour": 45,
    "Ghee": 220,
    "Honey": 180,
    "Ice Cream": 200,
    "Jam": 95,
    "Ketchup": 110,
    "Lentils": 85,
    "Milk": 45, "Maida": 50,
    "Noodles": 60,
    "Oil (1L)": 150,
    "Pasta": 75,
    "Quinoa": 140,
    "Rice (1kg)": 70,
    "Salt": 20, "Sugar (1kg)": 50,
    "Tea (250g)": 120,
    "Urad Dal": 95,
    "Vinegar": 65,
    "Wheat Flour": 55,
    "Xanthan Gum": 250,
    "Yeast": 70,
    "Zucchini": 60
}

item_vars, qty_vars, price_vars = {}, {}, {}

# ---------------- AI SEARCH LOGIC ----------------
def update_suggestions(e=None):
    text = search_var.get().strip().lower()
    suggestion_list.delete(0, tk.END)

    if not text or text == search_placeholder.lower():
        suggestion_list.pack_forget()
        return

    matches = [i for i in master_ingredients if i.lower().startswith(text)]

    if matches:
        suggestion_list.pack(fill="x")
        for m in matches:
            suggestion_list.insert(tk.END, m)
    else:
        suggestion_list.pack_forget()

def fill_from_search(e=None):
    if not suggestion_list.curselection():
        return
    selected = suggestion_list.get(suggestion_list.curselection())
    search_var.set(selected)
    suggestion_list.pack_forget()

    if selected not in items:
        items[selected] = master_ingredients[selected]
        add_item_row(selected, items[selected])

search_entry.bind("<KeyRelease>", update_suggestions)
suggestion_list.bind("<<ListboxSelect>>", fill_from_search)

# ---------------- ADD ITEM ROW ----------------
def add_item_row(name, price):
    row = ttk.Frame(items_frame)
    row.pack(fill="x", pady=5, padx=8)

    chk = tk.BooleanVar()
    qty = tk.IntVar(value=1)
    price_var = tk.DoubleVar(value=price)

    item_vars[name] = chk
    qty_vars[name] = qty
    price_vars[name] = price_var

    ttk.Checkbutton(row, text=name, variable=chk).pack(side="left")
    ttk.Label(row, text="₹").pack(side="left")
    ttk.Entry(row, width=6, textvariable=price_var).pack(side="left", padx=4)
    ttk.Label(row, text="Qty").pack(side="left")
    ttk.Entry(row, width=4, textvariable=qty).pack(side="left")

for n, p in items.items():
    add_item_row(n, p)

# ---------------- SAVE BILL TO DATE FOLDER ----------------
def save_bill_to_folder(bill_text, bill_date):
    folder = Path(__file__).parent / "billing_history" / bill_date
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "bill.txt", "a", encoding="utf-8") as f:
        f.write("\n" + "-" * 40 + "\n")
        f.write(bill_text)

# ---------------- VIEW BILL HISTORY ----------------
def view_history():
    base = Path(__file__).parent / "billing_history"
    base.mkdir(exist_ok=True)

    win = tk.Toplevel(root)
    win.title("Bill History")
    win.geometry("400x300")

    lb = tk.Listbox(win)
    lb.pack(fill="both", expand=True, padx=10, pady=10)

    for d in sorted(base.iterdir(), reverse=True):
        if d.is_dir():
            lb.insert(tk.END, d.name)

    def open_folder(e):
        sel = lb.get(lb.curselection())
        os.startfile(base / sel)

    lb.bind("<Double-Button-1>", open_folder)

# ================= RIGHT PANEL =================
right = ttk.Frame(main_card)
right.place(x=560, y=20, width=270, height=480)

ttk.Label(right, text="Add Custom Item",
          font=("Comic Sans MS", 15, "bold")).pack(pady=8)

ttk.Label(right, text="Food Item Name").pack()
ent_name = ttk.Entry(right, width=20)
ent_name.pack(pady=3)

ttk.Label(right, text="Price (₹)").pack()
ent_price = ttk.Entry(right, width=10)
ent_price.pack(pady=3)

def add_custom():
    nm = ent_name.get().strip()
    if not nm:
        return
    try:
        price = float(ent_price.get())
    except:
        return
    items[nm] = price
    add_item_row(nm, price)
    ent_name.delete(0, tk.END)
    ent_price.delete(0, tk.END)

ttk.Button(right, text="Add", command=add_custom).pack(pady=5)

ttk.Label(right, text="Bill Date").pack()
date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
ttk.Entry(right, textvariable=date_var).pack()

# ---------------- GENERATE BILL ----------------
def generate_bill():
    total = 0
    bill = f"Bill Date: {date_var.get()}\n\n"

    for name, chk in item_vars.items():
        if chk.get():
            qty = qty_vars[name].get()
            price = price_vars[name].get()
            cost = qty * price
            total += cost
            bill += f"{name} x {qty} @ ₹{price} = ₹{cost}\n"
            save_purchase(name, price, qty, cost)

    if total == 0:
        messagebox.showwarning("Empty", "Please select items")
        return

    bill += f"\nTotal = ₹{total}"
    save_bill_to_folder(bill, date_var.get())
    messagebox.showinfo("Bill Generated", bill)

ttk.Button(right, text="Generate Bill", command=generate_bill).pack(pady=10)
ttk.Button(right, text="View Bill History", command=view_history).pack(pady=5)
ttk.Button(right, text="Exit", command=root.destroy).pack(side="bottom", pady=10)

root.mainloop()