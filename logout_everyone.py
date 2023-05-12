import MySQLdb
from datetime import datetime
from requests import get
from tkinter import messagebox

sqlHost = get('https://api.ipify.org').text
sqlPort = 3306
sqlUser = "PUBCON"
sqlPasswd = "Pubcon123$"
sqlDB = "blackhart"

try:
    conn = MySQLdb.connect(host=sqlHost, port=sqlPort, user=sqlUser, passwd=sqlPasswd, db=sqlDB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM staff_hours WHERE total_time = 'X'")
    results = cursor.fetchall()

    for row in results:
        cursor.execute("UPDATE staff_hours SET clocked_out = %s WHERE total_time = 'X'", [datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        cursor.execute("SELECT TIMESTAMPDIFF(SECOND, clocked_in, clocked_out) FROM staff_hours WHERE total_time = 'X' ORDER BY clocked_in DESC")
        diff = cursor.fetchall()
        print(diff)
        for row in diff:

            cursor.execute("UPDATE staff_hours SET total_time=%s WHERE total_time = 'X'", [(format((int(row[0]) / 3600), '.2f'))+"?"])
except:
    messagebox.showwarning(title="Error", message="Couldn't connect to db!")
