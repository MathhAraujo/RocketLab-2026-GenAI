import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tabelas:", [r[0] for r in cur.fetchall()])

for table in ["avaliacao_pedido", "item_pedido", "pedido", "produtos"]:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]} registros")
    except Exception as e:
        print(f"  {table}: ERRO - {e}")

print("\nAmostra de produtos (vendas/avaliacao):")
cur.execute(
    "SELECT id_produto, nome_produto, total_vendas, avaliacao_media, total_avaliacoes FROM produtos LIMIT 5"
)
for r in cur.fetchall():
    print(" ", r)

conn.close()
