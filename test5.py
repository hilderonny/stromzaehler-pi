# Datenbanktests
import sqlite3

# Beim Start Datenbank anlegen bzw. öffnen
db_connection = sqlite3.connect("test.db", autocommit=True)
# Messwerttabelle anlegen
db_connection.execute(
    "CREATE TABLE IF NOT EXISTS measurements(timestamp, value);"
)

# Messwerte einfügen
db_connection.execute(
    "INSERT INTO measurements(timestamp, value) VALUES(datetime('now'),?);",
    (994042,),
)
db_connection.executemany(
    "INSERT INTO measurements(timestamp, value) VALUES(?,?);",
    (
        ("2024-12-01 10:34:55", 990001,),
        ("2024-12-12 09:01:26", 990045,),
        ("2024-12-24 09:11:13", 990347,),
    ),
)

# Werte für Dezember 2024 abfragen
for row in db_connection.execute("""
    SELECT timestamp, value 
    FROM measurements 
    WHERE strftime('%Y-%m', timestamp) = '2024-12';
"""):
    print(row)