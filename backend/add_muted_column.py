import sqlite3

db_path = r"D:\聊天项目\backend\chat.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查 muted 列是否存在
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

if 'muted' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN muted INTEGER DEFAULT 0")
    conn.commit()
    print("Column 'muted' added successfully")
else:
    print("Column 'muted' already exists")

conn.close()
