import random
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from tkinter import font
from datetime import datetime, timedelta
from prettytable import PrettyTable
import MySQLdb
from win32printing import Printer
import xlsxwriter
import os
from tkinter import colorchooser

import socket
# from requests import get

# make exe
# https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9
# pip install auto-py-to-exe
# auto-py-to-exe
# ---------- Marketing Website ---------- #
# ---------- hippos.netlify.app ---------- #

# ---------- server info ---------- #
local_ip = socket.gethostbyname(socket.gethostname())
# public_ip = get('https://api.ipify.org').text
public_ip = 'localhost'
print('localhost', local_ip, public_ip)
# ---------- server info ---------- #

#   TO DO`S:
#  backend for office web gui:
#       - analytics
#       - receipts
#       - web gui
#       - people logged/clocked
#       - current sales
#       - current day profit margin
# - exercise : make button to work only monday/tuesday/wednesday and to give 50% the bill, up to max £10/pers, only on mains


# bonus SQL commands:  // maybe later on implemented into an app, desktop/mobile or straight on the till
# ------------------------
# how much £ sales:
# SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%11/2021%"
# ------------------------
# how many hours someone worked in what time
# bonus --------- to use later on for a manager/staff app
# SELECT SUM(total_time) FROM `staff_hours` WHERE name = "Mihai" & & clocked_in LIKE "2021-%"
# ------------------------
# app idea for getting Net Profit Margin for daily/ weekly/ monthly/ yearly
# Net Profit Margin % = (Gross Revenue – Operating Expenses)/Gross Sales x 100
# Gross Revenue = sale of food/drinks/other
# Operating Expenses = ingredients/rent/wages/equipment/utilities/interest/taxes/repairs/maintenance
# ------------------------
# os.system('ECHO>COM8')  # cash drawer port

# GLOBAL VARIABLES
REAL_PRINT = False  # dev option: to use real printer or not
dev_reset_timer = False  # screensaver//dev opt
a_frame = None  # charging button
waiting_timer = None  # charging button
printer_font_sml = {"height": 10, "font": "Arial"}
printer_font_reg = {"height": 12, "font": "Arial"}
printer_font_XL = {"height": 16, "font": "Arial"}
DRAWER_PORT = "COM8"  # cash drawer settings
OPEN_IT = False  # cash drawer settings/dev opt
STOCK_MOD = False
STATUS = None
STOCK_SWITCH = 0
screen_logo = None
MEMBER_ID = 1
SCREENSAVER_TIMER = None
SCREENSAVER_TIMER2 = None
PRICE_DISCOUNT = 0  # if not 0, it will be considered
root_bg_color = "lightblue"  # root bg color
TEMP_BUTTONS = []  # for till buttons with stock
TEMP_BUTTONS2 = []  # for till buttons with only command
TEMP_FRAME = []
TEMP_LABEL = []
PUB_ID = "1"
PUB_NAME = "The Black Hart"
TABLE_NUMBER = 0  # if T:0 = bar
now = datetime.now()
time = now.strftime("%d/%m/%Y - %H:%M:%S")
SAME_DAY = now.strftime("%d")
CHECK_NUMBER = int  # check number that resets count daily
basket = []  # adding "bought" items, maybe later on not needed
total_price = 0.00  # total sum on the print, rounded to 2 decimals
icecream_frame = ""
icecream = []
icecream_buttons = []

# admin-------- future dev: check if pub is given access ( if subscription is paid, etc )
# adminHost = f"{public_ip}"
# adminPort = 3306
# adminUser = "PUBCON"
# adminPasswd = "Pubcon123$"
# adminDB = "posloc"

# adminconn = MySQLdb.connect(host=adminHost, port=adminPort, user=adminUser, passwd=adminPasswd, db=adminDB)
# admincursor = adminconn.cursor()

# admin--------
# admincursor.execute("INSERT INTO `pos`(`id_pub`, `id_phone`, `id_access`) VALUES ('pub_name','pub_phone','boolean')")


# # sql conn
sqlHost = f"{public_ip}"
sqlPort = 3306
sqlUser = "root"
sqlPasswd = ""
sqlDB = "blackhart"

# sqlHost = "remotemysql.com" medium speed
# sqlPort = 3306
# sqlUser = "ZfWgqnVXHb"
# sqlPasswd = "3bHM2J98KK"
# sqlDB = "ZfWgqnVXHb"

#
# sqlHost = "192.168.1.115"
# sqlPort = 3306
# sqlUser = "TILL1"
# sqlPasswd = "Pubcon123$_2"
# sqlDB = "blackhart"

# will hash later to hide them
conn = MySQLdb.connect(host=sqlHost, port=sqlPort, user=sqlUser, passwd=sqlPasswd, db=sqlDB)
cursor = conn.cursor()

# screen size
WIDTH = 1024
HEIGHT = 768

root = tk.Tk()
root.title("Mihai P.O.S. - :D")
photo = PhotoImage(file="icons/dog.png")
logo = PhotoImage(file="icons/logo.png")
root.iconphoto(False, photo)
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(width=0, height=0)
root.configure(bg=root_bg_color)

# root.state('zoomed') # force full screen
# root.wm_attributes("-fullscreen", "true", "-topmost", "true")  # disabled until app goes live on touchscreen
iconz = PhotoImage(file=r"icons/print.png")

# font
font = font.Font(family="Arial", size=12, weight="bold")
# button background img

total_price_label = Label(root, text=f"TOTAL : £{format(total_price, '.2f')}", font="Arial 18 bold", bg=root_bg_color,
                          justify="center")
total_price_label.grid(row=6, column=0, columnspan=2, sticky="w")
table_number_label = Label(root, text=f"TABLE : {TABLE_NUMBER}", font="Arial 18 bold", bg=root_bg_color,
                           justify="center")
table_number_label.grid(row=1, column=0, columnspan=2, sticky="w")
temp_total_label = Label()
temp_label = Label()
# scrollbar
my_scrollbar = Scrollbar(root, orient=VERTICAL)
# # listbox
my_listbox = Listbox(root, selectbackground="blue", yscrollcommand=my_scrollbar.set, selectmode=SINGLE,
                     width=18, height=18, activestyle="none")

prod_list = [
    ["8oz Rump", "16oz Rump", "8oz Gammon", "16oz Gammon", "10oz Ribeye", "24oz Mixed Grill", "PACK Back Bacon",
     "Black Pud"],
    ["8oz Steak Burger", "KG Chicken Breast", "KG Minced Beef", "KG Diced Beef", "KG C.Sausages", "6oz Wild Boar", "",
     ""],
    ["10oz Sirloin", "Whole Ham", "", "", "", "", "", "Chorizo"],
    ["KG Topside Beef", "KG Leg Lamb", "KG Pork Loin", "KG Sausage Meat", "", "", "", ""],
    ["8oz Lamb Burger", "PK Faggots", "PK Lamb Liver", "PK Minted Lamb Chops", "Duck Breast", "PK Parma Ham",
     "PK Pancetta", ""]]


class CommandButton(Button):
    def __init__(self, text, command, x, y, color=None, image=None, **kwargs):
        global TEMP_BUTTONS2
        self.text = text
        self.column = x
        self.row = y
        self.command = command
        self.color = color
        self.strip_text = str(text).replace("\n", " ")
        self.image = image
        super().__init__()
        self['image'] = self.image
        self['activebackground'] = self.color
        self['font'] = "Arial 10 bold"
        self['width'] = 12
        self['height'] = 5
        self['relief'] = RAISED
        self['bd'] = 4
        self['bg'] = self.color
        self['text'] = self.text
        self['command'] = self.command
        self.grid(row=self.row, column=self.column, sticky="nw", padx=0, pady=0, ipadx=1.5)
        if self.image is not None:
            self.configure(width=100, height=86)
        if self.text not in TEMP_BUTTONS2:
            TEMP_BUTTONS2.append(self)

    def kill(self):
        self.destroy()

    def remove_stock_label(self):
        return

    def refresh(self):
        return

    def __repr__(self):
        return self.strip_text


class LoginCommandButton(Button):
    def __init__(self, text, command, x, y, color=None, image=None, **kwargs):
        global TEMP_BUTTONS2
        self.text = text
        self.column = x
        self.row = y
        self.command = command
        self.color = color
        self.strip_text = str(text).replace("\n", " ")
        self.image = image
        super().__init__()
        self['image'] = self.image
        self['activebackground'] = self.color
        self['font'] = "Arial 10 bold"
        self['width'] = 12
        self['height'] = 5
        self['relief'] = RAISED
        self['bd'] = 4
        self['bg'] = self.color
        self['text'] = self.text
        self['command'] = self.command
        self.grid(row=self.row, column=self.column, sticky="nw", padx=0, pady=0, ipadx=1.5)
        if self.image is not None:
            self.configure(width=100, height=86)
        if self.text not in TEMP_BUTTONS2:
            TEMP_BUTTONS2.append(self)

    def kill(self):
        self.destroy()

    def remove_stock_label(self):
        return

    def refresh(self):
        return

    def __repr__(self):
        return self.strip_text


class TillButton(Button):
    def __init__(self, text, x, y, color=None, **kwargs):
        global TEMP_BUTTONS
        self.strip_text = None
        self.text = text
        self.row = y
        self.column = x
        self.strip_text = str(text).replace("\n", " ")
        self.command = lambda: [insert(self.strip_text), self.stocklabel.grid_remove(), self.refresh()]
        self.color = color
        super().__init__()
        self['activebackground'] = self.color
        self['font'] = "Arial 10 bold"
        self['width'] = 12
        self['height'] = 5
        self['relief'] = RAISED
        self['bd'] = 4
        self['bg'] = self.color
        self['text'] = self.text
        self['command'] = self.command
        self.grid(row=self.row, column=self.column, sticky="nw", padx=0, pady=0, ipadx=1.5, rowspan=2, columnspan=2)
        if self.grid is not None:
            if int(sql_retrieve_stock(self.strip_text)) >= 99:
                self.stocklabel = Label()
                self.configure(state=NORMAL)
            elif int(sql_retrieve_stock(self.strip_text)) >= 5:
                self.stocklabel = Label(text=sql_retrieve_stock(self.strip_text), bg=self.color)
                self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
                self['command'] = self.command
                self.configure(state=NORMAL)
            elif 5 > int(sql_retrieve_stock(self.strip_text)) >= 1:
                self.stocklabel = Label(text=sql_retrieve_stock(self.strip_text), bg="#f47f18")
                self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
                self['command'] = self.command
                self.configure(state=NORMAL)
            elif int(sql_retrieve_stock(self.strip_text)) == 0:
                self.stocklabel = Label(text="0", bg="red")
                self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
                self['command'] = DISABLED
                self.configure(state=DISABLED)
        if self.text not in TEMP_BUTTONS:
            TEMP_BUTTONS.append(self)

    def refresh(self):
        if int(sql_retrieve_stock(self.strip_text)) >= 99:
            self.stocklabel.grid_remove()
            self.stocklabel = Label()
            self.configure(state=NORMAL)
        elif int(sql_retrieve_stock(self.strip_text)) >= 5:
            self.stocklabel.grid_remove()
            self.stocklabel = Label(text=sql_retrieve_stock(self.strip_text), bg=self.color)
            self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
            self['command'] = self.command
            self.configure(state=NORMAL)
        elif 5 > int(sql_retrieve_stock(self.strip_text)) >= 1:
            self.stocklabel.grid_remove()
            self.stocklabel = Label(text=sql_retrieve_stock(self.strip_text), bg="#f47f18")
            self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
            self['command'] = self.command
            self.configure(state=NORMAL)
        elif int(sql_retrieve_stock(self.strip_text)) == int(0):
            self.stocklabel.grid_remove()
            self.stocklabel = Label(text="0", bg="red")
            self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
            self['command'] = DISABLED
            self.configure(state=DISABLED)
        if self.stocklabel is not None:
            self.grid_remove()
            self.grid(row=self.row, column=self.column, sticky="nw")

    def kill(self):
        self.grid_remove()
        self.stocklabel.grid_remove()

    def remove_stock_label(self):
        if self.stocklabel is not None:
            self.stocklabel.grid_remove()

    def __repr__(self):
        return self.strip_text


class TillStockButton(Button):
    def __init__(self, text, x, y, color=None, **kwargs):
        global TEMP_BUTTONS2
        self.strip_text = None
        self.text = text
        self.row = y
        self.column = x
        self.strip_text = str(text).replace("\n", " ")
        self.command = lambda: [sql_insert_stock(self.strip_text), self.stocklabel.grid_remove(), self.refresh()]
        self.color = color
        super().__init__()
        self['activebackground'] = self.color
        self['font'] = "Arial 10 bold"
        self['width'] = 12
        self['height'] = 5
        self['relief'] = RAISED
        self['bd'] = 4
        self['bg'] = self.color
        self['text'] = self.text
        self['command'] = self.command
        self.grid(row=self.row, column=self.column, sticky="nw", padx=0, pady=0, ipadx=1.5)
        if self.text not in TEMP_BUTTONS2:
            TEMP_BUTTONS2.append(self)
        if self.grid is not None:
            if int(sql_retrieve_stock(self.strip_text)) >= 1:
                self.stocklabel = Label(text=sql_retrieve_stock(self.strip_text), bg=self.color)
                self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
                self['command'] = self.command
            elif int(sql_retrieve_stock(self.strip_text)) == int(0):
                self['command'] = self.command
                self.stocklabel = Label(text="0", bg=self.color)
                self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")

    def refresh(self):
        if int(sql_retrieve_stock(self.strip_text)) >= 1:
            self.stocklabel.grid_remove()
            self.stocklabel = Label(text=sql_retrieve_stock(self.strip_text), bg=self.color)
            self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")
            self['command'] = self.command
        elif int(sql_retrieve_stock(self.strip_text)) == 0:
            self.stocklabel.grid_remove()
            self['command'] = self.command
            self.stocklabel = Label(text="0", bg=self.color)
            self.stocklabel.grid(row=self.row, column=self.column, sticky="nw")

        if self.stocklabel is not None:
            self.grid_remove()
            self.grid(row=self.row, column=self.column, sticky="nw")

    def kill(self):
        self.destroy()
        self.stocklabel.grid_remove()

    def remove_stock_label(self):
        if self.stocklabel is not None:
            self.stocklabel.grid_remove()

    def __repr__(self):
        return self.strip_text
        # return "<BtnNAME:%s>" % self.strip_text

    # def __str__(self):
    #     return "From str method of Test: a is %s" % self.strip_text


class LabelButton(Label):
    def __init__(self, text, x, y, color=None, **kwargs):
        global TEMP_BUTTONS
        self.strip_text = None
        self.text = text
        self.row = y
        self.column = x
        self.strip_text = str(text).replace("\n", " ")
        self.color = color
        super().__init__()
        self['activebackground'] = self.color
        self['font'] = "Arial 14 bold"
        self['width'] = 13
        # self['height'] = 5
        self['relief'] = RAISED
        self['bd'] = 5
        self['bg'] = self.color
        self['text'] = self.text
        self['justify'] = LEFT
        self.grid(row=self.row, column=self.column, ipadx=0, ipady=0, sticky="nw", columnspan=10, rowspan=10)
        if self.text not in TEMP_LABEL:
            TEMP_LABEL.append(self)

    def refresh(self):
        self.grid_remove()
        self.grid(row=self.row, column=self.column, sticky="nw")

    def kill(self):
        self.destroy()

    def remove_stock_label(self):
        return

    def __repr__(self):
        return self.strip_text

    # def __str__(self):
    #     return "From str method of Test: a is %s" % self.strip_text


class MyFrame(Frame):
    def __init__(self, x, y, width, height, color=None, **kwargs):
        self.row = y
        self.column = x
        self.color = color
        self.width = width
        self.height = height
        self.color = color
        super().__init__()
        # self['activebackground'] = self.color
        self['width'] = self.width
        self['height'] = self.height
        self['relief'] = RAISED
        self['bd'] = 5
        self['bg'] = self.color
        if self not in TEMP_FRAME:
            TEMP_FRAME.append(self)
        self.place(x=self.column, y=self.row)

    def refresh(self):
        return

    def kill(self):
        self.destroy()

    def remove_stock_label(self):
        return

    def __repr__(self):
        return self


def generate_unique_ref_number(membid, tabid, amountid):  # to be printed on paid bills : TBHP-date-memberID-tableID-ammountPaid
    random_int = random.randrange(111111, 999999, 1)
    todays_date = datetime.now().strftime("%Y%m%d")
    return f'TBHP-{todays_date}-{membid}-{tabid}-{amountid}-{random_int}'


def open_it():
    global DRAWER_PORT, OPEN_IT
    if OPEN_IT:
        if DRAWER_PORT:
            os.system(f"ECHO>{DRAWER_PORT}")
        else:
            print("port faulty")


def extras():
    global MEMBER_ID, TABLE_NUMBER, my_listbox, TEMP_BUTTONS

    if my_listbox.get(ANCHOR) and my_listbox.curselection() != ():
        item = my_listbox.get(ANCHOR)
        item = (str(item).split("                                                      "))
        xtra_frame = MyFrame(0, 0, WIDTH, HEIGHT, "#98dff5")
        xtra_frame.place(x=340, y=0, width=WIDTH - 340, height=HEIGHT)
        Button(xtra_frame, text="X", font="Arial 12 bold", bg="red").place(x=630, y=20)

        def xtra_commands(name, price):
            cursor.execute(
                "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                [str(item[0]), str(item[1]), MEMBER_ID, TABLE_NUMBER, '*' + name, "IN BASKET", time_now()])

            a_index = (my_listbox.get(0, END).index(my_listbox.get(ANCHOR)))
            my_listbox.insert(a_index + 1, f" *{name}")

            sql_insert = "INSERT INTO `basket`(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) VALUES (%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_insert, ('*' + name, price, MEMBER_ID, TABLE_NUMBER, time_now(), "IN BASKET"))
            calculate_total()
            temp_button.destroy()
            xtra_frame.destroy()

        list_of_extras = [("1 ADD CHIPS", "1.50"), ("1 ADD CHEDDAR", "1.00"), ("1 ADD STILTON", "1.00"),
                          ("1 ADD BACON", "0.75"),
                          ("1 ADD TOMATO", "0.75"), ("1 ADD MUSHROOM", "0.75"), ("1 ADD SAUSAGE", "1.00"),
                          ("1 ADD BLACK PUD", "0.75"), ("1 ADD HASH BROWN", "0.75"), ("1 ADD BAKED BEANS", "0.75"),
                          ("1 ADD FRIED BREAD", "0.75")]
        tfs = 14
        ths = 65
        tys = 65
        b0 = Button(xtra_frame, text=f"{list_of_extras[0][0]}",
                    command=lambda: [xtra_commands(list_of_extras[0][0], list_of_extras[0][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 0, width=94 * 3, height=ths)
        b1 = Button(xtra_frame, text=f"{list_of_extras[1][0]}",
                    command=lambda: [xtra_commands(list_of_extras[1][0], list_of_extras[1][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold", bg="#f7fc87").place(x=50, y=tys * 1, width=94 * 3, height=ths)
        b2 = Button(xtra_frame, text=f"{list_of_extras[2][0]}",
                    command=lambda: [xtra_commands(list_of_extras[2][0], list_of_extras[2][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold", bg="#bfe171").place(x=50, y=tys * 2, width=94 * 3, height=ths)
        b3 = Button(xtra_frame, text=f"{list_of_extras[3][0]}",
                    command=lambda: [xtra_commands(list_of_extras[3][0], list_of_extras[3][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 3, width=94 * 3, height=ths)
        b4 = Button(xtra_frame, text=f"{list_of_extras[4][0]}",
                    command=lambda: [xtra_commands(list_of_extras[4][0], list_of_extras[4][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 4, width=94 * 3, height=ths)
        b5 = Button(xtra_frame, text=f"{list_of_extras[5][0]}",
                    command=lambda: [xtra_commands(list_of_extras[5][0], list_of_extras[5][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 5, width=94 * 3, height=ths)
        b6 = Button(xtra_frame, text=f"{list_of_extras[6][0]}",
                    command=lambda: [xtra_commands(list_of_extras[6][0], list_of_extras[6][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 6, width=94 * 3, height=ths)
        b7 = Button(xtra_frame, text=f"{list_of_extras[7][0]}",
                    command=lambda: [xtra_commands(list_of_extras[7][0], list_of_extras[7][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold", bg="#1d2d40").place(x=50, y=tys * 7, width=94 * 3, height=ths)
        b8 = Button(xtra_frame, text=f"{list_of_extras[8][0]}",
                    command=lambda: [xtra_commands(list_of_extras[8][0], list_of_extras[8][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 8, width=94 * 3, height=ths)
        b9 = Button(xtra_frame, text=f"{list_of_extras[9][0]}",
                    command=lambda: [xtra_commands(list_of_extras[9][0], list_of_extras[9][1])], bd=5, relief=RAISED,
                    font=f"Arial {tfs} bold").place(x=50, y=tys * 9, width=94 * 3, height=ths)
        b10 = Button(xtra_frame, text=f"{list_of_extras[10][0]}",
                     command=lambda: [xtra_commands(list_of_extras[10][0], list_of_extras[10][1])], bd=5, relief=RAISED,
                     font=f"Arial {tfs} bold").place(x=50, y=tys * 10, width=94 * 3, height=ths)
        temp_button = CommandButton("Done!", lambda: [temp_button.destroy(), xtra_frame.destroy()], 0, 0, "lightgreen")
        temp_button.configure(bd=5, relief=RAISED, font="Arial 14 bold")
        temp_button.place(x=700, y=300, width=200, height=200)
        TEMP_BUTTONS.append(xtra_frame)
        TEMP_BUTTONS.append(temp_button)


def check_tables():
    global TABLE_NUMBER

    def remove_items():
        temp_listbox.destroy()
        temp_scrollbar.destroy()
        temp_frame.destroy()
        xtemp_frame.destroy()

    def callback(event):
        global TABLE_NUMBER
        root.unbind(callback)
        item = temp_listbox.get(ANCHOR)
        item_number = str(item).replace("TABLE: ", "")
        if item_number == "":
            item_number = 0
        elif item_number == "No ACTIVE Tables!":
            item_number = 0
        TABLE_NUMBER = item_number
        resume_basket()
        # temp2.destroy()
        calculate_total()
        temp_frame.destroy()
        xtemp_frame.destroy()

    xtemp_frame = MyFrame(0, 0, WIDTH, HEIGHT, "#568695")
    xtemp_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)

    temp_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    temp_frame.place(x=200, y=50, width=WIDTH / 2, height=HEIGHT - 100)

    temp_scrollbar = Scrollbar(temp_frame, orient=VERTICAL)
    temp_listbox = Listbox(temp_frame, selectbackground="blue", yscrollcommand=temp_scrollbar.set, selectmode=SINGLE,
                           activestyle="none", width=19)
    temp_listbox.grid(row=0, column=0, sticky="nw", ipady=92)
    temp_scrollbar.config(command=temp_listbox.yview)
    temp_scrollbar.grid(row=0, column=1, sticky="ne", ipady=303, ipadx=30)
    temp_listbox.grid_propagate(0)
    temp_listbox.propagate(0)
    temp_listbox.configure(font="Arial 30 bold", bg=root_bg_color, justify="center")

    temp_listbox.bind("<<ListboxSelect>>", callback)
    cursor.execute("SELECT DISTINCT table_id FROM basket")
    results = cursor.fetchall()
    temp_list = []
    for row in results:
        temp_list.append(int(row[0]))
    for row in sorted(temp_list):
        temp_listbox.insert(END, f"TABLE: {row}")
    if len(results) < 1:
        temp_listbox.insert(END, "No ACTIVE Tables!")


def return_member_name():
    global MEMBER_ID
    sql_member = f"SELECT `member_name` FROM `members` WHERE `member_id` = %s"
    cursor.execute(sql_member, str(MEMBER_ID))
    results = cursor.fetchall()
    return str(results[0][0])


def return_member_namee(value):
    global MEMBER_ID
    cursor.execute("SELECT `member_id`, `member_name` FROM `members` WHERE `member_id` = %s", [value])
    results = cursor.fetchall()
    for row in results:
        return str(row[1])


def time_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def user_is_inactive():
    global TEMP_BUTTONS, SCREENSAVER_TIMER
    clear()
    clear_cmd()
    clear_frame()
    clear_LABEL()
    bitch_clear()
    login()


def till_is_inactive():
    global TEMP_BUTTONS
    clear()
    clear_cmd()
    clear_frame()
    clear_LABEL()
    bitch_clear()
    screen_log()


def goToLogin(event=None):
    global screen_logo
    login()
    reset_timer()


def check_if_doneness(name):
    cursor.execute("SELECT doneness FROM `command_buttons` WHERE text = %s", [name])
    results = cursor.fetchall()
    if "ON" in results[0]:
        return True


def check_what_measure(name):
    cursor.execute("SELECT measure FROM `command_buttons` WHERE text = %s", [name])
    results = cursor.fetchall()
    return results[0][0]


def check_if_submenu(event):
    cursor.execute("Select * from submenu")
    results = cursor.fetchall()
    for row in range(len(results)):
        if str(event.widget['text']).replace("\n", " ") == results[row][0]:
            return True


def check_if_measure(name):
    cursor.execute("SELECT measure FROM `command_buttons` WHERE text = %s", [name])
    results = cursor.fetchall()
    if len(results) > 0:
        if str(results[0][0]) != "None":
            return True


def type_of_measure(name):
    cursor.execute("SELECT measure FROM `command_buttons` WHERE text = %s", [name])
    results = cursor.fetchall()
    return results[0][0]


def pressed_reset(event=None):
    global waiting_timer, a_frame, MEMBER_ID, TABLE_NUMBER, my_listbox, TEMP_BUTTONS
    if waiting_timer:
        root.after_cancel(waiting_timer)
        waiting_timer = None
        # popup with mods
        textzzzz = str(event.widget.__repr__())
        textzzz = textzzzz.split(" ")
        produx = ""
        for i in range(len(textzzz)):
            if len(textzzz) == 1:
                produx += textzzz[i]
            elif len(textzzz) > 1:
                produx += textzzz[i] + " "
        cursor.execute('SELECT text,doneness FROM command_buttons WHERE text = %s', [str(produx)])
        reszults = cursor.fetchall()
        if str(produx) == "BURGER":
            grab_burgers(event)
            cursor.execute(f"DELETE FROM basket WHERE product = 'BURGER' ORDER BY datez DESC LIMIT 1 ")
            my_listbox.delete(END)
        elif str(produx) == "KID ROAST ":
            grab_kid_roast(event)
            cursor.execute(f"DELETE FROM basket WHERE product = 'KID ROAST' ORDER BY datez DESC LIMIT 1 ")
            my_listbox.delete(END)
        elif str(produx) == "CIABATTAS":
            grab_ciabatta(event)
            cursor.execute(f"DELETE FROM basket WHERE product = 'CIABATTAS' ORDER BY datez DESC LIMIT 1")
            my_listbox.delete(END)
        elif str(produx) == "BREAKFAST BAP ":
            item = my_listbox.get(END)
            cursor.execute(f"DELETE FROM basket WHERE product = 'BREAKFAST BAP' ORDER BY datez DESC LIMIT 1")
            my_listbox.delete(END)
            grab_bap(event)
        elif str(produx) == "ICE CREAMS ":
            item = my_listbox.get(END)
            cursor.execute(f"DELETE FROM basket WHERE product = 'ICE CREAMS' ORDER BY datez DESC LIMIT 1")
            my_listbox.delete(END)
            grab_icecream(event)
        elif str(produx).startswith("KIDS"):
            item = my_listbox.get(END)
            item_pass0 = str(item).split("                                                      ")
            if len(item_pass0) > 1:
                cursor.execute(f"DELETE FROM basket WHERE item_id = %s ORDER BY datez DESC LIMIT 1 ",
                               [str(item_pass0[1])])
                mod_stock(item_pass0[0], +1)
                my_listbox.delete(END)
                grab_kids_choice_sides(event, item)
        elif check_if_measure(produx) is True:
            name = produx
            item = my_listbox.get(END)
            item_pass0 = str(item).split("                                                      ")
            if len(item_pass0) > 1:
                cursor.execute(f"DELETE FROM basket WHERE item_id = %s ORDER BY datez DESC LIMIT 1 ",
                               [str(item_pass0[1])])
            my_listbox.delete(END)
            if check_if_measure(name) is True:

                mod_stock(name, -1)
                mod_frame = MyFrame(342, 95, 683, 480, "lightgrey")
                mod_frame.configure(relief=RAISED)
                if type_of_measure(name) == "half/pint":  # x1 / 2,  x1
                    def set_msg(name2):
                        if str(v1.get()) == "1":  # full price
                            temp_name2 = str('PINT ' + str(name2))
                            insert_with_price(temp_name2, get_price(name))

                        elif str(v1.get()) == "0":
                            temp_name2 = str('HALF ' + str(name2))
                            temp_price2 = round(float(float(get_price(name)) / 2), 2)
                            insert_with_price(temp_name2, temp_price2)

                        calculate_total()
                        resume_basket()
                        mod_frame.destroy()

                    measure_size3 = [("HALF", 0), ("PINT", 1)]
                    v1 = IntVar()
                    counter = 25
                    for var1, val1 in measure_size3:
                        choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
                                              value=val1, selectcolor="#e47831", font="Arial 20 bold",
                                              command=lambda: [set_msg(name)])
                        choice1.place(x=200, y=counter * 4, width=300, height=150)
                        choice1.deselect()
                        counter += 50

                elif type_of_measure(name) == "25ml/50ml":  # x1 or x2 price
                    def set_msg(name3):
                        if str(v1.get()) == "1":
                            temp_name2 = str('DOUBLE ' + str(name3))
                            temp_price2 = round(float(float(get_price(name)) * 2), 2)
                            insert_with_price(temp_name2, temp_price2)

                        elif str(v1.get()) == "0":
                            temp_name3 = str('SINGLE ' + str(name3))
                            insert_with_price(temp_name3, get_price(name))
                        resume_basket()
                        mod_frame.destroy()

                    measure_size = [("25ml", 0), ("50ml", 1)]
                    v1 = IntVar()
                    counter = 25
                    for var1, val1 in measure_size:
                        choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
                                              value=val1, selectcolor="#e47831", font="Arial 20 bold",
                                              command=lambda: [set_msg(name)])
                        choice1.place(x=200, y=counter * 4, width=300, height=150)
                        choice1.deselect()
                        counter += 50

                elif type_of_measure(name) == "125/175/250/btl":  # x1, x1+2£, x1+4£, x1+10£
                    def set_msg(name4):
                        if str(v1.get()) == "0":
                            temp_name4 = str('125ML ' + str(name4))
                            insert_with_price(temp_name4, get_price(name4))
                        elif str(v1.get()) == "1":
                            temp_name5 = str('175ML ' + str(name4))
                            temp_price5 = round(float(float(get_price(name4)) + 2), 2)
                            insert_with_price(temp_name5, temp_price5)
                        elif str(v1.get()) == "2":
                            temp_name6 = str('250ML ' + str(name4))
                            temp_price6 = round(float(float(get_price(name4)) + 4), 2)
                            insert_with_price(temp_name6, temp_price6)
                        elif str(v1.get()) == "3":
                            temp_name7 = str('BTL ' + str(name4))
                            temp_price7 = round(float(float(get_price(name4)) + 12), 2)
                            insert_with_price(temp_name7, temp_price7)
                        calculate_total()
                        mod_frame.destroy()

                    measure_size2 = [("125ml", 0), ("175ml", 1), ("250ml", 2), ("BTL", 3)]
                    v1 = IntVar()
                    counter = 25
                    for var1, val1 in measure_size2:
                        choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
                                              value=val1, selectcolor="#e47831", font="Arial 20 bold",
                                              command=lambda: [set_msg(name)])
                        choice1.place(x=200, y=counter * 2, width=300, height=80)
                        choice1.deselect()
                        counter += 50

        elif len(reszults) > 0 and "ON" in reszults[0]:
            item = my_listbox.get(END)
            item_pass0 = str(item).split("                                                      ")
            item_name = item_pass0[0]
            item_id = item_pass0[1]
            mod_frame = MyFrame(340, 95, 685, 485, "lightgrey")
            v1 = IntVar()

            def set_msg(item_name, item_id):
                global MEMBER_ID, TABLE_NUMBER, my_listbox
                message = f"*{doneness[v1.get()][0]}".replace("\n", " ")
                cursor.execute(
                    "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    [str(item_name), item_id, MEMBER_ID, TABLE_NUMBER, message, "IN BASKET", time_now()])
                mod_frame.destroy()
                my_listbox.insert(END,
                                  " " + message + "                                                      " + item_id)

            doneness = [("BLUE", 0), ("RARE", 1), ("MR", 2), ("MED", 3), ("MW", 4), ("WD", 5)]

            counter = 10
            for var1, val1 in doneness:
                choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
                                      value=val1,
                                      selectcolor="#e47831", font="Arial 10 bold",
                                      command=lambda: [set_msg(item_name, item_id)])
                choice1.place(x=50, y=counter * 1.5, width=120, height=75)
                choice1.deselect()
                counter += 50
            counter = 10


def calculate_icecream():
    global icecream, icecream_buttons, icecream_frame, MEMBER_ID, TABLE_NUMBER
    icecream_buttons_clear()
    price = float()
    classic = ["VANILLA", "CHOCOLATE", "STRAWBERRY"]
    luxury = ["HONEYCOMB", "SALTED CARAMEL", "FUNKY BANANA", "PISTACHIO", "COOKIE DOUGH", "RHUBARB", "RUM&RAISIN",
              "MINT CHOC", "MANGO SORBET", "RASPBERRY SORBET", "LEMON SORBET"]
    for ic in icecream:
        if ic in classic:
            price += 1.95
        elif ic in luxury:
            price += 2.25

    sql_insert = "INSERT INTO `basket`(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql_insert, ("ICE CREAMS", price, MEMBER_ID, TABLE_NUMBER, time_now(), "IN BASKET"))
    cursor.execute("SELECT product, item_id FROM `basket` ORDER BY `datez` DESC LIMIT 1")
    res = cursor.fetchall()
    my_listbox.insert(END,
                      str("ICE CREAMS") + "                                                      " + str(res[0][1]))

    if len(icecream) > 0:
        for ic in icecream:
            cursor.execute(
                "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                ["ICE CREAMS", str(res[0][1]), MEMBER_ID, TABLE_NUMBER, '*' + ic, "IN BASKET", time_now()])
            my_listbox.insert(END,
                              f" *{ic}" + "                                                      " + str(res[0][1]))

    icecream.clear()
    calculate_total()


def grab_icecream(event):
    global MEMBER_ID, TABLE_NUMBER, icecream_frame, icecream_buttons
    if str(event.widget['text']).replace("\n", " ") == "ICE CREAMS":
        icecream_frame = MyFrame(340, 0, 685, 900, "lightgrey")
        close_button = Button(icecream_frame, text=" X ", bg="#FD4040", command=lambda: [icecream_frame.destroy()])
        close_button.place(x=600, y=10, width=50, height=50)
        flavours = ["VANILLA", "CHOCOLATE", "STRAWBERRY", "HONEYCOMB", "SALTED CARAMEL", "FUNKY BANANA", "PISTACHIO",
                    "COOKIE DOUGH", "RHUBARB", "RUM&RAISIN", "MINT CHOC", "MANGO SORBET", "RASPBERRY SORBET",
                    "LEMON SORBET"]
        f1 = StringVar()

        counter = 10

        def show_chices1(counter):
            global icecream_frame, icecream_buttons
            for var1 in flavours:
                choice1 = Radiobutton(icecream_frame, text=var1, indicatoron=0, width=20, padx=20, variable=f1,
                                      value=var1,
                                      selectcolor="#e47831", font="Arial 10 bold",
                                      command=lambda: [icecream.append(f1.get()), icecream_frame.destroy(),
                                                       calculate_icecream()])

                choice1.place(x=300, y=counter * 1.05, width=200, height=50)
                choice1.deselect()

                counter += 50
            counter = 10

        def show_chices2(counter):
            global icecream_frame, icecream_buttons
            for var1 in flavours:
                choice1 = Radiobutton(icecream_frame, text=var1, indicatoron=0, width=20, padx=20, variable=f1,
                                      value=var1,
                                      selectcolor="#e47831", font="Arial 10 bold",
                                      command=lambda: [icecream.append(f1.get()), choice1.destroy(),
                                                       icecream_buttons_clear(), show_chices1(counter)])
                choice1.place(x=200, y=counter * 1.05, width=200, height=50)
                choice1.deselect()
                icecream_buttons.append(choice1)
                counter += 50
            counter = 10

        def show_chices3(counter):
            global icecream_frame, icecream_buttons
            for var1 in flavours:
                choice1 = Radiobutton(icecream_frame, text=var1, indicatoron=0, width=20, padx=20, variable=f1,
                                      value=var1,
                                      selectcolor="#e47831", font="Arial 10 bold",
                                      command=lambda: [icecream.append(f1.get()), icecream_buttons_clear(),
                                                       show_chices2(counter)])
                choice1.place(x=100, y=counter * 1.05, width=200, height=50)
                choice1.deselect()
                icecream_buttons.append(choice1)
                counter += 50
            counter = 10

        # def price1scoop():
        #     global icecream_frame
        #     counter = 1
        #     scoop1.destroy(), scoop2.destroy(), scoop3.destroy()
        #     for flav in flavours:
        #         def create_button(frame, flav, counter, y=50*counter):
        #             global icecream_frame, icecream
        #             exec(f"Button({frame}, text='{flav}', command=lambda: [icecream.append('{flav}'), icecream_frame.destroy(),calculate_icecream()], font='Arial 12 bold').place(x=100, y=int(y), width=200)")
        #
        #         create_button('icecream_frame', flav, counter)
        #         counter += 1
        #
        #
        #
        # def price2scoop():
        #     global icecream_frame
        #     counter = 1
        #     scoop1.destroy(), scoop2.destroy(), scoop3.destroy()
        #     if 1 == 1:
        #         for flav in flavours:
        #             def create_button(frame, flav, counter, y=50 * counter):
        #                 global icecream_frame, icecream
        #
        #                 exec(f"Button({frame}, text='{flav}', command=lambda: [icecream.append('{flav}'), icecream_frame.destroy(), calculate_icecream()], font='Arial 12 bold').place(x=100, y=int(y), width=200)")
        #
        #             create_button('icecream_frame', flav, counter)
        #             counter += 1
        #
        #
        # def price3scoop():
        #     return
        counter = 10
        scoop1 = Button(icecream_frame, text="1 SCOOP",
                        command=lambda: [show_chices1(counter), scoop1.destroy(), scoop2.destroy(), scoop3.destroy()],
                        font="Arial 12 bold")
        scoop2 = Button(icecream_frame, text="2 SCOOP",
                        command=lambda: [show_chices2(counter), scoop1.destroy(), scoop2.destroy(), scoop3.destroy()],
                        font="Arial 12 bold")
        scoop3 = Button(icecream_frame, text="3 SCOOP",
                        command=lambda: [show_chices3(counter), scoop1.destroy(), scoop2.destroy(), scoop3.destroy()],
                        font="Arial 12 bold")

        scoop1.place(x=50, y=200, width=200, height=85)
        scoop2.place(x=50, y=300, width=200, height=85)
        scoop3.place(x=50, y=400, width=200, height=85)


def grab_kids_choice_sides(event, item):
    if str(event.widget['text']).replace("\n", " ").startswith("KIDS"):
        mod_frame = MyFrame(340, 0, 685, 900, "lightgrey")
        kids_item = item

        def set_msg1(item_pass1):
            global MEMBER_ID, TABLE_NUMBER, my_listbox
            optfirst = opt1[v1.get()][0]

            def set_msg2(item_pass2):
                global MEMBER_ID, TABLE_NUMBER, my_listbox
                item_pass3 = str(item_pass2).split("                                                      ")

                insert(item_pass3[0])

                optfirst = opt1[v1.get()][0]
                optsecond = opt2[v2.get()][0]
                message = "*" + optfirst + "+" + optsecond
                cursor.execute("SELECT item_id FROM `basket` ORDER BY `basket`.`datez` DESC LIMIT 1")
                item_id = cursor.fetchall()
                # message = str(message) + str(item_id[0][0])
                cursor.execute(
                    "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    [str(event.widget['text']).replace("\n", " "), item_id[0][0], MEMBER_ID, TABLE_NUMBER, message,
                     "IN BASKET", time_now()])

                my_listbox.insert(END, f" {message}")

            mod_frame = MyFrame(340, 0, 685, 900, "lightgrey")

            opt2 = [("NONE", 0), ("SALAD", 1), ("CUC", 2), ("BEANS", 3)]
            v2 = IntVar()
            counter = 10
            for var2, val2 in opt2:
                choice1 = Radiobutton(mod_frame, text=var2, indicatoron=0, width=20, padx=20, variable=v2,
                                      value=val2,
                                      selectcolor="#e47831", font="Arial 10 bold",
                                      command=lambda: [set_msg2(item_pass1), mod_frame.destroy()])
                choice1.place(x=200, y=200 + (counter * 1.6), width=200, height=80)
                choice1.deselect()
                counter += 50
            counter = 10

        opt1 = [("NONE", 0), ("CHIPS", 1), ("NEW POTS", 2)]
        v1 = IntVar()
        counter = 10
        for var1, val1 in opt1:
            choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
                                  value=val1,
                                  selectcolor="#e47831", font="Arial 10 bold",
                                  command=lambda: [set_msg1(kids_item), mod_frame.destroy()])
            choice1.place(x=100, y=200 + (counter * 1.6), width=200, height=80)
            choice1.deselect()
            counter += 50
        counter = 10


def grab_bap(event):
    if str(event.widget['text']).replace("\n", " ") == "BREAKFAST BAP":
        mod_frame = MyFrame(340, 0, 685, 900, "lightgrey")

        def set_msg1():
            global MEMBER_ID, TABLE_NUMBER, my_listbox
            optfirst = opt1[v1.get()][0]

            def set_msg2():
                global MEMBER_ID, TABLE_NUMBER, my_listbox
                insert("BREAKFAST BAP")
                optfirst = opt1[v1.get()][0]
                optsecond = opt2[v2.get()][0]
                message = f"{optfirst}+{optsecond}"
                cursor.execute("SELECT item_id FROM `basket` ORDER BY `basket`.`datez` DESC LIMIT 1")
                item_id = cursor.fetchall()
                cursor.execute(
                    "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    [str(event.widget['text']).replace("\n", " "), item_id[0][0], MEMBER_ID, TABLE_NUMBER, message,
                     "IN BASKET", time_now()])

                my_listbox.insert(END, f" *{message}")

            mod_frame = MyFrame(340, 0, 685, 900, "lightgrey")

            opt2 = [("BACON", 0), ("SAUSAGE", 1), ("MUSH", 2), ("TOMATO", 3), ("EGG", 4), ("BLACK PUD", 5),
                    ("HASH BROWN", 6), ("VEG SAUSAGE", 7), ("B.BEANS", 8)]
            v2 = IntVar()
            counter = 10
            for var2, val2 in opt2:
                choice1 = Radiobutton(mod_frame, text=var2, indicatoron=0, width=20, padx=20, variable=v2,
                                      value=val2,
                                      selectcolor="#e47831", font="Arial 10 bold",
                                      command=lambda: [set_msg2(), mod_frame.destroy()])
                choice1.place(x=200, y=counter * 1.6, width=200, height=80)
                choice1.deselect()
                counter += 50
            counter = 10

        opt1 = [("BACON", 0), ("SAUSAGE", 1), ("MUSH", 2), ("TOMATO", 3), ("EGG", 4), ("BLACK PUD", 5),
                ("HASH BROWN", 6), ("VEG SAUSAGE", 7), ("B.BEANS", 8)]
        v1 = IntVar()
        counter = 10
        for var1, val1 in opt1:
            choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
                                  value=val1,
                                  selectcolor="#e47831", font="Arial 10 bold",
                                  command=lambda: [set_msg1(), mod_frame.destroy()])
            choice1.place(x=100, y=counter * 1.6, width=200, height=80)
            choice1.deselect()
            counter += 50
        counter = 10


def grab_ciabatta(event):
    if str(event.widget['text']).replace("\n", " ") == "CIABATTAS":
        clear()
        cursor.execute("SELECT * FROM command_buttons WHERE text LIKE %s", ["CIABATTA %"])
        the_temp_results = cursor.fetchall()
        counter = 0
        counter = 0
        button_status = "ciabatta"
        for temp_results in the_temp_results:
            counter += 1

            def placez_button(counter):
                global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
                button_name = str(button_status) + f"{counter}"
                button_name = TillButton(str(temp_results[2]).replace(' ', '\n'), temp_results[4], temp_results[5],
                                         temp_results[6])

            placez_button(counter)


def grab_kid_roast(event):
    clear()
    cursor.execute("SELECT * FROM command_buttons WHERE button_status = %s", ['screen10.1'])
    temp_results = cursor.fetchall()
    counter = 0
    button_status = "burger"
    for temp_results in temp_results:
        counter += 1

        def placez_button(counter):
            global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
            button_name = str(button_status) + f"{counter}"
            button_name = TillButton(str(temp_results[2]).replace(' ', '\n'), temp_results[4], temp_results[5],
                                     temp_results[6])

        placez_button(counter)


def grab_burgers(event):
    if str(event.widget['text']).replace("\n", " ") == "BURGER":
        item = str(event.widget['text']).replace("\n", " ")
        clear()
        cursor.execute("SELECT * FROM command_buttons WHERE text LIKE %s", [f"% {item}"])
        the_temp_results = cursor.fetchall()
        counter = 0
        button_status = "burger"
        for temp_results in the_temp_results:
            counter += 1

            def placez_button(counter):
                global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
                button_name = str(button_status) + f"{counter}"
                button_name = TillButton(str(temp_results[2]).replace(' ', '\n'), temp_results[4], temp_results[5],
                                         temp_results[6])

            placez_button(counter)


def pressed(event):
    global waiting_timer, a_frame

    def do_this():  # bring up edit button
        global waiting_timer, a_frame, TEMP_BUTTONS

        if str(event.widget).startswith(".!tillbutton"):
            def update_me(item, qty, price, color):
                #  check if other button is there
                cursor.execute(
                    "SELECT button_status,x,y,text FROM command_buttons WHERE (button_status,x,y) = (%s,%s,%s)",
                    [xy_results[0][2], e7.get(), e8.get()])
                resultss = cursor.fetchall()
                if len(resultss) > 0 and (results[0][0] != resultss[0][3]):
                    answer = messagebox.showwarning("Button query!",
                                                    message="Another button is already there. \nPlease pick another spot.")
                else:
                    # update it
                    cursor.execute(
                        "UPDATE command_buttons SET text=%s, color=%s, x=%s, y=%s, doneness=%s, measure=%s WHERE text = %s",
                        [e1.get(), color, e7.get(), e8.get(), doneness1.get(), e12.get(), item])
                    cursor.execute(
                        "UPDATE stock SET item = %s, qty = %s, price = %s, belongs_to = %s WHERE (item, qty, price) = (%s,%s,%s)",
                        [e1.get(), e3.get(), e4.get(), e10.get(), item, qty, price])
                    messagebox.showwarning(title="Action completed.", message="Button updated.")
                    a_frame.destroy()
                    clear()

            def delete_me():
                cursor.execute("DELETE FROM command_buttons WHERE text = %s", [results[0][0]])
                cursor.execute("DELETE FROM stock WHERE item = %s", [results[0][0]])
                messagebox.showwarning(title="Action completed.", message="Button successfully deleted.")
                a_frame.destroy()
                clear()

            def create_new():
                # check first
                cursor.execute("SELECT text FROM command_buttons WHERE text = %s", [e1.get()])
                resultsss = cursor.fetchall()
                if len(resultsss) > 0:
                    messagebox.showwarning(title="Action canceled.", message="Button name exists.")
                else:
                    cursor.execute(
                        "SELECT button_status,x,y,text FROM command_buttons WHERE (button_status,x,y) = (%s,%s,%s)",
                        [xy_results[0][2], e7.get(), e8.get()])
                    resultssss = cursor.fetchall()
                    if len(resultssss) > 0:
                        answer = messagebox.showwarning("Button query!",
                                                        message="Another button is already there. \nPlease pick another spot.")
                    else:
                        # # create it
                        cursor.execute(
                            "INSERT INTO command_buttons(button_status, text, x, y, color, icon, doneness, measure) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                            [xy_results[0][2], e1.get(), e7.get(), e8.get(), e2['bg'], "", doneness1.get(), e12.get()])
                        cursor.execute("INSERT INTO stock(item, qty, price, belongs_to) VALUES (%s,%s,%s,%s)",
                                       [e1.get(), e3.get(), e4.get(), e10.get()])
                        messagebox.showinfo(title="Button query!", message="Button successfully created!")
                        a_frame.destroy()
                        clear()

            def pick_color():
                color = colorchooser.askcolor(color=e2['bg'], title="Pick color")
                e2['bg'] = color[1]

            a_frame = MyFrame(300, 50, 750, 750, "lightgrey")
            waiting_timer = None
            cursor.execute("SELECT item, qty, price, belongs_to FROM stock WHERE item = %s",
                           [str(event.widget['text']).replace("\n", " ")])
            results = cursor.fetchall()
            cursor.execute("SELECT x,y,button_status,doneness,measure FROM command_buttons WHERE text = %s",
                           [str(event.widget['text']).replace("\n", " ")])
            xy_results = cursor.fetchall()
            close_cfg = Button(a_frame, text="X", command=lambda: a_frame.destroy(), bd=5, relief=RAISED)
            close_cfg.place(x=700 - 35, y=2, width=50)

            e1 = Entry(a_frame, justify=CENTER, relief=RAISED, bd=2, font="Arial 12 bold")
            e1.place(x=110, y=20, width=150, height=50)

            e1info = Message(a_frame, text="BUTTON\nNAME:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=10, y=20, width=100, height=50)
            e2 = Button(a_frame, text=event.widget['bg'], bg=event.widget['bg'], command=pick_color, bd=2,
                        font="Arial 12 bold")
            e2.place(x=110, y=70, width=100, height=50)
            e2info = Message(a_frame, text="BUTTON\nCOLOR:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=10, y=70, width=100, height=50)
            e3 = Entry(a_frame, justify=CENTER, relief=RAISED, bd=2, font="Arial 12 bold")
            e3.place(x=110, y=120, width=100, height=50)
            e3info = Message(a_frame, text="BUTTON\nSTOCK:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=10, y=120, width=100, height=50)
            e4 = Entry(a_frame, justify=CENTER, relief=RAISED, bd=2, font="Arial 12 bold")
            e4.place(x=110, y=170, width=100, height=50)
            e4info = Message(a_frame, text="BUTTON\nPRICE:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=10, y=170, width=100, height=50)

            e5 = Button(a_frame, text="UPDATE", bd=4, bg="lightgreen", font="Arial 12 bold",
                        command=lambda: update_me(results[0][0], results[0][1], results[0][2], e2['bg']))
            e5.place(x=300, y=20, width=100, height=50)
            e6 = Button(a_frame, text="DELETE", bd=4, bg="#ff5454", font="Arial 12 bold", command=lambda: delete_me())
            e6.place(x=400, y=20, width=100, height=50)
            e9 = Button(a_frame, text="CREATE\nNEW", bd=4, bg="#f7ea00", font="Arial 12 bold",
                        command=lambda: create_new())
            e9.place(x=500, y=20, width=100, height=50)

            e7 = StringVar(a_frame)
            e7.set(xy_results[0][0])
            e7opts = OptionMenu(a_frame, e7, "4", "5", "6", "7", "8")
            e7opts.place(x=110, y=220, width=100, height=50)
            e7opts.config(font="Arial 15 bold")
            e7info = Message(a_frame, text="BUTTON\nX:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=10, y=220, width=100, height=50)
            e8 = StringVar(a_frame)
            e8.set(xy_results[0][1])
            e8opts = OptionMenu(a_frame, e8, "1", "2", "3", "4", "5")
            e8opts.place(x=110, y=270, width=100, height=50)
            e8opts.config(font="Arial 15 bold")
            e8info = Message(a_frame, text="BUTTON\nY:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=10, y=270, width=100, height=50)

            e10 = StringVar(a_frame)
            e10.set(results[0][3])
            e10opts = OptionMenu(a_frame, e10, "BAR", "STARTER", "MAIN", "SIDE", "PUD")
            e10opts.place(x=110, y=320, width=100, height=50)
            e10opts.config(font="Arial 15 bold")
            e10info = Message(a_frame, text="STOCK\nPLACE:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                              font="Arial 10 bold").place(x=10, y=320, width=100, height=50)

            def selected():
                print(doneness1.get())

            doneness1 = StringVar()
            e11opts = Checkbutton(a_frame, text="DONENESS", variable=doneness1, onvalue="ON", offvalue="OFF",
                                  command=selected, width=26)
            if check_if_doneness(results[0][0]):
                e11opts.select()
            elif not check_if_doneness(results[0][0]):
                e11opts.deselect()
            e11opts.place(x=300, y=320, height=50)
            e11opts.config(font="Arial 15 bold", bd=4, relief=RAISED)

            e12 = StringVar(a_frame)
            e12.set(xy_results[0][4])
            e12opts = OptionMenu(a_frame, e12, "None", "25ml/50ml", "125/175/250/btl", "half/pint")
            e12opts.place(x=445, y=270, width=205, height=50)
            e12opts.config(font="Arial 15 bold")
            e12info = Message(a_frame, text="MEASURE:", bg="white", relief=RAISED, bd=2, font="Arial 10 bold",
                              width=145).place(
                x=300, y=270, width=145, height=50)

            e1.insert(0, results[0][0])
            e3.insert(0, results[0][1])
            e4.insert(0, results[0][2])
            e7frame = root.nametowidget(e7opts.menuname).config(font="Arial 20 bold")
            e8frame = root.nametowidget(e8opts.menuname).config(font="Arial 20 bold")
            e10frame = root.nametowidget(e10opts.menuname).config(font="Arial 20 bold")
            e12frame = root.nametowidget(e12opts.menuname).config(font="Arial 20 bold")

            def backspace():
                if str(a_frame.focus_get()).endswith("entry"):
                    e1.delete(e1.index("end") - 1)
                elif str(a_frame.focus_get()).endswith("entry2"):
                    e3.delete(e3.index("end") - 1)
                elif str(a_frame.focus_get()).endswith("entry3"):
                    e4.delete(e4.index("end") - 1)

            def get_focus(key):
                if str(a_frame.focus_get()).endswith("entry"):
                    e1.insert(END, key.upper())
                    e1.configure(fg="black")
                elif str(a_frame.focus_get()).endswith("entry2"):
                    e3.insert(END, key.upper())
                    e3.configure(fg="black")
                elif str(a_frame.focus_get()).endswith("entry3"):
                    e4.insert(END, key.upper())
                    e4.configure(fg="black")

            buttonz = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                       ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                       ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                       ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '#']]
            counter = 0
            for r in buttonz:
                for c in r:
                    def create(r, c):
                        if c == "f" or c == "j":
                            Button(a_frame, relief=RAISED, text=str(c).upper(), padx=10, pady=10,
                                   font='Arial 15 bold',
                                   bd=5, bg="lightgrey", activebackground="lightgrey",
                                   command=lambda: get_focus(c)).place(
                                x=(((r.index(c) + 0.4) + counter) * 60), y=(((buttonz.index(r)) + 6.5) * 60), width=60,
                                height=60)
                        else:
                            Button(a_frame, relief=RAISED, text=str(c).upper(), padx=10, pady=10,
                                   font='Arial 15 bold',
                                   bd=5, command=lambda: get_focus(c)).place(
                                x=(((r.index(c) + 0.4) + counter) * 60), y=(((buttonz.index(r)) + 6.5) * 60), width=60,
                                height=60)

                    create(r, c)
                counter += 0.25
            space = Button(a_frame, relief=RAISED, text="SPACE", padx=20, pady=30, bd=5, font="Arial 12 bold",
                           command=lambda: get_focus(" ")).place(x=115, y=630, width=400, height=60)

            backspace = Button(a_frame, relief=RAISED, text="BACKSPACE", padx=20, bd=5, pady=30,
                               font="Arial 12 bold", command=backspace, bg="#F63131", activebackground="#F63131").place(
                x=550, y=630, width=150, height=60)

        if str(event.widget).startswith(".!commandbutton") and not str(event.widget.__repr__()).split(" ")[
            0].startswith("Logout"):
            textzzz = str(event.widget.__repr__())

            # textzzz = textzzzz.split(" ")

            def update_me(item, qty, price, color):
                #  check if other button is there
                cursor.execute(
                    "SELECT button_status,x,y,text FROM command_buttons WHERE (button_status,x,y) = (%s,%s,%s)",
                    [results[0][0], results[0][3], results[0][4]])
                resultss = cursor.fetchall()
                if len(resultss) > 0 and (textzzz != resultss[0][3]):
                    answer = messagebox.showwarning("Button query!",
                                                    message="Another button is already there. \nPlease pick another spot.")
                else:
                    # update it
                    cursor.execute("UPDATE command_buttons SET text=%s, color=%s, x=%s, y=%s WHERE text = %s",
                                   [e1.get(), e2['bg'], e7.get(), e8.get(), textzzz])
                    messagebox.showwarning(title="Action completed.", message="Button updated.")
                    a_frame.destroy()
                    clear()
                    clear_cmd()
                    login()

            def delete_me():
                cursor.execute("DELETE FROM command_buttons WHERE text = %s", [results[0][0]])
                cursor.execute("DELETE FROM stock WHERE item = %s", [results[0][0]])
                messagebox.showwarning(title="Action completed.", message="Button successfully deleted.")
                a_frame.destroy()
                clear()

            def create_new():
                # check first
                cursor.execute("SELECT text FROM command_buttons WHERE text = %s", [e1.get()])
                resultsss = cursor.fetchall()
                if len(resultsss) > 0:
                    messagebox.showwarning(title="Action canceled.", message="Button name exists.")
                else:
                    cursor.execute(
                        "SELECT button_status,x,y,text FROM command_buttons WHERE (button_status,x,y) = (%s,%s,%s)",
                        [xy_results[0][2], e7.get(), e8.get()])
                    resultssss = cursor.fetchall()
                    if len(resultssss) > 0:
                        answer = messagebox.showwarning("Button query!",
                                                        message="Another button is already there. \nPlease pick another spot.")
                    else:
                        # # create it
                        cursor.execute(
                            "INSERT INTO command_buttons(button_status, text, x, y, color, icon, doneness) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                            [xy_results[0][2], e1.get(), e7.get(), e8.get(), e2['bg'], "", doneness1.get()])
                        cursor.execute("INSERT INTO stock(item, qty, price, belongs_to) VALUES (%s,%s,%s,%s)",
                                       [e1.get(), e3.get(), e4.get(), e10.get()])
                        messagebox.showinfo(title="Button query!", message="Button successfully created!")
                        a_frame.destroy()
                        clear()

            def pick_color():
                color = colorchooser.askcolor(color=e2['bg'], title="Pick color")
                e2['bg'] = color[1]

            def backspace():
                if str(a_frame.focus_get()).endswith("entry"):
                    e1.delete(e1.index("end") - 1)
                elif str(a_frame.focus_get()).endswith("entry2"):
                    e3.delete(e3.index("end") - 1)
                elif str(a_frame.focus_get()).endswith("entry3"):
                    e4.delete(e4.index("end") - 1)

            def get_focus(key):
                if str(a_frame.focus_get()).endswith("entry"):
                    e1.insert(END, key.upper())
                    e1.configure(fg="black")
                elif str(a_frame.focus_get()).endswith("entry2"):
                    e3.insert(END, key.upper())
                    e3.configure(fg="black")
                elif str(a_frame.focus_get()).endswith("entry3"):
                    e4.insert(END, key.upper())
                    e4.configure(fg="black")

            a_frame = MyFrame(300, 50, 750, 750, "lightgrey")
            waiting_timer = None
            cursor.execute("SELECT button_status, text, command, x, y, color FROM command_buttons WHERE text = %s",
                           [textzzz])
            results = cursor.fetchall()

            Button(a_frame, text="X", command=lambda: a_frame.destroy(), bd=5, relief=RAISED).place(x=700 - 35, y=2)

            e1 = Entry(a_frame, justify=CENTER, relief=RAISED, bd=2, font="Arial 12 bold")
            e1.place(x=150, y=20, width=150, height=50)
            e1info = Message(a_frame, text="BUTTON\nNAME", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=20, width=110, height=50)

            e2 = Button(a_frame, text=event.widget['bg'], bg=event.widget['bg'], command=pick_color, bd=2,
                        font="Arial 12 bold")
            e2.place(x=150, y=70, width=150, height=50)
            e2info = Message(a_frame, text="BUTTON\nCOLOR", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=70, width=110, height=50)

            e3 = StringVar(a_frame)
            e3.set(results[0][2])
            e3opts = OptionMenu(a_frame, e3, f"{results[0][2]}")
            e3opts.place(x=150, y=130, width=150, height=50)
            e3opts.config(font="Arial 12 bold")
            e3info = Message(a_frame, text="BUTTON\nCOMMAND", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 9 bold").place(x=25, y=130, width=110, height=50)

            e5 = Button(a_frame, text="UPDATE", bd=4, bg="lightgreen", font="Arial 12 bold",
                        command=lambda: update_me(results[0][0], results[0][1], results[0][2], e2['bg']))
            e5.place(x=350, y=50, width=150, height=150)
            e6 = Button(a_frame, text="DELETE", bd=4, bg="#ff5454", font="Arial 12 bold", command=lambda: delete_me())
            e6.place(x=500, y=50, width=150, height=150)
            e9 = Button(a_frame, text="CREATE\nNEW", bd=4, bg="#f7ea00", font="Arial 12 bold",
                        command=lambda: create_new())
            e9.place(x=500, y=200, width=150, height=50)
            #
            e7 = StringVar(a_frame)
            e7.set(results[0][3])
            e7opts = OptionMenu(a_frame, e7, "0", "1", "2", "3", "4", "5", "6", "7", "8")
            e7opts.place(x=150, y=220, width=150, height=50)
            e7opts.config(font="Arial 15 bold")
            e7info = Message(a_frame, text="BUTTON\nX", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=220, width=110, height=50)
            e8 = StringVar(a_frame)
            e8.set(results[0][4])
            e8opts = OptionMenu(a_frame, e8, "0", "1", "2", "3", "4", "5", "6", "7")
            e8opts.place(x=150, y=270, width=150, height=50)
            e8opts.config(font="Arial 15 bold")
            e8info = Message(a_frame, text="BUTTON\nY", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=270, width=110, height=50)
            #
            e10 = StringVar(a_frame)
            e10.set(results[0][0])
            e10opts = OptionMenu(a_frame, e10, f"{results[0][0]}")
            e10opts.place(x=150, y=320, width=150, height=50)
            e10opts.config(font="Arial 15 bold")
            e10info = Message(a_frame, text="SCREEN\nFUNCTION", bg="white", justify=CENTER, relief=RAISED, bd=2,
                              font="Arial 8 bold").place(x=25, y=320, width=110, height=50)
            #
            # def selected():
            #     print(doneness1.get())
            #
            # doneness1 = StringVar()
            # e11opts = Checkbutton(a_frame, text="DONENESS", variable=doneness1, onvalue="ON", offvalue="OFF",
            #                       command=selected)
            # if check_if_doneness(results[0][0]):
            #     e11opts.select()
            # elif not check_if_doneness(results[0][0]):
            #     e11opts.deselect()
            # e11opts.place(x=300, y=320, height=50)
            # e11opts.config(font="Arial 15 bold", bd=4, relief=RAISED)

            e1.insert(0, textzzz)
            # e3.insert(0, results[0][1])
            # e4.insert(0, results[0][2])
            e7frame = root.nametowidget(e7opts.menuname).config(font="Arial 20 bold")
            e8frame = root.nametowidget(e8opts.menuname).config(font="Arial 20 bold")
            e10frame = root.nametowidget(e10opts.menuname).config(font="Arial 20 bold")

            buttonz = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                       ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                       ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                       ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '#']]
            counter = 0
            for r in buttonz:
                for c in r:
                    def create(r, c):
                        if c == "f" or c == "j":
                            Button(a_frame, relief=RAISED, text=str(c).upper(), padx=10, pady=10,
                                   font='Arial 15 bold',
                                   bd=5, bg="lightgrey", activebackground="lightgrey",
                                   command=lambda: get_focus(c)).place(
                                x=(((r.index(c) + 0.4) + counter) * 60), y=(((buttonz.index(r)) + 6.5) * 60), width=60,
                                height=60)
                        else:
                            Button(a_frame, relief=RAISED, text=str(c).upper(), padx=10, pady=10,
                                   font='Arial 15 bold',
                                   bd=5, command=lambda: get_focus(c)).place(
                                x=(((r.index(c) + 0.4) + counter) * 60), y=(((buttonz.index(r)) + 6.5) * 60), width=60,
                                height=60)

                    create(r, c)
                counter += 0.25
            space = Button(a_frame, relief=RAISED, text="SPACE", padx=20, pady=30, bd=5, font="Arial 12 bold",
                           command=lambda: get_focus(" ")).place(x=115, y=630, width=400, height=60)

            backspace = Button(a_frame, relief=RAISED, text="BACKSPACE", padx=20, bd=5, pady=30,
                               font="Arial 12 bold", command=backspace, bg="#F63131", activebackground="#F63131").place(
                x=500, y=325, width=150, height=60)

        if str(event.widget).startswith(".!logincommandbutton"):

            def update_me(item, color):
                #  check if other button is there
                cursor.execute("SELECT x,y,text FROM command_buttons WHERE (button_status,x,y) = (%s,%s,%s)",
                               ["login_buttons", e7.get(), e8.get()])
                resultss = cursor.fetchall()
                if len(resultss) > 0 and (results[0][0] != resultss[0][2]):
                    answer = messagebox.showwarning("Button query!",
                                                    message="Another button is already there. \nPlease pick another spot.")
                else:  # update it
                    cursor.execute("UPDATE command_buttons SET text=%s, color=%s, x=%s, y=%s WHERE text = %s",
                                   [e1.get(), color, e7.get(), e8.get(), item])
                    cursor.execute("UPDATE members SET member_name = %s WHERE member_id = %s",
                                   [e1.get(), user_id[0][0]])
                    messagebox.showwarning(title="Action completed.", message="Button updated.")
                    exec(f"{clear(), clear_LABEL(), clear_frame(), clear_cmd(), screen_log()}")

            def delete_me():
                cursor.execute("DELETE FROM command_buttons WHERE text = %s", [results[0][0]])
                cursor.execute("DELETE FROM members WHERE member_name = %s", [results[0][0]])
                messagebox.showwarning(title="Action completed.", message="Button successfully deleted.")
                exec(f"{clear(), clear_LABEL(), clear_frame(), clear_cmd(), screen_log()}")

            def create_new():
                # check first
                cursor.execute("SELECT text FROM command_buttons WHERE text = %s", [e1.get()])
                resultsss = cursor.fetchall()
                if len(resultsss) > 0:
                    messagebox.showwarning(title="Action canceled.", message="User already exists!")
                else:
                    cursor.execute(
                        "SELECT button_status,x,y,text FROM command_buttons WHERE (button_status,x,y) = (%s,%s,%s)",
                        ["login_buttons", e7.get(), e8.get()])
                    resultssss = cursor.fetchall()
                    if len(resultssss) > 0:
                        answer = messagebox.showwarning("Button query!",
                                                        message="Another button is already there. \nPlease pick another spot.")
                    else:
                        # # create it
                        cursor.execute(
                            "INSERT INTO command_buttons(button_status, text, x, y, color, icon, doneness) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                            ["login_buttons", e1.get(), e7.get(), e8.get(), e2['bg'], "", "OFF"])
                        cursor.execute("INSERT INTO members(member_name, member_type) VALUES (%s,%s)",
                                       [e1.get(), "OTHER"])

                        cursor.execute("SELECT member_id FROM members WHERE member_name = %s", [e1.get()])
                        user_id2 = cursor.fetchall()
                        user_id3 = user_id2[0][0]

                        messagebox.showinfo(title="Button query!", message="Button successfully created!")
                        cursor.execute("UPDATE command_buttons SET command = %s WHERE text = %s",
                                       [f'staff_id({user_id3})', e1.get()])
                        exec(f"{clear(), clear_LABEL(), clear_frame(), clear_cmd(), screen_log()}")

            def pick_color():
                color = colorchooser.askcolor(color=e2['bg'], title="Pick color")
                e2['bg'] = color[1]

            a_frame = MyFrame(300, 50, 750, 750, "lightgrey")
            waiting_timer = None

            cursor.execute("SELECT text,command,x,y,color FROM command_buttons WHERE text = %s",
                           [str(event.widget['text']).replace("\n", " ")])
            results = cursor.fetchall()
            cursor.execute("SELECT member_id FROM `members` WHERE member_name = %s",
                           [str(event.widget['text']).replace("\n", " ")])
            user_id = cursor.fetchall()

            Button(a_frame, text="X", command=lambda: a_frame.destroy(), bd=5, relief=RAISED).place(x=700 - 35, y=2)

            e1 = Entry(a_frame, justify=CENTER, relief=RAISED, bd=2, font="Arial 12 bold")
            e1.place(x=150, y=20, width=150, height=50)
            e1info = Message(a_frame, text="BUTTON\nNAME:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=20, width=100, height=50)

            e2 = Button(a_frame, text=event.widget['bg'], bg=event.widget['bg'], command=pick_color, bd=2,
                        font="Arial 12 bold")
            e2.place(x=150, y=70, width=100, height=50)
            e2info = Message(a_frame, text="BUTTON\nCOLOR:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=70, width=100, height=50)

            if len(user_id) > 0:
                e3 = Label(a_frame, text=user_id[0][0], bg=event.widget['bg'], bd=2, relief=RAISED,
                           font="Arial 12 bold")
                e3.place(x=150, y=120, width=100, height=50)
                e3info = Message(a_frame, text="USER\nID:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                                 font="Arial 10 bold").place(x=25, y=120, width=100, height=50)

            e5 = Button(a_frame, text="UPDATE", bd=4, bg="lightgreen", font="Arial 12 bold",
                        command=lambda: update_me(results[0][0], e2['bg']))
            e5.place(x=350, y=50, width=150, height=150)
            e6 = Button(a_frame, text="DELETE", bd=4, bg="#ff5454", font="Arial 12 bold", command=lambda: delete_me())
            e6.place(x=500, y=50, width=150, height=150)
            e9 = Button(a_frame, text="CREATE\nNEW", bd=4, bg="#f7ea00", font="Arial 12 bold",
                        command=lambda: create_new())
            e9.place(x=500, y=200, width=150, height=50)

            e7 = StringVar(a_frame)
            e7.set(results[0][2])
            e7opts = OptionMenu(a_frame, e7, "0", "1", "2", "3", "4", "5", "6", "7", "8")
            e7opts.place(x=150, y=220, width=100, height=50)
            e7opts.config(font="Arial 15 bold")
            e7info = Message(a_frame, text="BUTTON\nX:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=220, width=100, height=50)
            e8 = StringVar(a_frame)
            e8.set(results[0][3])
            e8opts = OptionMenu(a_frame, e8, "0", "1", "2", "3", "4", "5", "6", "7")
            e8opts.place(x=150, y=270, width=100, height=50)
            e8opts.config(font="Arial 15 bold")
            e8info = Message(a_frame, text="BUTTON\nY:", bg="white", justify=CENTER, relief=RAISED, bd=2,
                             font="Arial 10 bold").place(x=25, y=270, width=100, height=50)

            e1.insert(0, results[0][0])
            e7frame = root.nametowidget(e7opts.menuname).config(font="Arial 20 bold")
            e8frame = root.nametowidget(e8opts.menuname).config(font="Arial 20 bold")

            def backspace():
                if str(a_frame.focus_get()).endswith("entry"):
                    e1.delete(e1.index("end") - 1)
                elif str(a_frame.focus_get()).endswith("entry2"):
                    e3.delete(e3.index("end") - 1)
                elif str(a_frame.focus_get()).endswith("entry3"):
                    e4.delete(e4.index("end") - 1)

            def get_focus(key):
                if str(a_frame.focus_get()).endswith("entry"):
                    e1.insert(END, key.upper())
                    e1.configure(fg="black")
                elif str(a_frame.focus_get()).endswith("entry2"):
                    e3.insert(END, key.upper())
                    e3.configure(fg="black")
                elif str(a_frame.focus_get()).endswith("entry3"):
                    e4.insert(END, key.upper())
                    e4.configure(fg="black")

            buttonz = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                       ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                       ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                       ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '#']]
            counter = 0
            for r in buttonz:
                for c in r:
                    def create(r, c):
                        if c == "f" or c == "j":
                            Button(a_frame, relief=RAISED, text=str(c).upper(), padx=10, pady=10,
                                   font='Arial 15 bold',
                                   bd=5, bg="lightgrey", activebackground="lightgrey",
                                   command=lambda: get_focus(c)).place(
                                x=(((r.index(c) + 0.4) + counter) * 60), y=(((buttonz.index(r)) + 6.5) * 60), width=60,
                                height=60)
                        else:
                            Button(a_frame, relief=RAISED, text=str(c).upper(), padx=10, pady=10,
                                   font='Arial 15 bold',
                                   bd=5, command=lambda: get_focus(c)).place(
                                x=(((r.index(c) + 0.4) + counter) * 60), y=(((buttonz.index(r)) + 6.5) * 60), width=60,
                                height=60)

                    create(r, c)
                counter += 0.25
            space = Button(a_frame, relief=RAISED, text="SPACE", padx=20, pady=30, bd=5, font="Arial 12 bold",
                           command=lambda: get_focus(" ")).place(x=115, y=630, width=400, height=60)

            backspace = Button(a_frame, relief=RAISED, text="BACKSPACE", padx=20, bd=5, pady=30,
                               font="Arial 12 bold", command=backspace, bg="#F63131", activebackground="#F63131").place(
                x=500, y=325, width=150, height=60)
            #####################################################################################################################

    if str(event.widget).startswith(".!tillbutton"):
        if waiting_timer is not None:
            root.after_cancel(waiting_timer)
            waiting_timer = None
        waiting_timer = root.after(2000, do_this)
    elif str(event.widget).startswith(".!commandbutton"):
        if waiting_timer is not None:
            root.after_cancel(waiting_timer)
            waiting_timer = None
        waiting_timer = root.after(2000, do_this)
    elif str(event.widget).startswith(".!logincommandbutton"):
        if waiting_timer is not None:
            root.after_cancel(waiting_timer)
            waiting_timer = None
        waiting_timer = root.after(2000, do_this)
    # else:
    #     print("need to create the class")


def reset_timer(event=None):
    global SCREENSAVER_TIMER, SCREENSAVER_TIMER2
    if dev_reset_timer:
        # cancel the previous event
        if SCREENSAVER_TIMER is not None:
            root.after_cancel(SCREENSAVER_TIMER)
            root.after_cancel(SCREENSAVER_TIMER2)
        # create new timer
        SCREENSAVER_TIMER = root.after(12000, user_is_inactive)
        SCREENSAVER_TIMER2 = root.after(20000, till_is_inactive)


def screen_log():
    global TEMP_BUTTONS, screen_logo
    screen_logo = Canvas(root, height=HEIGHT, width=WIDTH, bg="lightgrey")
    screen_logo.place(x=0, y=0)
    screen_logo.create_image(0, 0, anchor="nw", image=logo)
    for button in TEMP_BUTTONS:
        button.destroy()
        button.remove_stock_label()
    TEMP_BUTTONS.clear()
    root.bind_all('<Any-ButtonPress>', goToLogin)


def sql_insert_stock(name):
    global STOCK_SWITCH
    curr_qty = sql_retrieve_stock(name)
    qty_upd = int(curr_qty) + STOCK_SWITCH
    if int(curr_qty) >= 0:
        if qty_upd >= 0:
            insert_stock = f"UPDATE stock SET qty='{qty_upd}' WHERE item='{name}'"
            cursor.execute(insert_stock)
        else:
            insert_stock = f"UPDATE stock SET qty='0' WHERE item='{name}'"
            cursor.execute(insert_stock)


def basket_retrieve_stock(name, mem_id, t_id):
    sql_select_basket = f"SELECT * FROM `basket` WHERE (product, member_id, table_id) = ('{name}','{mem_id}','{t_id}')"
    cursor.execute(sql_select_basket)
    all_basket_rows = cursor.fetchall()
    return all_basket_rows[0][1]


def basket_retrieve_name(name, mem_id, t_id):
    sql_select_basket = f"SELECT * FROM `basket` WHERE (product, member_id, table_id) = ('{name}','{mem_id}','{t_id}')"
    cursor.execute(sql_select_basket)
    all_basket_rows = cursor.fetchall()
    return all_basket_rows[0][0]


def sql_retrieve_stock(name):
    sql_select_basket = f"SELECT qty FROM `stock` WHERE item = '{name}' "
    cursor.execute(sql_select_basket)
    all_basket_rows = cursor.fetchall()
    for row in all_basket_rows:
        return row[0]


def mod_stock(name, qty):
    sql_remove_stock = f"SELECT * FROM `stock` WHERE item = '{name}' "
    cursor.execute(sql_remove_stock)
    all_basket_rows = cursor.fetchall()
    if len(all_basket_rows) > 0:
        curr_stock = all_basket_rows[0][2]
        upd_stock = int(curr_stock) + qty
        if int(sql_retrieve_stock(name)) >= 99:
            cursor.execute("UPDATE `stock` SET `qty`='%s' WHERE (item, qty) = (%s, %s)", [99, name, curr_stock])
        elif upd_stock > 0:
            sql_upd_stock = "UPDATE `stock` SET `qty`='%s' WHERE (item, qty) = (%s, %s)"
            cursor.execute(sql_upd_stock, [upd_stock, name, curr_stock])
        elif upd_stock < 0:
            return
        elif upd_stock == 0:
            sql_upd_stock = "UPDATE `stock` SET `qty`='%s' WHERE (item, qty) = (%s, %s)"
            cursor.execute(sql_upd_stock, [0, name, curr_stock])


def bold_text(value):
    string = "\033[1m" + str(value) + "\033[0m"
    return string


def italic_text(value):
    string = "\x1B[3m" + str(value) + "\x1B[0m"
    return string


def open_drawer(reason):
    global basket, total_price, TABLE_NUMBER, PRICE_DISCOUNT, MEMBER_ID, TEMP_BUTTONS2, TEMP_BUTTONS, DRAWER_PORT
    if reason == "?":
        def remove_payment_screen():
            clear_cmd()
            command_screen()

        def how_muchz():
            def backspace():
                refund_entry.delete(refund_entry.index("end") - 1)

            def delete_my_keypad():
                drawer_frame.destroy()
                refund_entry.destroy()
                for button in temp_x:
                    button.destroy()

            def button_click(number):
                current = refund_entry.get()
                refund_entry.delete(0, END)
                refund_entry.insert(0, ("£" + (str(current) + str(number))).replace("££", "£"))

            remove_payment_screen()

            drawer_frame = MyFrame(4, 1, 570, 800, root_bg_color)
            drawer_frame.place(x=455, y=96)
            refund_entry = tk.Entry(root, font="Arial 25 bold", justify="center")
            refund_entry.grid(row=2, column=4, columnspan=5)

            keypad_button_1 = CommandButton("1", lambda: button_click(1), 5, 5)
            keypad_button_2 = CommandButton("2", lambda: button_click(2), 6, 5)
            keypad_button_3 = CommandButton("3", lambda: button_click(3), 7, 5)
            keypad_button_4 = CommandButton("4", lambda: button_click(4), 5, 4)
            keypad_button_5 = CommandButton("5", lambda: button_click(5), 6, 4)
            keypad_button_6 = CommandButton("6", lambda: button_click(6), 7, 4)
            keypad_button_7 = CommandButton("7", lambda: button_click(7), 5, 3)
            keypad_button_8 = CommandButton("8", lambda: button_click(8), 6, 3)
            keypad_button_9 = CommandButton("9", lambda: button_click(9), 7, 3)
            keypad_button_0 = CommandButton("0", lambda: button_click(0), 5, 6)
            keypad_button_backspace = CommandButton(" DEL", backspace, 6, 6)
            keypad_button_finalize = CommandButton("OPEN\nDRAWER", lambda: [open_drawer("REFUND " + refund_entry.get()),
                                                                            delete_my_keypad(), drawer_frame.destroy(),
                                                                            open_it()],
                                                   8, 3)
            cancelz = CommandButton("CANCEL", delete_my_keypad, 7, 6)
            cancelz.configure(font="Arial 10 bold")
            keypad_button_1.configure(font="Arial 10 bold")
            keypad_button_2.configure(font="Arial 10 bold")
            keypad_button_3.configure(font="Arial 10 bold")
            keypad_button_4.configure(font="Arial 10 bold")
            keypad_button_5.configure(font="Arial 10 bold")
            keypad_button_6.configure(font="Arial 10 bold")
            keypad_button_7.configure(font="Arial 10 bold")
            keypad_button_8.configure(font="Arial 10 bold")
            keypad_button_9.configure(font="Arial 10 bold")
            keypad_button_0.configure(font="Arial 10 bold")
            keypad_button_backspace.configure(font="Arial 10 bold", bg="#F63131", activebackground="#F63131")
            keypad_button_finalize.configure(font="Arial 10 bold", bg="lightgreen", activebackground="lightgreen",
                                             width=11)
            temp_x = [keypad_button_0, keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                      keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_8, keypad_button_9,
                      keypad_button_backspace, keypad_button_finalize, cancelz]

        drawer_frame = MyFrame(4, 1, 570, 800, root_bg_color)
        drawer_frame.place(x=455, y=96)

        needz_change = CommandButton("NEED\nCHANGE", lambda: [remove_payment_screen(), drawer_frame.destroy(),
                                                              open_drawer("NEED CHANGE"), command_screen(), open_it()],
                                     6, 2)
        needz_change.configure(font="Arial 10 bold")
        refundz = CommandButton("REFUND", lambda: [remove_payment_screen(), how_muchz(), drawer_frame.destroy()], 6, 3)
        refundz.configure(font="Arial 10 bold")
        otherz = CommandButton("OTHER?", lambda: [remove_payment_screen(), drawer_frame.destroy(),
                                                  open_drawer(f"OTHER?!? ask {return_member_name()} :)"),
                                                  command_screen(), ], 6, 4)
        otherz.configure(font="Arial 10 bold")
        cancelz = CommandButton("CANCEL",
                                lambda: [remove_payment_screen(), drawer_frame.destroy(), command_screen(), open_it()],
                                6, 5)
        cancelz.configure(font="Arial 10 bold")

    else:
        cursor.execute("INSERT INTO drawer(member,reason, time) VALUES (%s,%s,%s)", [return_member_name(), reason, time_now()])
        open_it()


def print_bill_split(status, uniq_ref=None):
    global basket, total_price, TABLE_NUMBER, PRICE_DISCOUNT, MEMBER_ID
    or_status = f"{status} PAID BY %"
    info = PUB_NAME + "  " + str(datetime.now().strftime("%Y-%m-%d %H:%M"))
    xPrettyTable = PrettyTable()
    xPrettyTable.field_names = ["QTY", "ITEM", " "]
    cursor.execute(
        f"SELECT product,price FROM basket WHERE table_id = %s AND (status LIKE %s OR status = %s) ORDER BY datez ASC",
        [TABLE_NUMBER, f"{or_status}", status])
    results = cursor.fetchall()
    cursor.execute(
        f"SELECT IFNULL(format(sum(price), 2), 0) AS totalz FROM basket WHERE table_id = %s AND (status LIKE %s OR status = %s) ORDER BY datez ASC",
        [TABLE_NUMBER, f"{or_status}", status])
    total_price = cursor.fetchall()
    total_price = total_price[0][0]
    if len(results) > 0:
        print(f"""
    .      .
   /|      |\\
\__\\\\      //__/
   ||      ||
 \__'\     |'__/
   '_\\\\   //_'
   _.,:---;,._
   \_:     :_/
     |0. .0|    {PUB_NAME}
     |     |
      \.-./ 
       `-'   """)
        print(info)
        if int(TABLE_NUMBER) > 0:
            print(f"Table: {TABLE_NUMBER} . . . Server:{return_member_name()}")
        else:
            print(f"Table: BAR . . . Server:{return_member_name()}")
        print("-" * len(info))
        ordered = []
        for row in results:  # get products & price
            xPrettyTable.add_row([1, row[0], ("£" + format(round(float(row[1]), 2), '.2f')).replace("£-", "-£")])
            ordered.append([1, row[0], f"£{row[1]}"])

        sql_select_basket = "SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = %s && status LIKE %s ORDER BY datez ASC"
        cursor.execute(sql_select_basket, [TABLE_NUMBER, f"{status} CASHZ"])
        cash_paid = cursor.fetchall()  # SUM TOTAL CASH

        for row in cash_paid:
            cash_paid = str(row[0])  # TOTAL SUM OF CASH PAID

        if float(str(total_price).replace(',', '')) > 0:
            xPrettyTable.add_row(
                ["", "TOTAL:",
                 (("£" + format(round(float(str(total_price).replace(',', '')), 2), '.2f')).replace("£-", "-£"))])
            if float(str(cash_paid).replace(',', '')) < 0:
                xPrettyTable.add_row(
                    ["", "PAID:", (("£" + str(float(str(cash_paid).replace(',', '')))).replace("£-", "£"))])
                if abs(float(str(cash_paid).replace(',', ''))) > abs(float(str(total_price).replace(',', ''))):
                    xPrettyTable.add_row(["", "CHANGE:",
                                          (" £" + format(round((float(str(cash_paid).replace(',', '')) + float(
                                              str(total_price).replace(',', ''))), 2),
                                                         '.2f')).replace(
                                              "£-", "£")])
                elif abs(float(float(str(cash_paid).replace(',', '')))) == abs(
                        float(str(total_price).replace(',', ''))):
                    print("no change, all paid, etc")
                elif abs(float(float(str(cash_paid).replace(',', '')))) < abs(float(str(total_price).replace(',', ''))):
                    xPrettyTable.add_row(["", "LEFT TO PAY:",
                                          (" £" + format(round((float(str(cash_paid).replace(',', '')) + float(
                                              str(total_price).replace(',', ''))), 2),
                                                         '.2f')).replace(
                                              "£-", "£")])
            xPrettyTable.align["QTY"] = "c"
            xPrettyTable.align["ITEM"] = "l"
            xPrettyTable.align[" "] = "r"
            xPrettyTable.border = False
            xPrettyTable.min_width["QTY"] = 10
            xPrettyTable.min_width["ITEM"] = 50
            xPrettyTable.min_width[" "] = 20
            xPrettyTable.max_width["ITEM"] = 70
            xPrettyTable.max_table_width = 36
            print(xPrettyTable)
            print("-" * len(info))
            print("--------------Thank you,-------------")
            print(f"----------Team {PUB_NAME}--------")
            if uniq_ref is not None:
                print(f"---REF: {uniq_ref}---")

            print("-" * len(info))
            #
            with xlsxwriter.Workbook(f'bill_Till1_{str(status).replace(" ", "_")}.xlsx') as workbook:
                cell_format = workbook.add_format()
                cell_format.set_text_wrap()
                cell_format.set_align('left')
                cell_format.set_align('top')
                cell_format.set_font("Arial")
                cell_format.set_font_size(9)

                cell_format1 = workbook.add_format({'bold': True})
                cell_format1.set_align('center')
                cell_format1.set_align('top')
                cell_format1.set_font_size(12)

                cell_format2 = workbook.add_format({'bold': True})
                cell_format2.set_align('center')
                cell_format2.set_align('top')
                cell_format2.set_font_size(9)
                cell_format2.set_text_wrap()

                cell_format3 = workbook.add_format()
                # cell_format3.set_text_wrap()
                cell_format3.set_align('center')
                cell_format3.set_align('top')
                cell_format3.set_font("Arial")
                cell_format3.set_font_size(9)

                cell_format4 = workbook.add_format({'valign': 'vcenter'})
                cell_format4.set_text_wrap()
                cell_format4.set_align('center')
                cell_format4.set_align('top')
                cell_format4.set_font("Arial")
                cell_format4.set_font_size(8)

                worksheet = workbook.add_worksheet()

                worksheet.set_margins(left=0, right=0, top=0, bottom=0)
                worksheet.set_column("A:A", 2)
                worksheet.set_column("B:B", 13.80)
                worksheet.set_column("C:C", 5.71)

                counter = 0
                worksheet.insert_image('A1', 'icons/receipt1.15.png')
                counter += 10
                worksheet.write(f"B{counter}", f"Table:{TABLE_NUMBER}", cell_format3)
                counter += 1
                worksheet.write(f"B{counter}", f"Server:{return_member_namee(MEMBER_ID)}", cell_format3)
                counter += 1
                worksheet.write(f"B{counter}", f"{now.strftime('%d/%m/%Y - %H:%M:%S')}", cell_format3)
                counter += 1
                worksheet.write(f"B{counter}", "", workbook.add_format({'bold': True}))
                counter += 1
                for row_num, data in enumerate(ordered):
                    worksheet.write(f"A{counter}", f"{data[0]}", cell_format)
                    worksheet.write(f"B{counter}", f"{data[1]}", cell_format)
                    worksheet.write(f"C{counter}", f"{data[2]}", cell_format3)
                    counter += 1
                worksheet.write(f"B{counter}", f"    TOTAL: £{total_price}", cell_format1)
                counter += 1
                if not str(float(float(str(cash_paid).replace(',', '')))) == "0.0":
                    worksheet.write(f"B{counter}",
                                    f"    PAID: £{str(float(str(cash_paid).replace(',', ''))).replace('-', '')}",
                                    cell_format1)
                    counter += 1
                if abs(float(str(cash_paid).replace(',', ''))) > abs(float(str(total_price).replace(',', ''))):
                    worksheet.write(f"B{counter}",
                                    f"    CHANGE: £{format(round((float(str(cash_paid).replace(',', '')) + float(str(total_price).replace(',', ''))), 2), '.2f').replace('-', '')}",
                                    cell_format1)
                    counter += 1
                if uniq_ref is not None:
                    worksheet.write(f"B{counter}", f"UNIQUE REF:\n{uniq_ref}", cell_format4)
                counter += 2
                worksheet.insert_image(f'A{counter}', 'icons/receipt3.png')
                counter += 1
                if REAL_PRINT:
                    os.startfile(f'C:/POS/bill_Till1_{str(status).replace(" ", "_")}.xlsx', 'print')


def print_bill():
    global basket, total_price, TABLE_NUMBER, PRICE_DISCOUNT, MEMBER_ID

    info = PUB_NAME + "  " + str(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
    xPrettyTable = PrettyTable()
    sql_select_basket = f"SELECT product,price FROM basket WHERE table_id = %s && status NOT LIKE %s ORDER BY datez ASC"
    cursor.execute(sql_select_basket, [TABLE_NUMBER, '%CASHZ'])
    results = cursor.fetchall()

    if len(results) > 0:
        print(f"""
    .      .
   /|      |\\
\__\\\\      //__/
   ||      ||
 \__'\     |'__/
   '_\\\\   //_'
   _.,:---;,._
   \_:     :_/
     |0. .0|    {PUB_NAME}
     |     |
     ,\.-./ \\
     ;;`-'   `---__________----_""")
        print(info)

        if int(TABLE_NUMBER) > 0:
            print(f"Server:{return_member_name()}               Table:{TABLE_NUMBER}")
        else:
            print(f"Server:{return_member_name()}               Table: BAR")
        print("-" * len(info))
        ordered = []
        for row in results:  # get items & price
            xPrettyTable.add_row([1, row[0], ("£" + format(round(float(row[1]), 2), '.2f')).replace("£-", "-£")])
            ordered.append([1, row[0], f"£{row[1]}"])
        sql_select_basket = f"SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = %s && status != 'CASHZ' ORDER BY datez ASC"
        cursor.execute(sql_select_basket, [TABLE_NUMBER])
        all_basket_rows = cursor.fetchall()
        sql_select_basket = "SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = %s ORDER BY datez ASC"
        cursor.execute(sql_select_basket, [TABLE_NUMBER])
        change = 0
        the_change = cursor.fetchall()
        for row in all_basket_rows:
            total_price = str(row[0])
        for row in the_change:
            change = str(row[0])

        if PRICE_DISCOUNT > 0:
            before_discount = total_price
            total_price = round((float(total_price) - ((float(total_price) * PRICE_DISCOUNT) / 100)), 2)
            xPrettyTable.add_row(
                ["", "TOTAL:", ("£" + format(round(float(before_discount), 2), '.2f')).replace("£-", "-£")])
            xPrettyTable.add_row(["", "DISCOUNT:", f"{PRICE_DISCOUNT}%"])
            xPrettyTable.add_row(
                ["", "TOTAL:", (" £" + format(round(float(total_price), 2), '.2f')).replace("£-", "-£")])
            if total_price < 0:
                xPrettyTable.add_row(
                    ["", "CHANGE:", (" £" + format(round(float(total_price), 2), '.2f')).replace("£-", "£")])
            xPrettyTable.align["QTY"] = "c"
            xPrettyTable.align["ITEM"] = "l"
            xPrettyTable.align[" "] = "r"
            xPrettyTable.border = False
            xPrettyTable.min_width["QTY"] = 10
            xPrettyTable.min_width["ITEM"] = 35
            xPrettyTable.min_width[" "] = 20
            xPrettyTable.max_width["ITEM"] = 60
            xPrettyTable.max_table_width = 30
            xPrettyTable.header = False
            print(xPrettyTable)
            print("-" * len(info))
            print("-" * 11 + "-Thank you," + "-" * 11)
            print("-" * 7 + f"Team {PUB_NAME}" + "-" * 7)
            print("-" * len(info))
        else:
            xPrettyTable.add_row([" ", " TOTAL:", (("£" + total_price).replace("£-", "-£"))])
            if float(str(change).replace(",", "")) < 0:
                xPrettyTable.add_row(["", "CHANGE:", (("£" + change).replace("£-", "£"))])
            xPrettyTable.align["QTY"] = "c"
            xPrettyTable.align["ITEM"] = "l"
            xPrettyTable.align["x"] = "r"
            xPrettyTable.border = False
            xPrettyTable.min_width["QTY"] = 5
            xPrettyTable.max_width["QTY"] = 5
            xPrettyTable.min_width["ITEM"] = 14
            xPrettyTable.max_width["ITEM"] = 14
            xPrettyTable.min_width["x"] = 10
            xPrettyTable.max_width["x"] = 14
            xPrettyTable.max_table_width = 38
            xPrettyTable.header = False
            print(xPrettyTable)
            print("-" * len(info))
            print("--------------Thank you,-------------")
            print(f"----------Team {PUB_NAME}--------")
            print("-" * len(info))
            ordered.sort(key=lambda x: x[1])
            with xlsxwriter.Workbook(f'bill_Till1.xlsx') as workbook:
                cell_format = workbook.add_format()
                cell_format.set_text_wrap()
                cell_format.set_align('left')
                cell_format.set_align('top')
                cell_format.set_font("Arial")
                cell_format.set_font_size(9)

                cell_format1 = workbook.add_format({'bold': True})
                # cell_format1.set_align('right')
                cell_format1.set_align('top')
                cell_format1.set_font_size(12)

                cell_format2 = workbook.add_format({'bold': True})
                cell_format2.set_align('center')
                cell_format2.set_align('top')
                cell_format2.set_font_size(9)
                cell_format2.set_text_wrap()

                cell_format3 = workbook.add_format()
                # cell_format3.set_text_wrap()
                cell_format3.set_align('right')
                cell_format3.set_align('top')
                cell_format3.set_font("Arial")
                cell_format3.set_font_size(9)

                worksheet = workbook.add_worksheet()

                worksheet.set_margins(left=0, right=0, top=0, bottom=0)
                worksheet.set_column("A:A", 2)
                worksheet.set_column("B:B", 13.80)
                worksheet.set_column("C:C", 5.71)

                counter = 0
                worksheet.insert_image('A1', 'icons/receipt1.15.png')
                counter += 10
                worksheet.write(f"B{counter}", f"Table:{TABLE_NUMBER}", cell_format3)
                counter += 1
                worksheet.write(f"B{counter}", f"Server:{return_member_namee(MEMBER_ID)}", cell_format3)
                counter += 1
                worksheet.write(f"B{counter}", f"{now.strftime('%d/%m/%Y - %H:%M:%S')}", cell_format3)
                counter += 1
                worksheet.write(f"B{counter}", "", workbook.add_format({'bold': True}))
                counter += 1
                for row_num, data in enumerate(ordered):
                    worksheet.write(f"A{counter}", f"{data[0]}", cell_format)
                    worksheet.write(f"B{counter}", f"{data[1]}", cell_format)
                    worksheet.write(f"C{counter}", f"{data[2]}", cell_format3)
                    counter += 1
                worksheet.write(f"B{counter}", f"    TOTAL: £{total_price}", cell_format1)
                counter += 1
                worksheet.insert_image(f'A{counter}', 'icons/receipt3.png')
                counter += 1
                if REAL_PRINT:
                    os.startfile('bill_Till1.xlsx', 'print')


def reprint():
    global TEMP_BUTTONS
    mod_frame = MyFrame(100, 350, 300, 400, "lightgrey")

    temp = Button(mod_frame, text="X", font="Arial 10 bold", bg="#EA3F3F",
                  command=lambda: [mod_frame.destroy(), temp.destroy(), temp1.destroy(), temp2.destroy(),
                                   temp3.destroy()])
    temp1 = Button(mod_frame, text="FOR BAR", width="12",
                   command=lambda: [print_for_bar('ORDERED'), mod_frame.destroy(), temp.destroy(), temp1.destroy(),
                                    temp2.destroy(), temp3.destroy()])
    temp2 = Button(mod_frame, text="FOR KITCHEN", width="12",
                   command=lambda: [print_for_kitchen('ORDERED'), mod_frame.destroy(), temp.destroy(), temp1.destroy(),
                                    temp2.destroy(), temp3.destroy()])
    temp3 = Button(mod_frame, text="FOR PUDS", width="12",
                   command=lambda: [print_for_puds('ORDERED'), mod_frame.destroy(), temp.destroy(), temp1.destroy(),
                                    temp2.destroy(), temp3.destroy()])

    temp1.configure(font="Arial 25 bold")
    temp2.configure(font="Arial 25 bold")
    temp3.configure(font="Arial 25 bold")

    temp.place(x=260, y=15)
    temp1.place(x=10, y=50)
    temp2.place(x=10, y=150)
    temp3.place(x=10, y=250)


def print_for_kitchen(where):
    global basket, total_price, MEMBER_ID, TABLE_NUMBER, REAL_PRINT
    info = "Check:" + str(CHECK_NUMBER) + " . . " + str(datetime.now().strftime("%H:%M"))
    starter_PT = PrettyTable()
    starter_PT.field_names = ["c1", "c2"]
    starter_PT.align["c1"] = "c"
    starter_PT.align["c2"] = "l"
    starter_PT.border = False
    starter_PT.min_width["c1"] = 4
    starter_PT.max_width["c1"] = 4
    starter_PT.min_width["c2"] = 42  # edit later
    starter_PT.max_width["c2"] = 89
    starter_PT.max_table_width = 30
    starter_PT.header = False

    main_PT = PrettyTable()
    main_PT.field_names = ["c1", "c2"]
    main_PT.align["c1"] = "c"
    main_PT.align["c2"] = "l"
    main_PT.border = False
    main_PT.min_width["c1"] = 4
    main_PT.max_width["c1"] = 4
    main_PT.min_width["c2"] = 40  # edit later
    main_PT.max_width["c2"] = 89
    main_PT.max_table_width = 30
    main_PT.header = False

    side_PT = PrettyTable()
    side_PT.field_names = ["c1", "c2"]
    side_PT.align["c1"] = "c"
    side_PT.align["c2"] = "l"
    side_PT.border = False
    side_PT.min_width["c1"] = 4
    side_PT.max_width["c1"] = 4
    side_PT.min_width["c2"] = 42  # edit later
    side_PT.max_width["c2"] = 90
    side_PT.max_table_width = 30
    side_PT.header = False

    got_starters = False
    got_mains = False
    got_sides = False

    # cursor.execute("SELECT * FROM `basket` WHERE (table_id, status) = (%s, 'IN BASKET') ORDER BY product",
    #                [TABLE_NUMBER])
    cursor.execute("SELECT * FROM `basket` WHERE (table_id, status) = (%s,%s) ORDER BY product",
                   [TABLE_NUMBER, where])
    results_x = cursor.fetchall()
    # here to code to group items with same name
    if int(len(results_x)) > int(0):
        counterz = 0

        unique_items = {}

        for item in results_x:
            if belongs_to(item[0], "STARTER"):
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

            if belongs_to(item[0], "CUSTOM STARTER") or item[0].endswith("CUSTOM STARTER"):
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

            if belongs_to(item[0], "MAIN"):
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

            if belongs_to(item[0], "CUSTOM MAIN") or item[0].endswith("CUSTOM MAIN"):
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

            if belongs_to(item[0], "SIDE"):
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

            if belongs_to(item[0], "CUSTOM SIDE") or item[0].endswith("CUSTOM SIDE"):
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

        for row in unique_items:
            if belongs_to(row, "STARTER"):
                got_starters = True
                starter_PT.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            starter_PT.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            elif belongs_to(row, "CUSTOM STARTER") or row.endswith("CUSTOM STARTER"):
                got_starters = True
                starter_PT.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            starter_PT.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            elif belongs_to(row, "MAIN"):  # elif here
                got_mains = True

                main_PT.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            main_PT.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            elif belongs_to(row, "CUSTOM MAIN") or row.endswith("CUSTOM MAIN"):
                got_mains = True
                main_PT.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            main_PT.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            elif belongs_to(row, "SIDE"):  # elif here
                got_sides = True
                side_PT.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            side_PT.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            elif belongs_to(row, "CUSTOM SIDE") or row.endswith("CUSTOM SIDE"):
                got_sides = True
                side_PT.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            side_PT.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)
        if len(unique_items) > 0:
            print("*PRINTING FOR KITCHEN - ADMIN CHECK MODE")
            print()
            print(info)
            print(f"TB: {TABLE_NUMBER} . . . . . . {return_member_name()}")
            if where == "ORDERED":
                print("***** REPRINT *****")
            if got_starters:
                print("\t\tSTARTERS:")
                # starter_PT.sortby = "c2" # need to find another way, otherwise if there is a message, it wont stick to it
                print(starter_PT)  # and yes, found another way :) keep this here for reminder, good easter egg ^_^
            if got_mains:
                print("\t\tMAINS:")
                # main_PT.sortby = "c2"
                print(main_PT)
            if got_sides:
                print("\t\tSIDES:")
                print(side_PT)
            calculate_total()

            temp_print = open("temp_print_kitchen.txt", "w")

            with temp_print as file:
                if where == "ORDERED":
                    file.write("-------------REPRINT------------\n")
                if got_starters:
                    file.write("-------------STARTERS------------\n")
                    file.write(f"{starter_PT}\n")
                if got_mains:
                    file.write("\n")
                    file.write("----------------MAINS---------------\n")
                    file.write(f"{main_PT}\n")
                if got_sides:
                    file.write("\n")
                    file.write("----------------SIDES---------------\n")
                    file.write(f"{side_PT}\n")

            if got_mains or got_starters or got_sides:
                with open('temp_print_kitchen.txt', 'r+') as f:
                    txt = f.read().replace('   ', ' ')
                    f.seek(0)
                    f.write(txt)
                    f.truncate()

            if REAL_PRINT:
                with open("temp_print_kitchen.txt", "r") as file:
                    with Printer(linegap=0, printer_name="POS-58") as printer:
                        printer.text(f"{info}\n", font_config=printer_font_XL)
                        printer.text(f"TB: {TABLE_NUMBER} . . . . . . {return_member_name()}\n",
                                     font_config=printer_font_XL)
                        printer.text(file.read(), font_config=printer_font_reg)


def print_for_puds(where):
    global basket, total_price, TABLE_NUMBER

    info = "Check:" + str(CHECK_NUMBER) + " . . " + str(now.strftime("%H:%M"))
    xPrettyTable = PrettyTable()
    xPrettyTable.field_names = ["", " "]
    xPrettyTable.align[""] = "c"
    xPrettyTable.align[" "] = "l"
    xPrettyTable.border = False
    xPrettyTable.min_width[""] = 2
    xPrettyTable.max_width[""] = 2
    xPrettyTable.min_width[" "] = 42  # edit later
    xPrettyTable.max_width[" "] = 90
    xPrettyTable.max_table_width = 30
    xPrettyTable.header = False
    if_got_puds = False
    if_got_starter = False
    if_got_mains = False
    basket.sort()
    cursor.execute("SELECT * FROM `basket` WHERE (table_id, status) = (%s, %s) ", [TABLE_NUMBER, where])
    # cursor.execute("SELECT * FROM `basket` WHERE (table_id) = (%s) ", [TABLE_NUMBER])
    results_x = cursor.fetchall()
    just_icecream = []
    if int(len(results_x)) > int(0):
        counterz = 0
        unique_items = {}
        for item in results_x:
            if item[0] == "ICE CREAMS":
                if_got_puds = True
                just_icecream.append([item[0], item[6]])

            elif belongs_to(item[0], "STARTER"):
                if_got_starter = True
            elif belongs_to(item[0], "MAIN"):
                if_got_mains = True
            elif belongs_to(item[0], "PUD"):
                if_got_puds = True
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}
            elif belongs_to(item[0], "CUSTOM PUD") or item[0].endswith("CUSTOM PUD"):
                if_got_puds = True

                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}

        for row in unique_items:
            if belongs_to(row, "PUD"):
                xPrettyTable.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            xPrettyTable.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            elif belongs_to(row, "CUSTOM PUD") or row.endswith("CUSTOM PUD"):
                xPrettyTable.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            xPrettyTable.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

        for item in just_icecream:
            xPrettyTable.add_row([1, item[0]])
            if check_if_msg(item[0], item[1], where) is True:
                temp_msgs = get_msg_for(item[0], item[1], where)
                for x in range(len(temp_msgs)):
                    xPrettyTable.add_row(["", temp_msgs[x][0]])
                msg_is_printed_for(item[0], item[1])

    if if_got_puds:
        print("*PRINTING FOR PUDS - ADMIN CHECK MODE")
        print()
        print(info)
        print(f"{return_member_name()} . . . . . . TB:{bold_text(TABLE_NUMBER)}")
        if where == "ORDERED":
            print("***** REPRINT *****")
        if if_got_starter:
            print("Table got starters, wait!")
        if if_got_mains:
            print("Table got mains, wait!")
        if if_got_puds:
            print(xPrettyTable)
        print()
        print()
    calculate_total()

    if if_got_puds:
        temp_print_pud = open("temp_print_pud.txt", "w")
        with temp_print_pud as file:
            if where == "ORDERED":
                file.write("***** REPRINT *****\n")
            if if_got_starter:
                file.write("This table got starters, so wait!\n")
            if if_got_mains:
                file.write("This table got mains, so wait!\n")
            if if_got_puds:
                file.write(f"{xPrettyTable}\n")

    if if_got_puds:
        with open('temp_print_pud.txt', 'r+') as f:
            txt = f.read().replace('   ', '')
            f.seek(0)
            f.write(txt)
            f.truncate()

    if REAL_PRINT:
        if if_got_puds:
            with open("temp_print_pud.txt", "r") as file:
                with Printer(linegap=0) as printer:
                    printer.text(f"{info}\n", font_config=printer_font_XL)
                    printer.text(f"TB: {TABLE_NUMBER} . . . . . . {return_member_name()}\n",
                                 font_config=printer_font_XL)
                    printer.text(file.read(), font_config=printer_font_reg)


def print_for_bar(where):
    global basket, total_price, TABLE_NUMBER, MEMBER_ID

    info = "Check:" + str(CHECK_NUMBER) + " . . " + str(now.strftime("%H:%M"))

    xPrettyTable = PrettyTable()
    xPrettyTable.field_names = ["", " "]
    xPrettyTable.align[""] = "c"
    xPrettyTable.align[" "] = "l"
    xPrettyTable.border = False
    xPrettyTable.min_width[""] = 2
    xPrettyTable.max_width[""] = 2
    xPrettyTable.min_width[" "] = 42  # edit later
    xPrettyTable.max_width[" "] = 90
    xPrettyTable.max_table_width = 30
    xPrettyTable.header = False

    got_drinks = False
    cursor.execute("SELECT * FROM `basket` WHERE (table_id, status) = (%s, %s) ", [TABLE_NUMBER, where])
    results_x = cursor.fetchall()

    if int(len(results_x)) > int(0):
        counterz = 0
        unique_items = {}
        for item in results_x:
            if belongs_to(item[0], "BAR"):
                got_drinks = True
                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}
            elif belongs_to(item[0], "CUSTOM BAR") or item[0].endswith("CUSTOM BAR"):
                got_drinks = True

                if item[0] not in unique_items:
                    unique_items[item[0]] = {"qty": 1, "id": f"{item[6]}"}
                else:
                    unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                             "id": (str(unique_items[item[0]]["id"]) + ", " + str(item[6]))}
        for row in unique_items:

            if belongs_to(row, "BAR"):
                xPrettyTable.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            xPrettyTable.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

            if belongs_to(row, "CUSTOM BAR") or row.endswith("CUSTOM BAR"):
                xPrettyTable.add_row([unique_items[row]["qty"], row])

                for value in unique_items[row]["id"].split(", "):
                    if check_if_msg(row, value, where) is True:
                        temp_msgs = get_msg_for(row, value, where)
                        for x in range(len(temp_msgs)):
                            xPrettyTable.add_row(["", temp_msgs[x][0]])
                        msg_is_printed_for(row, value)

    if got_drinks:
        print("*PRINTING FOR BAR - ADMIN CHECK MODE")
        print()
        print(info)
        print(f"{return_member_name()} . . . . . . TB:{bold_text(TABLE_NUMBER)}")
        if where == "ORDERED":
            print("***** REPRINT *****")
        print(xPrettyTable)
        print()
        print()

        temp_print_bar = open("temp_print_bar.txt", "w")
        with temp_print_bar as file:
            if where == "ORDERED":
                file.write("***** REPRINT *****\n")
            file.write(f"{xPrettyTable}\n")

    calculate_total()

    if got_drinks:
        with open('temp_print_bar.txt', 'r+') as f:
            txt = f.read().replace('   ', '')
            f.seek(0)
            f.write(txt)
            f.truncate()

    if got_drinks:
        if REAL_PRINT:
            with open("temp_print_bar.txt", "r") as file:
                with Printer(linegap=0) as printer:
                    printer.text(f"{info}\n", font_config=printer_font_XL)
                    printer.text(f"TB: {TABLE_NUMBER} . . . . . . {return_member_name()}\n",
                                 font_config=printer_font_XL)
                    printer.text(file.read(), font_config=printer_font_reg)


def check_if_msg(item, id, where):
    where2 = where
    if where == "ORDERED":
        where2 = "PRINTED"
    cursor.execute(
        "SELECT IFNULL(message, 0) FROM messages WHERE (product, prod_id, table_id, status) = (%s,%s,%s,%s)",
        [item, id, TABLE_NUMBER, where2])
    results = cursor.fetchall()
    if len(results) > 0:
        return True
    else:
        return False


def get_msg_for(item, id, where):
    where2 = where
    if where == "ORDERED":
        where2 = "PRINTED"
    cursor.execute("SELECT message FROM messages WHERE (product,prod_id, table_id, status) = (%s,%s,%s,%s)",
                   [item, id, TABLE_NUMBER, where2])
    results = cursor.fetchall()
    return results


def msg_is_printed_for(item, id):
    cursor.execute("UPDATE messages SET status=%s WHERE (product, prod_id, table_id, status) = (%s,%s,%s,%s)",
                   ["PRINTED", item, id, TABLE_NUMBER, "IN BASKET"])


def belongs_to(name, place):
    cursor.execute("SELECT item, belongs_to FROM stock WHERE item = %s && belongs_to = %s", [name, place])
    results = cursor.fetchall()
    if len(results) > 0:
        return True


def to_print():
    global basket, total_price, MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS, total_price_label, CHECK_NUMBER

    sql_selectAll_basket = f"SELECT product, price FROM `basket` WHERE (table_id, status) = (%s,%s)"
    cursor.execute(sql_selectAll_basket, (TABLE_NUMBER, "IN BASKET"))
    all_basket_rows = cursor.fetchall()
    #
    for row in all_basket_rows:
        x = row[0], row[1]
        basket.append(x)
    ##
    check_count()
    print_for_bar('IN BASKET')
    print_for_kitchen('IN BASKET')
    print_for_puds('IN BASKET')
    clear()
    TABLE_NUMBER = 0
    my_listbox.delete(0, END)
    calculate_total()
    basket.clear()
    resume_basket()
    ##
    sql_upd = f"UPDATE basket SET status=%s WHERE table_id = %s"
    cursor.execute(sql_upd, ("ORDERED", TABLE_NUMBER))


def split_calculate_total(status):
    global basket, total_price_label, TABLE_NUMBER, MEMBER_ID, TEMP_BUTTONS
    sql_select_basket = f"SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = %s && status LIKE %s ORDER BY datez ASC"
    cursor.execute(sql_select_basket, [TABLE_NUMBER, f"{status}%"])
    results = cursor.fetchall()
    for row in results:
        total_price_label.destroy()
        get_discount = (float(row[0]) - ((float(row[0]) * float(PRICE_DISCOUNT)) / float(100)))
        x = f"£{get_discount}".replace("£-", "-£")
        total_price_label = LabelButton(f"Left to pay:\n {x}", 5, 1, "white")
        total_price_label.configure(width=15, height=2, pady=9)
        return row[0]


def calculate_total():
    global basket, total_price_label, TABLE_NUMBER, MEMBER_ID, TEMP_BUTTONS, PRICE_DISCOUNT, table_number_label
    sql_select_basket = "SELECT IFNULL(format(sum(price), 2), 0.00) FROM basket WHERE table_id = %s ORDER BY datez ASC"
    cursor.execute(sql_select_basket, [TABLE_NUMBER])
    all_basket_rows = cursor.fetchall()
    for row in all_basket_rows:
        total_price_label.destroy()
        # get_discount = (float(row[0]) - ((float(row[0]) * float(PRICE_DISCOUNT)) / float(100)))
        x = f"£{row[0]}".replace("£-", "-£")
        total_price_label = LabelButton(f"TOTAL:\n {x}", 0, 6, "white")
        total_price_label.configure(width=12, height=2, pady=9, font="Arial 22 bold")

        table_number_label.destroy()
        table_number_label = LabelButton(f"TABLE : {TABLE_NUMBER}", 0, 2, "white")
        table_number_label.configure(width=12, height=2, pady=9, font="Arial 22 bold")
        table_number_label.place(x=0, y=96, width=227, height=95)

        return row[0]


def get_price(product):
    cursor.execute(f"SELECT price FROM stock WHERE item = '{product}'")
    results = cursor.fetchall()
    return results[0][0]


def get_sql_item_price(product, id):
    cursor.execute(f"SELECT `price` FROM `basket` WHERE (`product`,`item_id`) = ('{product}','{id}')")
    results = cursor.fetchall()
    return results[0][0]


def check_count():
    global CHECK_NUMBER, SAME_DAY, SAME_DAY
    cursor.execute(f"SELECT * FROM `check_count`")
    all_basket_rows = cursor.fetchall()
    for row in all_basket_rows:
        if row[1] == SAME_DAY:
            x = row[0]
            x_upd = int(x) + int(1)
            sql_insert = "UPDATE `check_count` SET `count`='%s' WHERE (count,day) = (%s, %s)"
            cursor.execute(sql_insert, (x_upd, x, SAME_DAY))
            CHECK_NUMBER = x_upd
        else:
            y = SAME_DAY
            x = 1
            sql_delete = "DELETE FROM check_count"
            cursor.execute(sql_delete)
            sql_insert = "INSERT INTO `check_count` VALUES (%s, %s)"
            cursor.execute(sql_insert, (x, y))
            CHECK_NUMBER = x


def check_item_status(id):
    cursor.execute("SELECT `status` from `basket` WHERE `item_id` = %s", [id])
    results = cursor.fetchall()
    return results[0][0]


def delete():
    global basket, TEMP_BUTTONS, MEMBER_ID, PRICE_DISCOUNT, waiting_timer
    if my_listbox.get(ANCHOR) and my_listbox.curselection() != ():
        item = my_listbox.get(ANCHOR)
        item = (str(item).split("                                                      "))
        item_status = check_item_status(item[1])
        allowed = ["ADMIN", "OWNER", "MANAGEMENT"]
        if item_status == "ORDERED":

            if check_clearance(return_member_name()) in allowed:
                root.after_cancel(waiting_timer)
                waiting_timer = None

                if str(item[0]).startswith("Discount"):
                    cursor.execute(
                        f"DELETE FROM `basket` WHERE `product` LIKE 'Discount%' && table_id = '{TABLE_NUMBER}'")
                    PRICE_DISCOUNT = 0
                    my_listbox.delete(ANCHOR)
                elif str(item[0]).startswith(" *"):
                    cursor.execute(f"DELETE FROM `messages` WHERE `message` = %s && `prod_id` = %s",
                                   [(item[0])[1:], item[1]])
                    my_listbox.delete(ANCHOR)
                else:
                    cursor.execute(f"DELETE FROM `basket` WHERE item_id = %s ORDER BY datez DESC", [str(item[1])])
                    cursor.execute(f"DELETE FROM `messages` WHERE `prod_id` = %s ORDER BY `timez` DESC", [str(item[1])])
                    mod_stock(item[0], +1)
                    temp_indexx = my_listbox.index(ANCHOR)
                    my_listbox.delete(ANCHOR)
                    if str(my_listbox.get(temp_indexx)).startswith(" *"):
                        my_listbox.delete(temp_indexx)
                for button in TEMP_BUTTONS:
                    button.refresh()
            else:
                root.after_cancel(waiting_timer)
                waiting_timer = None
                messagebox.showerror(title="Access Level Denied!",
                                     message="You are not allowed to do this.\n\nCall a management member.")
        else:
            if str(item[0]).startswith("Discount"):
                cursor.execute(f"DELETE FROM `basket` WHERE `product` LIKE 'Discount%' && table_id = '{TABLE_NUMBER}'")
                PRICE_DISCOUNT = 0
                my_listbox.delete(ANCHOR)
            elif str(item[0]).startswith(" *"):
                cursor.execute(f"DELETE FROM `messages` WHERE `message` = %s && `prod_id` = %s",
                               [(item[0])[1:], item[1]])
                my_listbox.delete(ANCHOR)
            else:
                cursor.execute(f"DELETE FROM `basket` WHERE `item_id` = %s", [str(item[1])])
                cursor.execute(f"DELETE FROM `messages` WHERE `prod_id` = %s", [str(item[1])])
                mod_stock(item[0], +1)
                temp_indexx = my_listbox.index(ANCHOR)
                my_listbox.delete(ANCHOR)
                if str(my_listbox.get(temp_indexx)).startswith(" *"):
                    my_listbox.delete(temp_indexx)
            for button in TEMP_BUTTONS:
                button.refresh()
    calculate_total()


def delete_all():
    global basket, total_price, TABLE_NUMBER, TEMP_BUTTONS, MEMBER_ID, PRICE_DISCOUNT, waiting_timer
    allowed = ["ADMIN", "OWNER", "MANAGEMENT"]
    sql_select_basket = "SELECT `product`, `item_id` FROM `basket` WHERE `table_id` = %s ORDER BY `datez` DESC"
    cursor.execute(sql_select_basket, [TABLE_NUMBER])
    results = cursor.fetchall()
    items_x = []
    for row in results:
        if check_item_status(row[1]) != "ORDERED":
            items_x.append("ALLOWED")
        else:
            items_x.append("DENIED")

    if "DENIED" in items_x:
        if check_clearance(return_member_name()) in allowed:
            for row in results:
                mod_stock(row[0], + 1)
            my_listbox.delete(0, END)
            basket.clear()
            cursor.execute(f"DELETE FROM basket WHERE table_id = %s", [TABLE_NUMBER])
            cursor.execute(f"DELETE FROM messages WHERE table_id = %s", [TABLE_NUMBER])
            TABLE_NUMBER = 0
            PRICE_DISCOUNT = 0
            for button in TEMP_BUTTONS:
                button.refresh()
            calculate_total()
            resume_basket()
        else:
            root.after_cancel(waiting_timer)
            waiting_timer = None
            messagebox.showerror(title="Access Level Denied!",
                                 message="You are not allowed to do this.\n\nCall a management member.")
    else:
        for row in results:
            mod_stock(row[0], + 1)
        my_listbox.delete(0, END)
        basket.clear()
        cursor.execute(f"DELETE FROM basket WHERE table_id = %s", [TABLE_NUMBER])
        cursor.execute(f"DELETE FROM messages WHERE table_id = %s", [TABLE_NUMBER])
        TABLE_NUMBER = 0
        PRICE_DISCOUNT = 0
        for button in TEMP_BUTTONS:
            button.refresh()
        calculate_total()
        resume_basket()
    items_x.clear()


def add():
    global basket, TEMP_BUTTONS, MEMBER_ID, TABLE_NUMBER
    if my_listbox.get(ANCHOR) and my_listbox.curselection() != ():
        item = my_listbox.get(ANCHOR)
        item2 = (str(item).split("                                                      "))
        if int(sql_retrieve_stock(item2[0])) >= 1:
            cursor.execute(
                "INSERT INTO basket(product, price, member_id, table_id, datez, status) VALUES (%s,%s,%s,%s,%s,%s)",
                [item2[0], get_sql_item_price(item2[0], item2[1]), MEMBER_ID, TABLE_NUMBER, time_now(), 'IN BASKET'])
            mod_stock(item2[0], -1)
            my_listbox.insert(END, my_listbox.get(ANCHOR))
            calculate_total()
            for button in TEMP_BUTTONS:
                button.refresh()


def misc_screen_keyboard(item, val):
    global my_listbox, MEMBER_ID, TABLE_NUMBER

    def backspace():
        keyboard_screen.delete(keyboard_screen.index("end") - 1)

    def insert_me(item9, val9):
        if len(keyboard_screen.get()) > 0:
            misc_product(item9, val9, keyboard_screen.get())
        else:
            misc_product(item9, val9, "empty msg")
        kill_keyboard()
        resume_basket()

    def kill_keyboard():
        keyboard_frame.destroy()
        keyboard_screen.destroy()

    keyboard_frame = MyFrame(0, 0, 700, 600, 'lightblue')
    keyboard_frame.grid_configure(rowspan=11, columnspan=10)
    keyboard_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)

    keyboard_screen = Entry(keyboard_frame, width=4, font="Arial 20 bold", justify="center", bd=5, relief=RAISED)
    keyboard_screen.place(x=81, y=85, width=560, height=82)
    keyboard_screen.focus()

    mess = Message(keyboard_frame, text="3.INSERT MESSAGE:", width=300)
    mess.configure(font="Arial 22 bold")
    mess.place(x=180, y=40)

    buttonz = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
               ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
               ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
               ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.']]
    counter = 0
    for r in buttonz:
        for c in r:
            def create(r, c):
                if c == "f" or c == "j":
                    Button(keyboard_frame, relief=RAISED, text=str(c).upper(), padx=20, pady=20,
                           font='Arial 15 bold',
                           bd=5, bg="lightgrey", activebackground="lightgrey",
                           command=lambda: keyboard_screen.insert(END, c.upper())).place(
                        x=(((r.index(c) + 0.4) + counter) * 82), y=(((buttonz.index(r)) + 2) * 89), width=80)
                else:
                    Button(keyboard_frame, relief=RAISED, text=str(c).upper(), padx=20, pady=20,
                           font='Arial 15 bold',
                           bd=5, command=lambda: keyboard_screen.insert(END, c.upper())).place(
                        x=(((r.index(c) + 0.4) + counter) * 82), y=(((buttonz.index(r)) + 2) * 89), width=80)

            create(r, c)
        counter += 0.25
    space = Button(keyboard_frame, relief=RAISED, text="SPACE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                   command=lambda: keyboard_screen.insert(END, " ")).place(x=125, y=535, width=500)
    insertz = Button(keyboard_frame, relief=RAISED, text="SEND", padx=20, pady=30, bd=5, font="Arial 15 bold",
                     bg="lightgreen", activebackground="lightgreen",
                     command=lambda: [insert_me(item, val)]).place(x=625, y=535, width=160)
    backspace = Button(keyboard_frame, relief=RAISED, text="BACKSPACE", padx=20, bd=5, pady=30,
                       font="Arial 15 bold", command=backspace, bg="#F63131", activebackground="#F63131").place(
        x=650, y=85, width=240, height=82)
    # cancelz = Button(keyboard_frame, relief=RAISED, text="X", padx=20, pady=30, bd=5, font="Arial 15 bold",
    #                  command=lambda: [kill_keyboard()]).place(x=790, y=10, width=100, height=50)


def misc_screen():
    global TABLE_NUMBER, MEMBER_ID, my_listbox

    def ok_button(item, val):
        global TABLE_NUMBER, MEMBER_ID, my_listbox
        if float(val) > 0:
            misc_screen_keyboard(item, val)
            kill_keypad()

    def backspace():
        keypad_screen.delete(keypad_screen.index("end") - 1)

    def kill_keypad():
        keypad_screen.destroy()
        keypad_frame.destroy()
        for button in tempz_keypad:
            button.destroy()

    def button_click(number):
        keypad_screen.insert(END, str(number))

    keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, f"{root_bg_color}")
    keypad_frame.grid(row=0, column=0, columnspan=9, rowspan=8)

    mess = Message(keypad_frame, text="1.INSERT PRICE:", width=300)
    mess.configure(font="Arial 22 bold")
    mess.place(x=285, y=100)

    mess2 = Message(keypad_frame, text="2.PRINT TO:", width=300)
    mess2.configure(font="Arial 22 bold")
    mess2.place(x=645, y=100)

    keypad_screen = Entry(root, font="Arial 90 bold", justify="center", width=5)
    keypad_screen.place(x=230, y=150)

    keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5, color="teal")
    keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5, color="teal")
    keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5, color="teal")
    keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4, color="teal")
    keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4, color="teal")
    keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4, color="teal")
    keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3, color="teal")
    keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3, color="teal")
    keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3, color="teal")
    keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6, color="teal")
    keypad_button_backspace = CommandButton(" DEL", backspace, 3, 7, color="#FF2A2A")
    keypad_button_dot = CommandButton(".", lambda: button_click("."), 3, 6, color="teal")
    keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 4, 6, color="white")

    keypad_button_bar = CommandButton("BAR", lambda: [ok_button("BAR", keypad_screen.get())], 6, 2, color="lightgreen")
    keypad_button_starter = CommandButton("STARTER", lambda: [ok_button("STARTER", keypad_screen.get())], 6, 3,
                                          color="#E6EE33")
    keypad_button_main = CommandButton("MAIN", lambda: [ok_button("MAIN", keypad_screen.get())], 6, 4, color="#2D41E2")
    keypad_button_side = CommandButton("SIDE", lambda: [ok_button("SIDE", keypad_screen.get())], 6, 5, color="#ffffca")
    keypad_button_pud = CommandButton("PUD", lambda: [ok_button("PUD", keypad_screen.get())], 6, 6, color="pink")

    tempz_keypad = [keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                    keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                    keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_bar,
                    keypad_button_starter, keypad_button_main, keypad_button_pud, keypad_button_dot, keypad_button_side]


def misc_product(item, price, message):
    global MEMBER_ID, TABLE_NUMBER, my_listbox
    cursor.execute(
        f"INSERT INTO `basket`(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) VALUES (%s, %s, %s, %s, %s, %s)",
        [f"£{price} CUSTOM {item}", f"{price}", MEMBER_ID, TABLE_NUMBER, time_now(), "IN BASKET"])
    cursor.execute("SELECT product, item_id FROM `basket` ORDER BY `datez` DESC LIMIT 1")
    res = cursor.fetchall()
    my_listbox.insert(END,
                      f"£{price} CUSTOM {item}                                                      {str(res[0][1])}")

    # insert msg and display in listbox !!!!!!!
    cursor.execute(
        "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [f"£{price} CUSTOM {item}", str(res[0][1]), MEMBER_ID, TABLE_NUMBER, '*' + message, "IN BASKET", time_now()])
    my_listbox.insert(END, " *" + message)

    calculate_total()


def insert(name):
    global basket, MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS
    if int(sql_retrieve_stock(name)) >= int(1):
        # add here the popup in the future... calling myself an idiot here...
        # if check_if_measure(name) is True:
        #     for button in TEMP_BUTTONS:
        #         if name == button.__repr__():
        #             print("Yes")
        #             button.stock_label = ""
        #     mod_stock(name, -1)
        #     mod_frame = MyFrame(342, 95, 683, 480, "lightgrey")
        #     mod_frame.configure(relief=RAISED)
        #     if type_of_measure(name) == "half/pint":  # x1 / 2,  x1
        #         def set_msg(name2):
        #             if str(v1.get()) == "1":  # full price
        #                 temp_name2 = str('PINT '+str(name2))
        #                 insert_with_price(temp_name2, get_price(name))
        #
        #             elif str(v1.get()) == "0":
        #                 temp_name2 = str('HALF ' + str(name2))
        #                 temp_price2 = round(float(float(get_price(name))/2), 2)
        #                 insert_with_price(temp_name2, temp_price2)
        #
        #             resume_basket()
        #             mod_frame.destroy()
        #
        #         measure_size3 = [("HALF", 0), ("PINT", 1)]
        #         v1 = IntVar()
        #         counter = 25
        #         for var1, val1 in measure_size3:
        #             choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
        #                                   value=val1, selectcolor="#e47831", font="Arial 20 bold", command=lambda: [set_msg(name)])
        #             choice1.place(x=200, y=counter * 4, width=300, height=150)
        #             choice1.deselect()
        #             counter += 50
        #
        #     elif type_of_measure(name) == "25ml/50ml":  # x1 or x2 price
        #         def set_msg(name3):
        #             if str(v1.get()) == "1":
        #                 temp_name2 = str('DOUBLE ' + str(name3))
        #                 temp_price2 = round(float(float(get_price(name))*2), 2)
        #                 insert_with_price(temp_name2, temp_price2)
        #
        #             elif str(v1.get()) == "0":
        #                 temp_name3 = str('SINGLE '+str(name3))
        #                 insert_with_price(temp_name3, get_price(name))
        #             resume_basket()
        #             mod_frame.destroy()
        #
        #         measure_size = [("25ml", 0), ("50ml", 1)]
        #         v1 = IntVar()
        #         counter = 25
        #         for var1, val1 in measure_size:
        #             choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
        #                                   value=val1, selectcolor="#e47831", font="Arial 20 bold", command=lambda: [set_msg(name)])
        #             choice1.place(x=200, y=counter * 4, width=300, height=150)
        #             choice1.deselect()
        #             counter += 50
        #
        #     elif type_of_measure(name) == "125/175/250/btl":  # x1, x1+2£, x1+4£, x1+10£
        #         def set_msg(name4):
        #             if str(v1.get()) == "0":
        #                 temp_name4 = str('125ML ' + str(name4))
        #                 insert_with_price(temp_name4, get_price(name4))
        #             elif str(v1.get()) == "1":
        #                 temp_name5 = str('175ML ' + str(name4))
        #                 temp_price5 = round(float(float(get_price(name4))+2), 2)
        #                 insert_with_price(temp_name5, temp_price5)
        #             elif str(v1.get()) == "2":
        #                 temp_name6 = str('250ML ' + str(name4))
        #                 temp_price6 = round(float(float(get_price(name4))+4), 2)
        #                 insert_with_price(temp_name6, temp_price6)
        #             elif str(v1.get()) == "3":
        #                 temp_name7 = str('BTL ' + str(name4))
        #                 temp_price7 = round(float(float(get_price(name4))+12), 2)
        #                 insert_with_price(temp_name7, temp_price7)
        #             calculate_total()
        #             mod_frame.destroy()
        #
        #         measure_size2 = [("125ml", 0), ("175ml", 1), ("250ml", 2), ("BTL", 3)]
        #         v1 = IntVar()
        #         counter = 25
        #         for var1, val1 in measure_size2:
        #             choice1 = Radiobutton(mod_frame, text=var1, indicatoron=0, width=20, padx=20, variable=v1,
        #                                   value=val1, selectcolor="#e47831", font="Arial 20 bold", command=lambda: [set_msg(name)])
        #             choice1.place(x=200, y=counter * 2, width=300, height=80)
        #             choice1.deselect()
        #             counter += 50

        # else:
        sql_insert = "INSERT INTO `basket`(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql_insert, (name, get_price(name), MEMBER_ID, TABLE_NUMBER, time_now(), "IN BASKET"))
        cursor.execute("SELECT product, item_id FROM `basket` ORDER BY `datez` DESC LIMIT 1")
        res = cursor.fetchall()
        my_listbox.insert(END, str(name) + "                                                      " + str(res[0][1]))
        mod_stock(name, -1)
        calculate_total()


def insert_with_price(name, price):
    global basket, MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS
    # add here the popup in the future... calling myself an idiot here...
    sql_insert = "INSERT INTO `basket`(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql_insert, (name, price, MEMBER_ID, TABLE_NUMBER, time_now(), "IN BASKET"))
    cursor.execute(
        "SELECT item_id FROM `basket` WHERE (`product`,`member_id`,`table_id`) = (%s,%s,%s) ORDER BY `datez` DESC LIMIT 1",
        [name, MEMBER_ID, TABLE_NUMBER])
    res = cursor.fetchall()
    my_listbox.insert(END, str(name) + "                                                      " + str(res[0][0]))
    calculate_total()


def table_number():  # code to be compacted laterz...
    global TABLE_NUMBER, TEMP_BUTTONS, MEMBER_ID, my_listbox

    clear()

    def ok_button(val):
        global TABLE_NUMBER, MEMBER_ID, my_listbox
        if val != "":
            my_listbox.delete(0, END)
            kill_keypad()
            TABLE_NUMBER = val
            resume_basket()
            calculate_total()
            return val

    def backspace():
        keypad_screen.delete(keypad_screen.index("end") - 1)

    def kill_keypad():
        keypad_screen.destroy()
        keypad_frame.destroy()
        for button in tempz_keypad:
            button.destroy()

    def button_click(number):
        keypad_screen.insert(END, str(number))

    keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    keypad_frame.grid(row=0, column=0, columnspan=9, rowspan=8)

    keypad_screen = Entry(root, font="Arial 90 bold", justify="center", width=5)
    keypad_screen.place(x=230, y=85, height=200)

    keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5, color="teal")
    keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5, color="teal")
    keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5, color="teal")
    keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4, color="teal")
    keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4, color="teal")
    keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4, color="teal")
    keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3, color="teal")
    keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3, color="teal")
    keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3, color="teal")
    keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6, color="teal")
    keypad_button_backspace = CommandButton(" DEL", backspace, 3, 6, color="#FF2A2A")
    keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 4, 6, color="white")
    keypad_button_OK = CommandButton("OK", lambda: [ok_button(keypad_screen.get())], 5, 3, color="lightgreen")

    tempz_keypad = [keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                    keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                    keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_OK]


def left_to_pay(status_pass2):
    global temp_label, TABLE_NUMBER

    temp_label.destroy()
    sql_select_basket = f"SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = %s && status LIKE %s ORDER BY datez ASC"
    cursor.execute(sql_select_basket, [TABLE_NUMBER, f"{status_pass2}%"])
    left_to_payz = cursor.fetchall()
    temp_label = LabelButton(f"Left to pay: £{(float(str(left_to_payz[0][0]).replace(',', '')))}", 5, 2)
    temp_label.place(x=550, y=200, width=300, height=100)
    return float(str(left_to_payz[0][0]).replace(',', ''))


def split_payment_types(status_pass1):
    global my_listbox, TEMP_BUTTONS, TEMP_BUTTONS2, TABLE_NUMBER, MEMBER_ID, PRICE_DISCOUNT

    cursor.execute(f"SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = {TABLE_NUMBER}")
    checkifthereissomethingtopay = ((cursor.fetchall())[0][0])
    if float(str(checkifthereissomethingtopay).replace(",", "")) > float(0):

        def pay_by_cash(status_pass2):
            global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, total_price_label

            def end_screen(status_pass4, card_total3):
                global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, TEMP_BUTTONS, temp_total_label

                def delete_this(status_pass5):
                    global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, TEMP_BUTTONS, total_price, temp_total_label

                    cursor.execute(
                        "DELETE FROM basket WHERE (member_id, table_id) = (%s,%s) && status LIKE %s",
                        (MEMBER_ID, TABLE_NUMBER, f"{status_pass5}%"))
                    if str(status_pass5) == "SPLIT BILL 0":
                        calculate_total()
                        resume_basket()
                    clear()

                cursor.execute("UPDATE basket SET status=%s WHERE (member_id, table_id) = (%s,%s) && status = %s",
                               (f"{status_pass4} PAID BY CASH", MEMBER_ID, TABLE_NUMBER, status_pass4))

                # -----------
                cursor.execute(
                    "INSERT INTO orders_placed(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) SELECT `product`, `price`, `member_id`, `table_id`, `datez`, `status` FROM basket WHERE (member_id, table_id, status) = (%s, %s, %s)",
                    [MEMBER_ID, TABLE_NUMBER, f"{status_pass4} PAID BY CASH"])

                cursor.execute("DELETE FROM messages WHERE (member_id, table_id) = (%s,%s)", [MEMBER_ID, TABLE_NUMBER])

                amountID = int(card_total3)
                uniq_ref = generate_unique_ref_number(MEMBER_ID, TABLE_NUMBER, amountID)
                cursor.execute(
                    "UPDATE `orders_placed` SET `uniq_ref`= %s WHERE (`uniq_ref`, `member_id`, `table_id`) = (%s,%s,%s) ",
                    [uniq_ref, 'X', MEMBER_ID, TABLE_NUMBER])
                # -----------
                payment_frame = MyFrame(3, 1, 680, 800, root_bg_color)
                payment_frame.place(x=340, y=0, width=690, height=800)
                if float(left_to_pay(status_pass4)) != 0:
                    temp_label = LabelButton(f"Change: £{-(float(left_to_pay(status_pass4)))}", 5, 2)
                    temp_label.place(x=550, y=200, width=300, height=100)
                    open_drawer("NEED CHANGE")
                but1 = CommandButton("DONE!",
                                     lambda: [clear_LABEL(), delete_this(status_pass4), payment_frame.destroy(),
                                              but1.destroy(),
                                              but2.destroy()], 6, 5)
                but2 = CommandButton("Need receipt?", lambda: [print_bill_split(status_pass4, uniq_ref), clear_LABEL(),
                                                               delete_this(status_pass4), payment_frame.destroy(),
                                                               but1.destroy(),
                                                               but2.destroy()], 6, 6)
                but1.configure(font="Arial 14 bold")
                but2.configure(font="Arial 14 bold")
                but1.place(x=550, y=500, width=300, height=100)
                but2.place(x=550, y=600, width=300, height=100)
                temp_buts = [but1, but2]

            def backspace():
                coins_entry.delete(coins_entry.index("end") - 1)

            def button_click(number):
                coins_entry.insert(END, str(number))

            def remove_payment_buttons(status_pass3):
                global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, total_price_label
                coins_entry.destroy()
                payment_frame.destroy()

                for button in tempz_keypad:
                    button.destroy()
                cursor.execute(
                    "DELETE FROM basket WHERE (member_id, table_id) = (%s,%s) AND status LIKE %s ORDER BY datez ASC",
                    [MEMBER_ID, TABLE_NUMBER, f'{status_pass3} CASHZ'])

            def cash_value(value, status_pass3, card_total2):
                global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, STATUS, TEMP_BUTTONS, total_price_label, temp_label

                current_status = status_pass3 + " CASHZ"
                cursor.execute(
                    "INSERT INTO basket(product, price, member_id, table_id, datez, status) VALUES (%s,%s,%s,%s,%s,%s)",
                    [("-£" + str(value)), -value, MEMBER_ID, TABLE_NUMBER, time_now(), current_status])
                coins_entry.delete(0, END)

                if str(status_pass3) == "SPLIT BILL 0":
                    calculate_total()
                if float(left_to_pay(status_pass3)) <= 0:  # if total is paid or overpaid:
                    coins_entry.destroy()
                    payment_frame.destroy()

                    for button in tempz_keypad:
                        button.destroy()
                    end_screen(status_pass3, card_total2)

                # ----

            def revertz(status_passx):
                cursor.execute("UPDATE basket SET status='ORDERED' WHERE table_id = %s", [TABLE_NUMBER])

            payment_frame = MyFrame(3, 1, 680, 800, root_bg_color)
            payment_frame.place(x=340, y=0, width=690, height=800)

            coins_entry = tk.Entry(payment_frame, font="Arial 25 bold", justify="center")
            coins_entry.place(x=155, y=350, width=400)
            coins_entry.focus()
            # sql_select_basket = f"SELECT IFNULL(format(sum(price), 2), 0) FROM basket WHERE table_id = %s && status LIKE %s ORDER BY datez ASC"
            # cursor.execute(sql_select_basket, [TABLE_NUMBER, f"{status_pass2}%"])
            # left_to_pay = cursor.fetchall()

            left_to_pay(status_pass2)
            card_total1 = left_to_pay(status_pass2)
            a1 = Button(payment_frame, text="£5", command=lambda: [cash_value(5, status_pass2, card_total1)])
            a2 = Button(payment_frame, text="£10", command=lambda: [cash_value(10, status_pass2, card_total1)])
            a3 = Button(payment_frame, text="£20", command=lambda: [cash_value(20, status_pass2, card_total1)])
            a4 = Button(payment_frame, text="CANCEL",
                        command=lambda: [temp_label.destroy(), remove_payment_buttons(status_pass2),
                                         revertz(status_pass2)])
            a5 = Button(payment_frame, text="OK",
                        command=lambda: [temp_label.destroy(),
                                         cash_value(float(coins_entry.get()), status_pass2, card_total1)],
                        bg="lightgreen")

            keypad_button_7 = Button(payment_frame, text="7", command=lambda: button_click(7), bg="teal")
            keypad_button_8 = Button(payment_frame, text="8", command=lambda: button_click(8), bg="teal")
            keypad_button_9 = Button(payment_frame, text="9", command=lambda: button_click(9), bg="teal")
            keypad_button_4 = Button(payment_frame, text="4", command=lambda: button_click(4), bg="teal")
            keypad_button_5 = Button(payment_frame, text="5", command=lambda: button_click(5), bg="teal")
            keypad_button_6 = Button(payment_frame, text="6", command=lambda: button_click(6), bg="teal")
            keypad_button_1 = Button(payment_frame, text="1", command=lambda: button_click(1), bg="teal")
            keypad_button_2 = Button(payment_frame, text="2", command=lambda: button_click(2), bg="teal")
            keypad_button_3 = Button(payment_frame, text="3", command=lambda: button_click(3), bg="teal")

            keypad_button_0 = Button(payment_frame, text="0", command=lambda: button_click(0), bg="teal")
            keypad_button_dot = Button(payment_frame, text=".", command=lambda: button_click("."), bg="teal")
            keypad_button_backspace = Button(payment_frame, text=" DEL", command=backspace, bg="#FF2A2A")

            a1.place(x=100, y=400, width=100, height=90)
            a2.place(x=100, y=490, width=100, height=90)
            a3.place(x=100, y=580, width=100, height=90)
            a4.place(x=506, y=670, width=100, height=90)
            a5.place(x=506, y=580, width=100, height=90)
            a1.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            a2.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            a3.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            a4.configure(font="Arial 15 bold", bd=4, relief=RAISED)
            a5.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_7.place(x=200, y=400, width=100, height=90)
            keypad_button_8.place(x=302, y=400, width=100, height=90)
            keypad_button_9.place(x=404, y=400, width=100, height=90)
            keypad_button_4.place(x=200, y=490, width=100, height=90)
            keypad_button_5.place(x=302, y=490, width=100, height=90)
            keypad_button_6.place(x=404, y=490, width=100, height=90)
            keypad_button_1.place(x=200, y=580, width=100, height=90)
            keypad_button_2.place(x=302, y=580, width=100, height=90)
            keypad_button_3.place(x=404, y=580, width=100, height=90)
            keypad_button_0.place(x=200, y=670, width=100, height=90)
            keypad_button_dot.place(x=302, y=670, width=100, height=90)
            keypad_button_backspace.place(x=404, y=670, width=100, height=90)
            keypad_button_7.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_8.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_9.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_4.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_5.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_6.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_1.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_2.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_3.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_0.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_dot.configure(font="Arial 30 bold", bd=4, relief=RAISED)
            keypad_button_backspace.configure(font="Arial 20 bold", bd=4, relief=RAISED)
            tempz_keypad = [a1, a2, a3, a4, a5, keypad_button_dot, keypad_button_1, keypad_button_2, keypad_button_3,
                            keypad_button_4,
                            keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                            keypad_button_0, keypad_button_backspace]

        def pay_by_card(status_pass2):
            global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, total_price_label, temp_label

            def card_value(status_pass3, card_total):
                global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, total_price_label, temp_label

                def finish_card_payment(status_pass4):
                    global my_listbox, temp_label

                    temp_label.destroy()
                    cursor.execute("DELETE FROM basket WHERE (member_id, table_id) = (%s,%s) && status LIKE %s",
                                   (MEMBER_ID, TABLE_NUMBER, f"{status_pass3}%"))
                    if str(status_pass4).startswith("SPLIT BILL 0"):
                        my_listbox.delete(0, END)
                        resume_basket()
                    clear()

                current_card_status = status_pass3 + " CARDZ"
                cursor.execute(
                    "INSERT INTO basket(product, price, member_id, table_id, datez, status) VALUES (%s,%s,%s,%s,%s,%s)",
                    ['-£' + str(card_total), '-' + str(card_total), MEMBER_ID, TABLE_NUMBER, time_now(),
                     current_card_status])

                cursor.execute("UPDATE basket SET status=%s WHERE (member_id, table_id) = (%s,%s) && status = %s",
                               [f"{status_pass3} PAID BY CARD", MEMBER_ID, TABLE_NUMBER, status_pass3])
                cursor.execute(
                    "INSERT INTO orders_placed(`product`, `price`, `member_id`, `table_id`, `datez`, `status`) SELECT `product`, `price`, `member_id`, `table_id`, `datez`, `status` FROM basket WHERE (member_id, table_id, status) = (%s, %s, %s)",
                    (MEMBER_ID, TABLE_NUMBER, f"{status_pass3} PAID BY CARD"))

                cursor.execute("DELETE FROM messages WHERE (member_id, table_id) = (%s,%s)", [MEMBER_ID, TABLE_NUMBER])

                amountID = int(card_total)
                uniq_ref = generate_unique_ref_number(MEMBER_ID, TABLE_NUMBER, amountID)
                cursor.execute(
                    "UPDATE `orders_placed` SET `uniq_ref`= %s WHERE (`uniq_ref`, `member_id`, `table_id`) = (%s,%s,%s) ",
                    [uniq_ref, 'X', MEMBER_ID, TABLE_NUMBER])

                but1 = CommandButton("DONE!",
                                     lambda: [but1.destroy(), but2.destroy(), payment_frame.destroy(),
                                              finish_card_payment(status_pass3)], 6, 5)
                but2 = CommandButton("Need receipt?",
                                     lambda: [print_bill_split(status_pass3, uniq_ref), but1.destroy(), but2.destroy(),
                                              payment_frame.destroy(), finish_card_payment(status_pass3)], 6, 6)
                but1.configure(font="Arial 14 bold")
                but2.configure(font="Arial 14 bold")
                but1.place(x=550, y=500, width=300, height=100)
                but2.place(x=550, y=600, width=300, height=100)
                temp_buts = [but1, but2]

            def remove_payment_buttons(status_pass3):
                global MEMBER_ID, TABLE_NUMBER, TEMP_BUTTONS2, total_price_label
                payment_frame.destroy()
                for button in tempz_keypad:
                    button.destroy()
                cursor.execute(
                    "DELETE FROM basket WHERE (member_id, table_id) = (%s,%s) AND status LIKE %s ORDER BY datez ASC",
                    [MEMBER_ID, TABLE_NUMBER, f'{status_pass3} CARDZ'])

            def revertz(status_passx):
                cursor.execute("UPDATE basket SET status='ORDERED' WHERE table_id = %s", [TABLE_NUMBER])

            payment_frame = MyFrame(3, 1, 680, 800, root_bg_color)
            payment_frame.place(x=340, y=0, width=690, height=800)

            left_to_pay(status_pass2)

            send_payment_to_machine = CommandButton("CLICK HERE TO CONFIRM\nTHAT YOU HAVE TAKEN\nTHE PAYMENT",
                                                    lambda: [temp_label.destroy(), a4.destroy(),
                                                             send_payment_to_machine.destroy(),
                                                             card_value(status_pass2, left_to_pay(status_pass2))], 0, 0)
            send_payment_to_machine.place(x=540, y=400, width=300, height=100)
            a4 = Button(payment_frame, text="CANCEL",
                        command=lambda: [temp_label.destroy(), remove_payment_buttons(status_pass2),
                                         revertz(status_pass2)])
            a4.configure(font="Arial 15 bold", bd=4, relief=RAISED)
            a4.place(x=506, y=670, width=100, height=90)

            tempz_keypad = [send_payment_to_machine, a4]

        def pay_by_voucher(status_pass2):
            return

        def remove_payment_buttons():
            cash.destroy()
            card.destroy()
            voucher.destroy()
            cancelz.destroy()
            payment_frame.destroy()

        def revertz(status_passx):
            cursor.execute("UPDATE basket SET status='ORDERED' WHERE table_id = %s", [TABLE_NUMBER])

        if str(status_pass1) == "SPLIT BILL 0":
            cursor.execute("UPDATE basket SET status='SPLIT BILL 0' WHERE table_id = %s", [TABLE_NUMBER])

        payment_frame = MyFrame(3, 1, 680, 800, root_bg_color)
        payment_frame.place(x=340, y=0, width=690, height=800)

        cash = CommandButton("CASH", lambda: [remove_payment_buttons(), pay_by_cash(status_pass1)], 5, 2)
        cash.configure(font="Arial 10 bold", width=30)

        card = CommandButton("CARD", lambda: [remove_payment_buttons(), pay_by_card(status_pass1)], 5, 3)
        card.configure(font="Arial 10 bold", width=30)

        voucher = CommandButton("VOUCHER", lambda: [remove_payment_buttons(), pay_by_voucher(status_pass1)], 5, 4)
        voucher.configure(state=DISABLED, font="Arial 10 bold", width=30)

        cancelz = CommandButton("CANCEL",
                                lambda: [remove_payment_buttons(), payment_frame.destroy(), revertz(status_pass1)], 5,
                                5)
        cancelz.configure(font="Arial 10 bold", width=30)


def split_bill_screen():
    global my_listbox, TEMP_BUTTONS, TEMP_BUTTONS2, TABLE_NUMBER, MEMBER_ID, PRICE_DISCOUNT

    def move_to(list_first, list_second, SQLfirst, SQLsecond):
        selection = list_first.curselection()
        for index in selection[::-1]:
            list_second.insert(END, list_first.get(index))
            tempitem = list_first.get(index)
            xtempitem = (str(tempitem).split("                                                      "))
            cursor.execute(f"UPDATE basket SET status='SPLIT BILL {SQLsecond}' WHERE item_id = '{str(xtempitem[1])}'")
            list_first.delete(index)

    def split_bill_buttons():

        CommandButton("MOVE RIGHT\n>>>>>", lambda: move_to(listbox1, listbox2, 1, 2), 1, 1, color="#add8e6",
                      image=PhotoImage(file="icons/arrow_right.png")).place(x=200, y=100)
        CommandButton("MOVE LEFT\n<<<<<<", lambda: move_to(listbox2, listbox1, 2, 1), 4, 1, color="#add8e6",
                      image=PhotoImage(file="icons/arrow_left.png")).place(x=405, y=100)
        CommandButton("MOVE RIGHT\n>>>>>", lambda: move_to(listbox2, listbox3, 2, 3), 5, 1, color="#add8e6",
                      image=PhotoImage(file="icons/arrow_right.png")).place(x=520, y=100)
        CommandButton("MOVE LEFT\n<<<<<<", lambda: move_to(listbox3, listbox2, 3, 2), 9, 1, color="#add8e6",
                      image=PhotoImage(file="icons/arrow_left.png")).place(x=735, y=100)

        CommandButton("PRINT\nBILL", lambda: print_bill_split("SPLIT BILL 1"), 1, 9, color="#ffaec8",
                      image=PhotoImage(file="icons/printbill.png")).place(x=85, y=600)
        CommandButton("PRINT\nBILL", lambda: print_bill_split("SPLIT BILL 2"), 4, 9, color="#ffaec8",
                      image=PhotoImage(file="icons/printbill.png")).place(x=405, y=600)
        CommandButton("PRINT\nBILL", lambda: print_bill_split("SPLIT BILL 3"), 8, 9, color="#ffaec8",
                      image=PhotoImage(file="icons/printbill.png")).place(x=735, y=600)

        CommandButton("PAY\nBILL", lambda: [split_payment_types("SPLIT BILL 1"), listbox1.delete(0, END)], 2, 9).place(
            x=200, y=600)
        CommandButton("PAY\nBILL", lambda: [split_payment_types("SPLIT BILL 2"), listbox2.delete(0, END)], 5, 9).place(
            x=520, y=600)
        CommandButton("PAY\nBILL", lambda: [split_payment_types("SPLIT BILL 3"), listbox3.delete(0, END)], 9, 9).place(
            x=853, y=600)

        CommandButton("<BACK", lambda: [splitscreen_frame.destroy(), clear_cmd(),
                                        clear(), clear_table_number(), login(), revert_bill()], 8, 0).configure(
            width=10)

    def revert_bill():
        cursor.execute(
            "UPDATE basket SET status='ORDERED' WHERE table_id = %s && (status = 'SPLIT BILL 2' OR status = 'SPLIT BILL 1' OR status = 'SPLIT BILL 3'OR status = 'SPLIT BILL 0') && status NOT LIKE %s",
            [TABLE_NUMBER, '%CASHZ'])

    cursor.execute(f"DELETE FROM basket WHERE product LIKE 'Discount%' && table_id = '{TABLE_NUMBER}'")
    PRICE_DISCOUNT = 0

    old_listbox = []
    for item in my_listbox.get(0, END):
        if not str(item).startswith("Discount"):
            old_listbox.append(item)
    cursor.execute(
        "UPDATE basket SET status='SPLIT BILL 2' WHERE table_id = %s && status NOT LIKE %s",
        [TABLE_NUMBER, '%CASHZ'])

    # -----------
    splitscreen_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    splitscreen_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)

    scrollbar1 = Scrollbar(root, orient=VERTICAL)
    listbox1 = Listbox(root, selectbackground="grey", yscrollcommand=scrollbar1.set, selectmode=MULTIPLE)

    listbox1.place(x=50, y=200, width=300, height=384)
    # listbox1.grid(row=0, column=0, sticky="nw", rowspan=15, columnspan=10)
    scrollbar1.config(command=listbox1.yview)
    scrollbar1.place(x=290, y=200, height=384)
    listbox1.grid_propagate()
    listbox1.propagate()
    listbox1.configure(font="Arial 24 bold", bg="white", activestyle="none")
    # -----------
    scrollbar2 = Scrollbar(root, orient=VERTICAL)
    listbox2 = Listbox(root, selectbackground="grey", yscrollcommand=scrollbar2.set, selectmode=MULTIPLE)
    listbox2.place(x=375, y=200, width=300, height=384)
    scrollbar2.config(command=listbox2.yview)
    scrollbar2.place(x=615, y=200, height=384)
    listbox2.grid_propagate()
    listbox2.propagate()
    listbox2.configure(font="Arial 24 bold", bg="white", activestyle="none")
    # -----------
    scrollbar3 = Scrollbar(root, orient=VERTICAL)
    listbox3 = Listbox(root, selectbackground="grey", yscrollcommand=scrollbar3.set, selectmode=MULTIPLE)
    listbox3.place(x=700, y=200, width=300, height=384)
    scrollbar3.config(command=listbox3.yview)
    scrollbar3.place(x=940, y=200, height=384)
    listbox3.grid_propagate()
    listbox3.propagate()
    listbox3.configure(font="Arial 24 bold", bg="white", activestyle="none")
    # -----------
    temp_items = [listbox1, listbox2, listbox3, scrollbar3, scrollbar2, scrollbar1]

    # -----------

    split_bill_buttons()
    for item in old_listbox:
        if not str(item).startswith("Table"):
            if not str(item).startswith(" *"):
                listbox2.insert(END, item)


def insert_discount(value):
    global PRICE_DISCOUNT, my_listbox, MEMBER_ID, TABLE_NUMBER
    cursor.execute("DELETE FROM basket WHERE product LIKE 'Discount%'")
    PRICE_DISCOUNT = int(value)
    item = my_listbox.get(0, END)
    counter = 0
    for x in item:
        if str(x).startswith("Discount"):
            my_listbox.delete(counter)
        counter += 1
    my_listbox.insert(END, f"Discount:{value}%")

    sql_select_basket = "SELECT IFNULL(format(sum(price), 2), 0.00) FROM basket WHERE table_id = %s ORDER BY datez ASC"
    cursor.execute(sql_select_basket, [TABLE_NUMBER])
    all_basket_rows = cursor.fetchall()
    get_discount = 0
    for row in all_basket_rows:
        get_discount = (float(row[0]) * float(PRICE_DISCOUNT)) / float(100)

    cursor.execute("INSERT INTO basket(product, price, member_id, table_id, datez, status) VALUES (%s,%s,%s,%s,%s,%s)",
                   [f'Discount:{value}%', -float(get_discount), MEMBER_ID, TABLE_NUMBER, time_now(), 'CASHZ'])
    calculate_total()

    # sql_insert = "INSERT INTO basket(product, price, member_id, table_id, datez, status) VALUES (%s,%s,%s,%s,%s,%s)", [("-£" + str(value)), -value, MEMBER_ID, TABLE_NUMBER, time_now(), "CASH"])"
    # cursor.execute(sql_insert, (name, price, MEMBER_ID, TABLE_NUMBER, time_now(), "IN BASKET"))


def clear_table_number():
    global TABLE_NUMBER
    TABLE_NUMBER = 0
    basket.clear()


def keypad():
    global TABLE_NUMBER, MEMBER_ID, my_listbox

    def ok_button(val):
        global TABLE_NUMBER, MEMBER_ID, my_listbox
        if val != "":
            cursor.execute("UPDATE basket SET table_id = %s WHERE table_id= %s",
                           [val, TABLE_NUMBER])
            my_listbox.delete(0, END)
            kill_keypad()
            TABLE_NUMBER = val
            resume_basket()
            calculate_total()
            return val

    def backspace():
        keypad_screen.delete(keypad_screen.index("end") - 1)

    def kill_keypad():
        keypad_screen.destroy()
        keypad_frame.destroy()
        for button in tempz_keypad:
            button.destroy()

    def button_click(number):
        keypad_screen.insert(END, str(number))

    keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    keypad_frame.grid(row=0, column=0, columnspan=9, rowspan=8)

    keypad_screen = Entry(root, font="Arial 90 bold", justify="center", width=5)
    keypad_screen.place(x=230, y=85, height=200)

    keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5, color="teal")
    keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5, color="teal")
    keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5, color="teal")
    keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4, color="teal")
    keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4, color="teal")
    keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4, color="teal")
    keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3, color="teal")
    keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3, color="teal")
    keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3, color="teal")
    keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6, color="teal")
    keypad_button_backspace = CommandButton(" DEL", backspace, 3, 6, color="#FF2A2A")
    keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 4, 6, color="white")
    keypad_button_OK = CommandButton("OK", lambda: [ok_button(keypad_screen.get())], 5, 3, color="lightgreen")

    tempz_keypad = [keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                    keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                    keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_OK]


def transfer_table():
    global MEMBER_ID, TABLE_NUMBER, REAL_PRINT

    def ok_button(val):
        global TABLE_NUMBER, MEMBER_ID, my_listbox
        if val != "":
            info = str(now.strftime("%H:%M"))
            print()
            print("*PRINTING FOR ALL - ADMIN CHECK MODE")
            print()
            print(f"{info}   {return_member_name()}")
            # print(f"TB: {bold_text(TABLE_NUMBER)} >MOVED TO> TB: {bold_text(val)}")
            print("  *** TABLE TRANSFER ***")
            print(f"                {TABLE_NUMBER}  TO  {val}\n")
            print()
            print()
            cursor.execute("UPDATE basket SET table_id = %s WHERE table_id= %s", [val, TABLE_NUMBER])
            cursor.execute("UPDATE messages SET table_id = %s WHERE table_id= %s && status = 'IN BASKET'",
                           [val, TABLE_NUMBER])
            temp_transfer_table = open("temp_transfer_table.txt", "w")
            with temp_transfer_table as file:
                file.write(f"{info}   {return_member_name()}\n")
                file.write("  *** TABLE TRANSFER ***\n")
                file.write(f"               {TABLE_NUMBER}  TO  {val}\n")

            if REAL_PRINT:
                with open("temp_transfer_table.txt", "r") as file:
                    with Printer(linegap=0) as printer:
                        # printer.text(f"{info}\n", font_config=printer_font_XL)
                        # printer.text(f"TB: {TABLE_NUMBER} . . . . . . {return_member_name()}\n",
                        #              font_config=printer_font_XL)
                        printer.text(file.read(), font_config=printer_font_reg)

            my_listbox.delete(0, END)
            kill_keypad()
            TABLE_NUMBER = val
            resume_basket()
            calculate_total()
            return val

    def backspace():
        keypad_screen.delete(keypad_screen.index("end") - 1)

    def kill_keypad():
        keypad_screen.destroy()
        keypad_frame.destroy()
        for button in tempz_keypad:
            button.destroy()

    def button_click(number):
        keypad_screen.insert(END, str(number))

    keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    keypad_frame.grid(row=0, column=0, columnspan=9, rowspan=8)

    mess = Message(keypad_frame, text="TRANSFER TO TABLE:", width=400)
    mess.configure(font="Arial 22 bold")
    mess.place(x=230, y=30)

    keypad_screen = Entry(root, font="Arial 90 bold", justify="center", width=5)
    keypad_screen.place(x=230, y=85, height=200)

    keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5, color="teal")
    keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5, color="teal")
    keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5, color="teal")
    keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4, color="teal")
    keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4, color="teal")
    keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4, color="teal")
    keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3, color="teal")
    keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3, color="teal")
    keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3, color="teal")
    keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6, color="teal")
    keypad_button_backspace = CommandButton(" DEL", backspace, 3, 6, color="#FF2A2A")
    keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 4, 6, color="white")
    keypad_button_OK = CommandButton("OK", lambda: [ok_button(keypad_screen.get())], 5, 3, color="lightgreen")

    tempz_keypad = [keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                    keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                    keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_OK]


def add_msg():
    global my_listbox, MEMBER_ID, TABLE_NUMBER
    product_listbox = my_listbox.get(ANCHOR)
    product_listbox = (str(product_listbox).split("                                                      "))
    if len(str(my_listbox.get(ANCHOR))) > 0:
        def backspace():
            keyboard_screen.delete(keyboard_screen.index("end") - 1)

        def insert_me():
            if len(keyboard_screen.get()) > 1:
                cursor.execute(
                    "INSERT INTO `messages`(`product`, `prod_id`, `member_id`, `table_id`, `message`, `status`, `timez`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    [str(product_listbox[0]), str(product_listbox[1]), MEMBER_ID, TABLE_NUMBER,
                     '*' + keyboard_screen.get(), "IN BASKET", time_now()])
                a_index = (my_listbox.get(0, END).index(my_listbox.get(ANCHOR)))
                my_listbox.insert(a_index + 1,
                                  f" *{keyboard_screen.get()}                                                      {str(product_listbox[1])}")

        def kill_keyboard():
            keyboard_frame.destroy()
            keyboard_screen.destroy()

        keyboard_frame = MyFrame(0, 0, 700, 600, 'lightblue')
        keyboard_frame.grid_configure(rowspan=11, columnspan=10)
        keyboard_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)

        keyboard_screen = Entry(keyboard_frame, width=4, font="Arial 20 bold", justify="center", bd=5, relief=RAISED)
        keyboard_screen.place(x=81, y=85, width=560, height=82)
        keyboard_screen.focus()
        buttonz = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                   ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                   ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                   ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.']]
        counter = 0
        for r in buttonz:
            for c in r:
                def create(r, c):
                    if c == "f" or c == "j":
                        Button(keyboard_frame, relief=RAISED, text=str(c).upper(), padx=20, pady=20,
                               font='Arial 15 bold',
                               bd=5, bg="lightgrey", activebackground="lightgrey",
                               command=lambda: keyboard_screen.insert(END, c.upper())).place(
                            x=(((r.index(c) + 0.4) + counter) * 82), y=(((buttonz.index(r)) + 2) * 89), width=80)
                    else:
                        Button(keyboard_frame, relief=RAISED, text=str(c).upper(), padx=20, pady=20,
                               font='Arial 15 bold',
                               bd=5, command=lambda: keyboard_screen.insert(END, c.upper())).place(
                            x=(((r.index(c) + 0.4) + counter) * 82), y=(((buttonz.index(r)) + 2) * 89), width=80)

                create(r, c)
            counter += 0.25
        space = Button(keyboard_frame, relief=RAISED, text="SPACE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                       command=lambda: keyboard_screen.insert(END, " ")).place(x=125, y=535, width=500)
        insertz = Button(keyboard_frame, relief=RAISED, text="SEND", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="lightgreen", activebackground="lightgreen",
                         command=lambda: [insert_me(), kill_keyboard()]).place(x=625, y=535, width=160)
        backspace = Button(keyboard_frame, relief=RAISED, text="BACKSPACE", padx=20, bd=5, pady=30,
                           font="Arial 15 bold", command=backspace, bg="#F63131", activebackground="#F63131").place(
            x=650, y=85, width=240, height=82)
        cancelz = Button(keyboard_frame, relief=RAISED, text="X", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         command=lambda: [kill_keyboard()]).place(x=790, y=10, width=100, height=50)

        custom1 = Button(keyboard_frame, relief=RAISED, text="BLUE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="#D10000", activebackground="#D10000",
                         command=lambda: keyboard_screen.insert(END, "1 BLUE")).place(x=25, y=650, width=100,
                                                                                      height=105)
        custom2 = Button(keyboard_frame, relief=RAISED, text="RARE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="#DF1F36", activebackground="#DF1F36",
                         command=lambda: keyboard_screen.insert(END, "1 RARE")).place(x=130, y=650, width=100,
                                                                                      height=105)
        custom3 = Button(keyboard_frame, relief=RAISED, text="MED\nRARE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="#C12336", activebackground="#C12336",
                         command=lambda: keyboard_screen.insert(END, "1 MED-RARE")).place(x=235, y=650, width=100,
                                                                                          height=105)
        custom4 = Button(keyboard_frame, relief=RAISED, text="MEDIUM", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="#AC3240", activebackground="#AC3240",
                         command=lambda: keyboard_screen.insert(END, "1 MEDIUM")).place(x=340, y=650, width=100,
                                                                                        height=105)
        custom5 = Button(keyboard_frame, relief=RAISED, text="MED\nWELL", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="#810000", activebackground="#810000",
                         command=lambda: keyboard_screen.insert(END, "1 MED-WELL")).place(x=445, y=650, width=100,
                                                                                          height=105)
        custom6 = Button(keyboard_frame, relief=RAISED, text="WELL\nDONE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="#56272C", activebackground="#56272C",
                         command=lambda: keyboard_screen.insert(END, "1 WELLDONE")).place(x=550, y=650, width=100,
                                                                                          height=105)
        custom7 = Button(keyboard_frame, relief=RAISED, text="ALL\nTOG.", padx=20, pady=30, bd=5, font="Arial 15 bold",
                         bg="white", activebackground="white",
                         command=lambda: keyboard_screen.insert(END, "ALL TOGETHER")).place(x=655, y=650, width=100,
                                                                                            height=105)
        custom14 = Button(keyboard_frame, relief=RAISED, text="KIDS\nW/\nSTARTERS", padx=20, pady=30, bd=5,
                          font="Arial 15 bold",
                          bg="white", activebackground="white",
                          command=lambda: keyboard_screen.insert(END, "KIDS W/ STARTERS")).place(x=760, y=650,
                                                                                                 width=100,
                                                                                                 height=105)
        custom8 = Button(keyboard_frame, relief=RAISED, text="DAIRY\nALLERGY", padx=20, pady=30, bd=5,
                         font="Arial 15 bold",
                         bg="white", activebackground="white",
                         command=lambda: keyboard_screen.insert(END, "1 DAIRY ALLERGY")).place(x=900, y=180, width=110,
                                                                                               height=105)
        custom9 = Button(keyboard_frame, relief=RAISED, text="GLUTEN\nALLERGY", padx=20, pady=30, bd=5,
                         font="Arial 15 bold",
                         bg="white", activebackground="white",
                         command=lambda: keyboard_screen.insert(END, "1 GLUTEN ALLERGY")).place(x=900, y=290,
                                                                                                width=110,
                                                                                                height=105)
        custom15 = Button(keyboard_frame, relief=RAISED, text="NUT\nALLERGY", padx=20, pady=30, bd=5,
                          font="Arial 15 bold",
                          bg="white", activebackground="white",
                          command=lambda: keyboard_screen.insert(END, "1 NUT ALLERGY")).place(x=900, y=400, width=110,
                                                                                              height=105)
        custom16 = Button(keyboard_frame, relief=RAISED, text="NO\nDRESSING", padx=20, pady=30, bd=5,
                          font="Arial 15 bold",
                          bg="white", activebackground="white",
                          command=lambda: keyboard_screen.insert(END, "1 NO DRESSING")).place(x=900, y=510, width=110,
                                                                                              height=105)


def insert_button(statusz, text, x, y, color, icon, doneness):  # 4dev
    cursor.execute(
        "INSERT INTO command_buttons(button_status, text, x, y, color, icon, doneness) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [statusz, text, x, y, color, icon, doneness])


def grab_cmd_button(button_status):
    global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
    cursor.execute("SELECT * FROM command_buttons WHERE button_status = %s", [button_status])
    the_temp_results = cursor.fetchall()
    counter = 0
    for temp_results in the_temp_results:
        the_command = temp_results[3]
        counter = 0

        def place_button(cmdz, counter):
            global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
            counter += 1
            button_name = str(button_status) + f"{counter}"
            if len(temp_results[7]) > 2:
                icon = image = PhotoImage(file=f"{temp_results[7]}")
            else:
                icon = image = None

            if temp_results[0] == 1016:
                name = return_member_namee(MEMBER_ID)
                button_name = CommandButton(f"Logout\n{name}", lambda: exec(f"{cmdz}"), temp_results[4],
                                            temp_results[5], temp_results[6])
            elif 1100 <= temp_results[0] <= 1107:
                button_name = CommandButton(temp_results[2], lambda: exec(f"{cmdz}"), temp_results[4], temp_results[5],
                                            temp_results[6], icon)
                TEMP_BUTTONS.append(button_name)
                TEMP_BUTTONS2.remove(button_name)
            else:
                button_name = CommandButton(str(temp_results[2]).replace(' ', '\n'), lambda: exec(f"{cmdz}"),
                                            temp_results[4], temp_results[5],
                                            temp_results[6], icon)

        place_button(the_command, counter)


def mod_stockz(item):
    global TEMP_BUTTONS

    def ok_button(val):
        global TABLE_NUMBER, MEMBER_ID, my_listbox, TEMP_FRAME, TEMP_BUTTONS, TEMP_BUTTONS2
        if val != "":
            cursor.execute("UPDATE stock SET qty = %s WHERE item = %s", [val, item])
            keypad_screen.delete(0, END)
            kill_keypad()

    def backspace():
        keypad_screen.delete(keypad_screen.index("end") - 1)

    def kill_keypad():
        keypad_screen.destroy()
        for button_X in tempz_keypad:
            button_X.destroy()
        keypad_frame.destroy()

    def button_click(number):
        keypad_screen.insert(END, str(number))

    keypad_frame = MyFrame(0, 0, WIDTH - 568, HEIGHT - 94, "lightblue")
    keypad_frame.grid_configure(rowspan=10, columnspan=11, ipadx=0, ipady=0)
    keypad_frame.place(x=0, y=0)
    keypad_screen = Entry(keypad_frame, font="Arial 90 bold", justify="center", bd=5, relief=RAISED)
    keypad_screen.place(x=115, y=96, height=193, width=227)
    keypad_button_1 = CommandButton("1", lambda: button_click(1), 0, 5, color="teal")
    keypad_button_2 = CommandButton("2", lambda: button_click(2), 1, 5, color="teal")
    keypad_button_3 = CommandButton("3", lambda: button_click(3), 2, 5, color="teal")
    keypad_button_4 = CommandButton("4", lambda: button_click(4), 0, 4, color="teal")
    keypad_button_5 = CommandButton("5", lambda: button_click(5), 1, 4, color="teal")
    keypad_button_6 = CommandButton("6", lambda: button_click(6), 2, 4, color="teal")
    keypad_button_7 = CommandButton("7", lambda: button_click(7), 0, 3, color="teal")
    keypad_button_8 = CommandButton("8", lambda: button_click(8), 1, 3, color="teal")
    keypad_button_9 = CommandButton("9", lambda: button_click(9), 2, 3, color="teal")
    keypad_button_0 = CommandButton("0", lambda: button_click(0), 0, 6, color="teal")
    keypad_button_backspace = CommandButton(" DEL", backspace, 1, 6, color="#FF4A4A")
    keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 2, 6, color="white")
    keypad_button_OK = CommandButton("OK", lambda: [ok_button(keypad_screen.get())], 3, 3, color="lightgreen")
    keypad_button_stk = CommandButton(f"{item}\nCurrent Stock:\n{sql_retrieve_stock(item)}", DISABLED, 0, 2,
                                      color="#4AE2FF")
    tempz_keypad = [keypad_button_stk, keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                    keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                    keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_OK]
    for button in tempz_keypad:
        TEMP_BUTTONS.append(button)
    TEMP_BUTTONS.append(keypad_frame)


def grab_stock_cmd_button(button_status):
    global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
    cursor.execute("SELECT * FROM command_buttons WHERE button_status = %s", [button_status])
    the_temp_results = cursor.fetchall()
    counter = 0
    for temp_results in the_temp_results:
        the_command = temp_results[3]
        the_name = temp_results[2]
        counter = 0

        def place_button(cmdz, counter, the_name):
            global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
            counter += 1
            button_name = str(button_status) + f"{counter}"
            if button_status == "login_buttons":
                button_name = LoginCommandButton(temp_results[2], lambda: exec(f"{cmdz}"), temp_results[4],
                                                 temp_results[5], temp_results[6])
                # TEMP_BUTTONS.append(button_name)
                # TEMP_BUTTONS2.remove(button_name)

            else:
                if temp_results[0] == 1016:
                    name = return_member_namee(MEMBER_ID)
                    button_name = CommandButton(f"Logout\n{name}", lambda: exec(f"{cmdz}"), temp_results[4],
                                                temp_results[5], temp_results[6])
                elif 1102 <= temp_results[0] <= 1107:
                    button_name = CommandButton(temp_results[2], lambda: exec(f"{cmdz}"), temp_results[4],
                                                temp_results[5], temp_results[6])
                    TEMP_BUTTONS.append(button_name)
                    TEMP_BUTTONS2.remove(button_name)
                else:
                    button_name = CommandButton(temp_results[2], lambda: exec(f"{mod_stockz(the_name)}"),
                                                temp_results[4],
                                                temp_results[5], temp_results[6])
                    TEMP_BUTTONS.append(button_name)
                    TEMP_BUTTONS2.remove(button_name)

        place_button(the_command, counter, the_name)


def grab_till_button(button_status):
    global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
    cursor.execute("SELECT * FROM command_buttons WHERE button_status = %s", [button_status])
    the_temp_results = cursor.fetchall()
    counter = 0
    for temp_results in the_temp_results:
        counter += 1

        def placez_button(counterz):
            global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
            button_name = str(button_status) + f"{counterz}"
            button_name = TillButton(str(temp_results[2]).replace(' ', '\n'), temp_results[4], temp_results[5],
                                     temp_results[6])

        placez_button(counter)


def standard_stock_button_layout():
    global STOCK_SWITCH, TEMP_BUTTONS

    def ss(value):
        global STOCK_SWITCH
        STOCK_SWITCH = value

    splitscreen_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    splitscreen_frame.grid_configure(rowspan=12, columnspan=11, ipadx=0, ipady=0)


def insert_table_number():  # table number
    global TABLE_NUMBER, MEMBER_ID, my_listbox

    def ok_button(val):
        global TABLE_NUMBER, MEMBER_ID, my_listbox
        if val != "":
            my_listbox.delete(0, END)
            kill_keypad()
            TABLE_NUMBER = val
            resume_basket()
            calculate_total()
            return val

    def backspace():
        keypad_screen.delete(keypad_screen.index("end") - 1)

    def kill_keypad():
        keypad_screen.destroy()
        keypad_frame.destroy()
        for button in tempz_keypad:
            button.destroy()

    def button_click(number):
        keypad_screen.insert(END, str(number))

    keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    keypad_frame.grid(row=0, column=0, columnspan=9, rowspan=8)

    mess = Message(keypad_frame, text="OPEN TABLE:", width=400)
    mess.configure(font="Arial 22 bold")
    mess.place(x=280, y=30)

    keypad_screen = Entry(root, font="Arial 90 bold", justify="center", width=5)
    keypad_screen.place(x=230, y=85, height=200)

    keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5, color="teal")
    keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5, color="teal")
    keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5, color="teal")
    keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4, color="teal")
    keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4, color="teal")
    keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4, color="teal")
    keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3, color="teal")
    keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3, color="teal")
    keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3, color="teal")
    keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6, color="teal")
    keypad_button_backspace = CommandButton(" DEL", backspace, 3, 6, color="#FF2A2A")
    keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 4, 6, color="white")
    keypad_button_OK = CommandButton("OK", lambda: [ok_button(keypad_screen.get())], 5, 3, color="lightgreen")

    tempz_keypad = [keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                    keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                    keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_OK]


def clear_frame():
    global TEMP_FRAME
    for button in TEMP_FRAME:
        button.kill()
    TEMP_FRAME.clear()


def clear_LABEL():
    global TEMP_LABEL
    for button in TEMP_LABEL:
        button.kill()
    TEMP_LABEL.clear()


def clear_cmd():
    global TEMP_BUTTONS2
    for button in TEMP_BUTTONS2:
        button.kill()
    TEMP_BUTTONS2.clear()


def clear():
    global TEMP_BUTTONS, PRICE_DISCOUNT, total_price_label
    for button in TEMP_BUTTONS:
        button.kill()
        button.remove_stock_label()
    TEMP_BUTTONS.clear()
    PRICE_DISCOUNT = 0


def resume_basket():
    global my_listbox, basket, MEMBER_ID, TABLE_NUMBER
    cursor.execute("SELECT * FROM basket WHERE table_id = %s ORDER BY datez ASC", [TABLE_NUMBER])
    all_basket_rows = cursor.fetchall()
    my_listbox.delete(0, END)
    for row in all_basket_rows:
        my_listbox.insert(END, (str(row[0]) + "                                                      " + str(row[6])))
        cursor.execute(
            "SELECT `message`, `prod_id` FROM `messages` WHERE `prod_id` = %s && (status = %s OR status = %s)",
            [row[6], "IN BASKET", "PRINTED"])
        maybe_msg = cursor.fetchall()
        for msg in maybe_msg:
            my_listbox.insert(END, " " + str(msg[0]) + "                                                      " + str(
                msg[1]))

        # if check_if_msg(row[0], row[6]) is True:
        #     temp_listbox_msgs = get_msg_for(row[0], row[6])
        #     for x in range(len(temp_listbox_msgs)):
        #         my_listbox.insert(END, " ^MSG:"+str(temp_listbox_msgs[x][0]))

    calculate_total()


def print_MySQL():
    cursor.execute("SELECT * FROM basket")
    all_basket_rows = cursor.fetchall()
    empty_list = []
    for row in all_basket_rows:
        empty_list.append(row[0])
        empty_list.append(f"M_ID:{row[2]}")
        empty_list.append(f"T_ID:{row[3]}")
    return empty_list


def icecream_buttons_clear():
    global icecream_buttons
    for button in icecream_buttons:
        button.destroy()


def bitch_clear():
    global TEMP_BUTTONS, TEMP_BUTTONS2, my_listbox, my_scrollbar, total_price_label
    clear()
    clear_cmd()
    my_listbox.destroy()
    my_scrollbar.destroy()
    total_price_label.destroy()


def is_you_logged(user):
    global waiting_timer
    if int(user) not in [99, 101, 102]:
        namez = return_member_namee(user)
        cursor.execute("SELECT name FROM staff_hours WHERE clocked_out ='X' && name=%s", [namez])
        if_clocked = cursor.fetchall()
        if len(if_clocked) < 1:
            root.after_cancel(waiting_timer)
            waiting_timer = None
            messagebox.showwarning(title="Error",
                                   message=f"{namez}, you are not logged!\n\n*depending on the owners choice and needs,\nthe app can allow or not access\nbased on if you are logged")


def call_default_listbox():
    global my_listbox, my_scrollbar

    listbox_frame = MyFrame(0, 192, 341, 384, "white")

    # scrollbar
    my_scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
    # # listbox
    my_listbox = Listbox(listbox_frame, selectbackground="blue", yscrollcommand=my_scrollbar.set, selectmode=SINGLE,
                         activestyle="none")
    my_scrollbar.place(x=280, y=0, width=50, height=374)
    my_listbox.place(x=0, y=0, width=280, height=374)
    # scrollbar config
    my_scrollbar.config(command=my_listbox.yview)

    my_listbox.grid_propagate(0)
    my_listbox.propagate(0)
    my_listbox.configure(font="Arial 16 bold", bg=root_bg_color)


def my_secretz():
    global TEMP_BUTTONS, TEMP_BUTTONS2

    def kill_my_secretz():
        keypad_frame.destroy()

    def EOD_print():
        today = datetime.now().strftime("%d/%m/%Y")
        cursor.execute(
            f"SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE '{today}%'")
        total_salez = cursor.fetchall()

        print(f"""
    .      .
   /|      |\\
\__\\\\      //__/
   ||      ||
 \__'\     |'__/
   '_\\\\   //_'
   _.,:---;,._
   \_:     :_/
     |0. .0|   {PUB_NAME} 
     |     |
     ,\.-./ \\
     ;;`-'   `---__________-        
""")
        cursor.execute(f"SELECT DISTINCT member_id FROM orders_placed WHERE datez LIKE '{today}%'")
        members = cursor.fetchall()
        sumz = []
        print("")
        counter = 0
        for person in members:
            cursor.execute(
                f"SELECT IFNULL(format(sum(price), 2), 0) FROM orders_placed WHERE member_id = {person[0]} && datez LIKE '{today}%'")
            xq = cursor.fetchall()
            cursor.execute(
                f"SELECT IFNULL(format(sum(price), 2), 0) FROM orders_placed WHERE member_id = {person[0]} && datez LIKE '{today}%' && status LIKE '%PAID BY CASH'")
            cash1 = cursor.fetchall()
            cursor.execute(
                f"SELECT IFNULL(format(sum(price), 2), 0) FROM orders_placed WHERE member_id = {person[0]} && datez LIKE '{today}%' && status LIKE '%PAID BY CARD'")
            card1 = cursor.fetchall()
            cursor.execute(
                f"SELECT IFNULL(format(sum(price), 2), 0) FROM orders_placed WHERE member_id = {person[0]} && datez LIKE '{today}%' && status LIKE '%PAID BY VOUCHER'")
            voucher1 = cursor.fetchall()

            temp = xq[0][0].replace(",", "")

            sumz.append((person[0], float(temp)))
            print(
                f"{return_member_namee(sumz[counter][0])} has made today £{sumz[counter][1]}. Cash:£{cash1[0][0]}, Card:£{card1[0][0]}, Vouchers:£{voucher1[0][0]}.  VAT20%: £{round((float(sumz[counter][1]) * 0.2), 2)}.")
            counter += 1

        sortedsumz = sorted(sumz, key=lambda student: sumz[0][1])
        # print(sumz.sort(key=lambda sum: sumz[1]))

        # sortedsumz = sorted(sumz, key=lambda z: z[1], reverse=True)
        print(
            f"\nCongrats to {return_member_namee(sortedsumz[0][0])} for most sales of the day! (£{sortedsumz[0][1]}) :)")
        print("")
        print(f"""Total sales of the day: £{total_salez[0][0]}.""")
        total_salez2 = str(total_salez[0][0]).replace(",", "")
        print(f"""VAT20% of Total Sales: £{round((float(total_salez2) * 0.2), 2)}.""")
        print(
            f"""Total Sales without VAT20%: £{round((float(total_salez2) - (float(total_salez2) * 0.2)), 2)}.""")
        print("")

        mostH = float()
        mostH2 = ""
        for person in members:
            cursor.execute(
                f"SELECT IFNULL(format(sum(total_time), 2), 0) FROM staff_hours WHERE name = '{return_member_namee(person[0])}' && clocked_in LIKE '{datetime.now().strftime('%Y-%m-%d')}%' LIMIT 1")
            hours = cursor.fetchall()

            for row in hours:
                print(f"{return_member_namee(person[0])} has worked today {row[0]} hours.")
                if float(row[0]) > float(mostH):
                    mostH = row[0]
                    mostH2 = return_member_namee(person[0])

        print(f"Congrats to {mostH2} for most hours worked({mostH}h!) of this day! :)")
        print("\nProducts sold today:\n")
        unique_items = {}
        cursor.execute(f"SELECT product,price FROM orders_placed WHERE datez LIKE '{today}%'")
        print(today)
        todays_items = cursor.fetchall()
        test_total_sales = float(0)
        for item in todays_items:
            test_total_sales += round(float(item[1]), 2)
            if item[0] not in unique_items:
                unique_items[item[0]] = {"qty": 1, "Total": f"{item[1]}"}
            else:
                unique_items[item[0]] = {"qty": (unique_items[item[0]]["qty"] + 1),
                                         "Total": round((float(unique_items[item[0]]["Total"]) + float(item[1])), 2)}
        zPrettyTable = PrettyTable()
        zPrettyTable.title = f'Z Raport - {PUB_NAME} - {today}'

        zPrettyTable.field_names = ["Product", "Qty", "Total"]
        zPrettyTable.align["Product"] = "c"
        zPrettyTable.align["Qty"] = "c"
        zPrettyTable.align["Total"] = "c"
        zPrettyTable.min_width["Product"] = 30
        zPrettyTable.min_width["Qty"] = 10
        zPrettyTable.min_width["Total"] = 10
        for dictx in sorted(unique_items, key=lambda x: float(unique_items[x]['Total']), reverse=True):
            zPrettyTable.add_row([dictx, unique_items[dictx]["qty"], unique_items[dictx]["Total"]])
        zPrettyTable.add_row(["", "", ""])
        zPrettyTable.add_row(["", "TOTAL", f"£{round(test_total_sales, 2)}"])
        print(zPrettyTable)

        #########################################################  end of Z ############################################################################

    clear_cmd()
    keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    keypad_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)

    l1 = Label(root, text="welcome to the page where only cool kids stay :DDD").place(x=300, y=700)
    l2 = Label(root,
               text="here is where i can put some apps, like stocks, profit margin, sales, cash drawer opening with no reason, etc").place(
        x=300, y=720)
    l3 = Label(root, text="open to suggestions and needs").place(x=300, y=740)
    back = CommandButton("<- BACK", lambda: [kill_my_secretz(), login()], 0, 0)

    this_year = now.strftime("%Y")
    this_month = now.strftime("%m")
    this_day = now.strftime("%d")

    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%/{this_year}%"')
    results_this_year = cursor.fetchall()
    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%/{this_month}/{this_year}%"')
    results_this_month = cursor.fetchall()

    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "{this_day}/{this_month}/{this_year}%"')
    results_this_day = cursor.fetchall()

    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%/{int(this_year) - 1}%"')
    results_this_year_last_year = cursor.fetchall()
    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%/{this_month}/{int(this_year) - 1}%"')
    results_this_month_last_year = cursor.fetchall()
    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "{this_day}/{this_month}/{int(this_year) - 1}%"')
    results_this_day_last_year = cursor.fetchall()
    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%{int(this_year)}%" and price NOT LIKE "-%"')
    turnover = cursor.fetchall()
    cursor.execute(
        f'SELECT IFNULL(format(sum(price), 2), 0) AS Sales FROM `orders_placed` WHERE datez LIKE "%{int(this_year) - 1}%" and price NOT LIKE "-%"')
    turnover_last_year = cursor.fetchall()

    xxx1 = LabelButton(f"Sales This Day £{results_this_day[0][0]}", 1, 2, "lightgreen")
    xxx2 = LabelButton(f"Sales This Month £{results_this_month[0][0]}", 2, 2, "lightgreen")
    xxx3 = LabelButton(f"Sales This Year £{results_this_year[0][0]}", 3, 2, "lightgreen")
    xxx4 = LabelButton(f"Sales Last Year £{results_this_year_last_year[0][0]}", 1, 3)
    xxx5 = LabelButton(f"Sales This Month Year Ago £{results_this_month_last_year[0][0]}", 2, 3)
    xxx6 = LabelButton(f"Sales This Day Year Ago £{results_this_day_last_year[0][0]}", 3, 3)

    xxx7 = LabelButton(f"Turnover This Year £{turnover[0][0]}", 1, 4, "pink")
    xxx8 = LabelButton(f"Turnover Last Year £{turnover_last_year[0][0]}", 2, 4, "pink")

    xxx1.configure(font='Arial 12 bold')
    xxx2.configure(font='Arial 12 bold')
    xxx3.configure(font='Arial 12 bold')
    xxx4.configure(font='Arial 12 bold')
    xxx5.configure(font='Arial 12 bold')
    xxx6.configure(font='Arial 12 bold')
    xxx7.configure(font='Arial 12 bold')
    xxx8.configure(font='Arial 12 bold')

    xxx1.place(x=150, y=50, width=300, height=50)
    xxx2.place(x=150, y=100, width=300, height=50)
    xxx3.place(x=150, y=150, width=300, height=50)
    xxx4.place(x=150, y=200, width=300, height=50)
    xxx5.place(x=150, y=250, width=300, height=50)
    xxx6.place(x=150, y=300, width=300, height=50)
    xxx7.place(x=150, y=350, width=300, height=50)
    xxx8.place(x=150, y=400, width=300, height=50)

    button_end_of_day_print = CommandButton("End of\nday\nZ", lambda: EOD_print(), 0, 0)
    button_end_of_day_print.place(x=500, y=200, height=190, width=190)


def kitchen_ordering():
    global my_listbox, my_scrollbar, TEMP_BUTTONS, prod_list

    def place_order():
        def send_email(user, pwd, recipient, subject, body):
            import smtplib

            FROM = user
            TO = recipient if isinstance(recipient, list) else [recipient]
            SUBJECT = subject
            TEXT = body

            # Prepare actual message
            message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.login(user, pwd)
                server.sendmail(FROM, TO, message)
                server.close()
                print('successfully sent the mail')
            except:
                print("failed to send mail")

        temp_order = ""
        for item in my_listbox.get(0, END):
            temp_order += item + "\n"

        send_email("alemihai25@gmail.com", "Oanamihai12", "alemihai25@gmail.com",
                   f"The Black Hart Order - GL14 1JB - {datetime.now().strftime('%d/%m/%Y')}",
                   f"""
Hello. This is Chef from Black Hart in Broadoak.\n
Can i please have:\n
{temp_order}
Thank you,
Kind regards
Chef,
The Black Hart
GL14 1JB
01594 516 319
""")

    def addz():
        if my_listbox.get(ANCHOR) and my_listbox.curselection() != ():
            my_listbox.insert(END, my_listbox.get(ANCHOR))

    def removz():
        if my_listbox.get(ANCHOR) and my_listbox.curselection() != ():
            my_listbox.delete(ANCHOR)

    def cancel_ordering():
        root.unbind("<Button-1>")
        ordering_frame.destroy()
        my_listbox.destroy()
        my_scrollbar.destroy()
        clear_frame()
        clear_cmd()
        login()

    def zpressed(event):
        global waiting_timer, a_frame, prod_list

        for item in prod_list:
            if str(f'{event.widget.__repr__()}') in item:
                return order_this(str(event.widget.__repr__()))

    def order_this(item):
        global my_listbox, my_scrollbar, TEMP_BUTTONS

        def ok_button(val):
            global TABLE_NUMBER, MEMBER_ID, my_listbox, TEMP_FRAME, TEMP_BUTTONS, TEMP_BUTTONS2
            if val != "":
                my_listbox.insert(END, keypad_screen.get() + " x " + item)
                keypad_screen.delete(0, END)
                root.bind("<Button-1>", zpressed)
                kill_keypad()

        def backspace():
            keypad_screen.delete(keypad_screen.index("end") - 1)

        def kill_keypad():
            keypad_screen.destroy()
            for button_X in tempz_keypad:
                button_X.destroy()
            keypad_frame.destroy()

        def button_click(number):
            keypad_screen.insert(END, str(number))

        for listz in prod_list:
            if item in listz:
                root.unbind("<Button-1>")

                keypad_frame = MyFrame(0, 0, WIDTH - 568, HEIGHT, "lightblue")
                keypad_frame.place(x=0, y=0)
                keypad_screen = Entry(keypad_frame, font="Arial 90 bold", justify="center", bd=5, relief=RAISED)
                keypad_screen.place(x=115, y=96, height=193, width=227)
                keypad_button_1 = CommandButton("1", lambda: button_click(1), 0, 5, color="teal")
                keypad_button_2 = CommandButton("2", lambda: button_click(2), 1, 5, color="teal")
                keypad_button_3 = CommandButton("3", lambda: button_click(3), 2, 5, color="teal")
                keypad_button_4 = CommandButton("4", lambda: button_click(4), 0, 4, color="teal")
                keypad_button_5 = CommandButton("5", lambda: button_click(5), 1, 4, color="teal")
                keypad_button_6 = CommandButton("6", lambda: button_click(6), 2, 4, color="teal")
                keypad_button_7 = CommandButton("7", lambda: button_click(7), 0, 3, color="teal")
                keypad_button_8 = CommandButton("8", lambda: button_click(8), 1, 3, color="teal")
                keypad_button_9 = CommandButton("9", lambda: button_click(9), 2, 3, color="teal")
                keypad_button_0 = CommandButton("0", lambda: button_click(0), 0, 6, color="teal")
                keypad_button_backspace = CommandButton(" DEL", backspace, 1, 6, color="#FF4A4A")
                keypad_button_cancel = CommandButton("CANCEL", kill_keypad, 2, 6, color="white")
                keypad_button_OK = CommandButton("OK", lambda: [ok_button(keypad_screen.get())], 3, 3,
                                                 color="lightgreen")

                keypad_button_1.place(x=0, y=500, width=100, height=100)
                keypad_button_2.place(x=100, y=500, width=100, height=100)
                keypad_button_3.place(x=200, y=500, width=100, height=100)
                keypad_button_4.place(x=0, y=400, width=100, height=100)
                keypad_button_5.place(x=100, y=400, width=100, height=100)
                keypad_button_6.place(x=200, y=400, width=100, height=100)
                keypad_button_7.place(x=0, y=300, width=100, height=100)
                keypad_button_8.place(x=100, y=300, width=100, height=100)
                keypad_button_9.place(x=200, y=300, width=100, height=100)
                keypad_button_0.place(x=0, y=600, width=100, height=100)
                keypad_button_backspace.place(x=100, y=600, width=100, height=100)
                keypad_button_cancel.place(x=200, y=600, width=100, height=100)
                keypad_button_OK.place(x=300, y=300, width=100, height=100)
                #
                # for button in tempz_keypad:
                #     for y in range(1, 4):
                #         for yy in range(1, 5):
                #             button
                tempz_keypad = [keypad_button_1, keypad_button_2, keypad_button_3, keypad_button_4,
                                keypad_button_5, keypad_button_6, keypad_button_7, keypad_button_9, keypad_button_8,
                                keypad_button_0, keypad_button_backspace, keypad_button_cancel, keypad_button_OK]

                for button in tempz_keypad:
                    TEMP_BUTTONS.append(button)
                TEMP_BUTTONS.append(keypad_frame)

    def show_buttcher_buttons():

        for i in range(0, 8):
            for ii in range(0, 5):
                button_name = LoginCommandButton(f"{prod_list[ii][i]}", DISABLED, i, ii)
                button_name.place(x=125 * i, y=100 * ii, width=125, height=100)
                TEMP_BUTTONS.append(button_name)
        root.unbind_all("<Button-1>")
        root.bind("<Button-1>", zpressed)

    clear_cmd()
    ordering_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
    ordering_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)
    call_default_listbox()
    butcher = CommandButton("Pete Jeff.\nButcher", lambda: [show_buttcher_buttons()], 0, 0)
    butcher.place(x=0, y=640, height=120, width=120)

    addz = CommandButton("ADD!", addz, 0, 0)
    addz.place(x=345, y=280, height=120, width=120)
    removz = CommandButton("REMOVE!", removz, 0, 0)
    removz.place(x=345, y=400, height=120, width=120)

    close_screen = CommandButton("Done\nAdding\nTo List", lambda: [root.unbind("<Button-1>"), clear()], 0, 0)
    close_screen.place(x=780, y=640, height=120, width=120)

    close_screen3 = CommandButton("Place\nButcher\nOrder!", lambda: [place_order(), cancel_ordering()], 0, 0)
    close_screen3.place(x=900, y=0, height=120, width=120)

    close2_screen = CommandButton("Cancel\nOrdering", lambda: cancel_ordering(), 0, 0)
    close2_screen.place(x=900, y=640, height=120, width=120)


def secret_key():
    def secret_keypad():
        def ok_button(val):
            cursor.execute("SELECT * FROM `keypad_passwd`")
            results = cursor.fetchall()
            for row in results:
                if val == row[0]:
                    keypad_screen.destroy()
                    my_secretz()
                    break
                elif val == "44444":
                    root.quit()

        def backspace():
            keypad_screen.delete(keypad_screen.index("end") - 1)

        def button_click(number):
            current = keypad_screen.get()
            keypad_screen.delete(0, END)
            keypad_screen.insert(0, str(current) + str(number))

        keypad_frame = MyFrame(0, 0, WIDTH, HEIGHT, "lightblue")
        random_chars = ['☺', '☻', '♥', '☻', '☺', '♦', '♣', '♥', '☼']
        keypad_screen = Entry(root, show=random_chars[random.randrange(len(random_chars))], width=12,
                              font="Arial 60 bold", justify="center")
        keypad_screen.grid(column=2, row=2, columnspan=5)

        keypad_button_7 = CommandButton("7", lambda: [button_click(7), ok_button(keypad_screen.get())], 3, 3)
        keypad_button_8 = CommandButton("8", lambda: [button_click(8), ok_button(keypad_screen.get())], 4, 3)
        keypad_button_9 = CommandButton("9", lambda: [button_click(9), ok_button(keypad_screen.get())], 5, 3)
        keypad_button_4 = CommandButton("4", lambda: [button_click(4), ok_button(keypad_screen.get())], 3, 4)
        keypad_button_5 = CommandButton("5", lambda: [button_click(5), ok_button(keypad_screen.get())], 4, 4)
        keypad_button_6 = CommandButton("6", lambda: [button_click(6), ok_button(keypad_screen.get())], 5, 4)

        keypad_button_1 = CommandButton("1", lambda: [button_click(1), ok_button(keypad_screen.get())], 3, 5)
        keypad_button_2 = CommandButton("2", lambda: [button_click(2), ok_button(keypad_screen.get())], 4, 5)
        keypad_button_3 = CommandButton("3", lambda: [button_click(3), ok_button(keypad_screen.get())], 5, 5)

        keypad_button_0 = CommandButton("0", lambda: button_click(0), 3, 6)
        keypad_button_backspace = CommandButton(" DEL", backspace, 4, 6)
        keypad_button_cancel = CommandButton("CANCEL",
                                             lambda: [keypad_screen.destroy(), clear_frame(), clear_cmd(), login()], 5,
                                             6)

    secret_keypad()


def command_screen():
    grab_cmd_button("command")


def screen1_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen1")
    if STOCK_MOD:
        grab_stock_cmd_button("screen1")


def screen2_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen2")
    if STOCK_MOD:
        grab_stock_cmd_button("screen2")


def screen3_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen3")
    if STOCK_MOD:
        grab_stock_cmd_button("screen3")


def screen4_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen4")
    if STOCK_MOD:
        grab_stock_cmd_button("screen4")


def screen5_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen5")
    if STOCK_MOD:
        grab_stock_cmd_button("screen5")


def screen6_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen6")
    if STOCK_MOD:
        grab_stock_cmd_button("screen6")


def screen7_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen7")
    if STOCK_MOD:
        grab_stock_cmd_button("screen7")


def screen8_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen8")
    if STOCK_MOD:
        grab_stock_cmd_button("screen8")


def screen9_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen9")
    if STOCK_MOD:
        grab_stock_cmd_button("screen9")


def screen10_buttons():
    global MEMBER_ID, waiting_timer
    clear()
    allowed = ["ADMIN", "OWNER", "MANAGEMENT"]
    if check_clearance(return_member_name()) in allowed:
        root.after_cancel(waiting_timer)
        waiting_timer = None
        grab_cmd_button("screen10")
    else:
        root.after_cancel(waiting_timer)
        waiting_timer = None
        messagebox.showerror(title="Access Level Denied!",
                             message="You are not allowed to do this.\n\nCall a management member.")


def check_clearance(name):
    cursor.execute("SELECT `member_type` from `members` WHERE `member_name` = %s", [name])
    results = cursor.fetchall()
    return results[0][0]


def screen_extra1_buttons():
    global STOCK_MOD
    clear()
    if not STOCK_MOD:
        grab_till_button("screen_extra1_buttons")
    if STOCK_MOD:
        grab_stock_cmd_button("screen_extra1_buttons")


def mod_stock_cmd_buts():
    back = CommandButton("<- BACK", lambda: [clear(), clear_cmd(), clear_frame(), clear_LABEL(), bitch_clear(),
                                             set_STOCK_MOD(False), login()], 1, 0)
    for i in range(7):
        CommandButton("", DISABLED, 0, i)
    cursor.execute(
        "SELECT * FROM command_buttons WHERE command LIKE 'screen%' && command != 'screen10_buttons()' ORDER BY command")
    the_temp_results = cursor.fetchall()
    counter = 0
    for temp_results in the_temp_results:
        the_command = temp_results[3]

        def place_button(cmdz, counter):
            global TEMP_BUTTONS, TEMP_BUTTONS2, MEMBER_ID
            if counter < 10:
                button_name = "z" + f"{counter}"
                # x = CommandButton("", DISABLED, 0,  counter-1)
                button_name = CommandButton(temp_results[2], lambda: exec(f"{cmdz}"), f"{counter - 1}", 7,
                                            temp_results[6])
            else:
                button_name = "z" + f"{counter}"
                # x = CommandButton("", DISABLED, 0,  counter-1)
                button_name = CommandButton(temp_results[2], lambda: exec(f"{cmdz}"), f"{(counter - 1) - 7}", 0,
                                            temp_results[6])

        counter += 1
        place_button(the_command, counter)


def set_STOCK_MOD(status):
    global STOCK_MOD
    STOCK_MOD = status


def suggestion_bx():
    clear_cmd()

    def backspace():
        keyboard_screen.delete(keyboard_screen.index("end") - 1)

    def insert_me():
        if len(keyboard_screen.get()) > 1:
            cursor.execute("INSERT INTO `suggestion_bx`(`message`, `time`)  VALUES (%s,%s)",
                           [keyboard_screen.get(), time_now()])

    def kill_keyboard():
        keyboard_frame.destroy()
        keyboard_screen.destroy()

    keyboard_frame = MyFrame(0, 0, WIDTH, HEIGHT, 'lightblue')
    keyboard_frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)

    keyboard_screen = Entry(keyboard_frame, width=4, font="Arial 20 bold", justify="center", bd=5, relief=RAISED)
    keyboard_screen.place(x=81, y=85, width=560, height=82)
    keyboard_screen.focus()
    buttonz = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
               ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
               ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
               ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.']]
    counter = 0
    for r in buttonz:
        for c in r:
            def create(r, c):
                if c == "f" or c == "j":
                    Button(keyboard_frame, relief=RAISED, text=str(c).upper(), padx=20, pady=20,
                           font='Arial 15 bold',
                           bd=5, bg="lightgrey", activebackground="lightgrey",
                           command=lambda: keyboard_screen.insert(END, c.upper())).place(
                        x=(((r.index(c) + 0.4) + counter) * 82), y=(((buttonz.index(r)) + 2) * 89), width=80)
                else:
                    Button(keyboard_frame, relief=RAISED, text=str(c).upper(), padx=20, pady=20,
                           font='Arial 15 bold',
                           bd=5, command=lambda: keyboard_screen.insert(END, c.upper())).place(
                        x=(((r.index(c) + 0.4) + counter) * 82), y=(((buttonz.index(r)) + 2) * 89), width=80)

            create(r, c)
        counter += 0.25
    space = Button(keyboard_frame, relief=RAISED, text="SPACE", padx=20, pady=30, bd=5, font="Arial 15 bold",
                   command=lambda: keyboard_screen.insert(END, " ")).place(x=125, y=535, width=500)
    insertz = Button(keyboard_frame, relief=RAISED, text="SEND", padx=20, pady=30, bd=5, font="Arial 15 bold",
                     bg="lightgreen", activebackground="lightgreen",
                     command=lambda: [insert_me(), kill_keyboard(), login()]).place(x=625, y=535, width=160)
    backspace = Button(keyboard_frame, relief=RAISED, text="BACKSPACE", padx=20, bd=5, pady=30,
                       font="Arial 15 bold", command=backspace, bg="#F63131", activebackground="#F63131").place(
        x=650, y=85, width=240, height=82)
    cancelz = Button(keyboard_frame, relief=RAISED, text="X", padx=20, pady=30, bd=5, font="Arial 15 bold",
                     command=lambda: [kill_keyboard(), login()]).place(x=790, y=10, width=100, height=50)


def staff_id(user):
    global MEMBER_ID, screen_logo, my_listbox, my_scrollbar, TEMP_BUTTONS, TABLE_NUMBER, STOCK_MOD, waiting_timer
    clear()
    MEMBER_ID = int(user)
    screen_logo = Canvas(root, height=HEIGHT, width=WIDTH, bg=root_bg_color)
    screen_logo.grid(row=0, column=0, sticky="nwes", columnspan=11, rowspan=10)
    is_you_logged(user)
    if 99 > int(user) >= 1:  # general staff
        command_screen()
        calculate_total()
    elif int(user) == 99:
        my_listbox.destroy()
        my_scrollbar.destroy()
        clear_cmd()
        set_STOCK_MOD("True")
        mod_stock_cmd_buts()
    elif int(user) == 101:
        def sql_clockIN(value):
            global waiting_timer
            namez = return_member_namee(value)
            stamp = datetime.now()
            cursor.execute(" SELECT name FROM staff_hours WHERE clocked_out ='X' && name=%s", [namez])
            if_clocked = cursor.fetchall()
            if len(if_clocked) > 0:
                root.after_cancel(waiting_timer)
                waiting_timer = None
                messagebox.showerror(title="Error", message="User already logged!")
                exit_clock_in_screen()
            else:
                cursor.execute(" SELECT member_name FROM members WHERE member_name=%s", [namez])
                check_name = cursor.fetchall()
                if len(check_name) > 0:
                    cursor.execute("INSERT INTO `staff_hours`(`name`,`clocked_in`) VALUES (%s,%s)", [namez, stamp])
                    exit_clock_in_screen()
                else:
                    root.after_cancel(waiting_timer)
                    waiting_timer = None
                    messagebox.showerror(title="Error", message="User does not exist!")
                    exit_clock_in_screen()

        def backspace():
            keypad_screen.delete(keypad_screen.index("end") - 1)

        def exit_clock_in_screen():
            root.after_cancel(xx)
            keypad_screen.destroy()
            clear_cmd()
            login()

        def button_click(number):
            keypad_screen.insert(END, str(number))

        my_listbox.destroy()
        my_scrollbar.destroy()
        keypad_screen = Entry(root, font="Arial 60 bold", justify="center")
        keypad_screen.grid_configure(rowspan=11, columnspan=10)
        keypad_screen.place(x=200, y=100, width=600)
        xx = root.after(910000, exit_clock_in_screen)
        keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5)
        keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5)
        keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5)
        keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4)
        keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4)
        keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4)
        keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3)
        keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3)
        keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3)
        keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6)
        keypad_button_backspace = CommandButton(" DEL", backspace, 3, 6)
        keypad_button_cancel = CommandButton("CANCEL", exit_clock_in_screen, 4, 6)
        keypad_button_clockin = CommandButton("IN",
                                              lambda: [sql_clockIN(keypad_screen.get()), exit_clock_in_screen()], 5,
                                              3)
        keypad_button_clockin.configure(pady=145, padx=50, bg="lightgreen")
        keypad_button_clockin.grid_configure(rowspan=4, columnspan=3)
    elif int(user) == 102:
        def sql_clockOUT(value):
            global waiting_timer
            namez = return_member_namee(value)
            zzz = datetime.now().strftime("%d/%m/%Y")
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(" SELECT name FROM staff_hours WHERE clocked_out ='X' && name=%s", [namez])
            if_clocked = cursor.fetchall()
            if len(if_clocked) != 1:
                root.after_cancel(waiting_timer)
                waiting_timer = None
                messagebox.showerror(title="Error", message="User is not logged in!")
                exit_clock_out_screen()

            else:
                cursor.execute("UPDATE staff_hours SET clocked_out = %s WHERE (name, clocked_out) = (%s,%s)",
                               [stamp, namez, "X"])
                cursor.execute(
                    "SELECT TIMESTAMPDIFF(SECOND, clocked_in, clocked_out) FROM staff_hours WHERE (name,total_time) = (%s,%s) ORDER BY clocked_in DESC LIMIT 1 ",
                    [namez, "X"])
                diff = cursor.fetchall()
                for row in diff:
                    cursor.execute("UPDATE staff_hours SET total_time=%s WHERE (name,total_time) = (%s,%s)",
                                   [format((int(row[0]) / 3600), '.2f'), namez, "X"])
            exit_clock_out_screen()

        def backspace():
            keypad_screen.delete(keypad_screen.index("end") - 1)

        def exit_clock_out_screen():
            root.after_cancel(xx)
            keypad_screen.destroy()
            clear_cmd()
            login()

        def button_click(number):
            keypad_screen.insert(END, str(number))

        my_listbox.destroy()
        my_scrollbar.destroy()
        keypad_screen = Entry(root, font="Arial 60 bold", justify="center")
        keypad_screen.grid_configure(rowspan=11, columnspan=10)
        keypad_screen.place(x=200, y=100, width=600)
        xx = root.after(910000, exit_clock_out_screen)
        keypad_button_1 = CommandButton("1", lambda: button_click(1), 2, 5)
        keypad_button_2 = CommandButton("2", lambda: button_click(2), 3, 5)
        keypad_button_3 = CommandButton("3", lambda: button_click(3), 4, 5)
        keypad_button_4 = CommandButton("4", lambda: button_click(4), 2, 4)
        keypad_button_5 = CommandButton("5", lambda: button_click(5), 3, 4)
        keypad_button_6 = CommandButton("6", lambda: button_click(6), 4, 4)
        keypad_button_7 = CommandButton("7", lambda: button_click(7), 2, 3)
        keypad_button_8 = CommandButton("8", lambda: button_click(8), 3, 3)
        keypad_button_9 = CommandButton("9", lambda: button_click(9), 4, 3)
        keypad_button_0 = CommandButton("0", lambda: button_click(0), 2, 6)
        keypad_button_backspace = CommandButton(" DEL", backspace, 3, 6)
        keypad_button_cancel = CommandButton("CANCEL", exit_clock_out_screen, 4, 6)
        keypad_button_clockout = CommandButton("OUT",
                                               lambda: [sql_clockOUT(keypad_screen.get()), exit_clock_out_screen()],
                                               5, 3)
        keypad_button_clockout.configure(pady=145, padx=50, bg="#ff777c")
        keypad_button_clockout.grid_configure(rowspan=4, columnspan=3)
    if int(user) not in [99, 101, 102]:
        call_default_listbox()
        resume_basket()
        calculate_total()


def login():
    global TEMP_BUTTONS, screen_logo, STOCK_SWITCH, TABLE_NUMBER, MEMBER_ID, my_listbox, STOCK_MOD, icecream

    screen_logo = Canvas(root, height=HEIGHT, width=WIDTH, bg="yellow")
    # screen_logo.grid(row=0, column=0, sticky="nwes", columnspan=9, rowspan=10)
    screen_logo.place(x=0, y=0)
    screen_logo.create_image(0, 0, anchor="nw", image=logo)

    # buttons to be loaded from DB later on // makes adding/deleting easier
    grab_stock_cmd_button("login_buttons")  # to grab the login screen buttons

    def xpressed(event):
        global waiting_timer, a_frame
        print(str(event.widget), str(event.widget.__repr__()))

    root.bind_all('<Any-KeyPress>', reset_timer)
    root.bind_all('<Any-ButtonPress>', reset_timer)
    root.bind("<Button-1>", pressed)
    root.bind("<ButtonRelease-1>", pressed_reset)

    root.bind("<Button-2>", xpressed)
    root.bind("<F9>", lambda event: print(icecream))
    root.bind("<F12>", lambda event: exec(
        "if messagebox.askokcancel(title='DEV HACK :)', message='Want to reset?'): clear(), clear_LABEL(), clear_frame(), clear_cmd(), screen_log()"))
    ##


# admincursor.execute("SELECT * FROM `pos` WHERE (`id_no`,`id_pub`) = (%s,%s)", [PUB_ID, PUB_NAME])
# adminresults = admincursor.fetchall()
#
# if adminresults[0][3] == "TRUE":
#     admincursor.execute(
#         "INSERT INTO `pos_last_opened`(`last_open`, `id`, `pub_name`, `attempt`) VALUES (%s, '1', %s, %s)",
#         [datetime.now(), PUB_NAME, 'SUCCESS'])
screen_log()
# else:
#     admincursor.execute(
#         "INSERT INTO `pos_last_opened`(`last_open`, `id`, `pub_name`, `attempt`) VALUES (%s, '1', %s, %s)",
#         [datetime.now(), PUB_NAME, 'FAIL'])
#     root.destroy()

def on_closing():
    root.destroy()

if __name__ == "__main__":
    try:
        root.mainloop()
        root.protocol("WM_DELETE_WINDOW", on_closing)
    except KeyboardInterrupt:
        root.destroy()