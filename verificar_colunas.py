import sqlite3

def alterar_tabela():
    conn = sqlite3.connect('users.db')  # Certifique-se de que o caminho está correto
    cursor = conn.cursor()

    # Adicionando novas colunas
    cursor.execute("ALTER TABLE propostas ADD COLUMN tipo_produto TEXT NOT NULL DEFAULT 'Indefinido'")
    cursor.execute("ALTER TABLE propostas ADD COLUMN valor_parcela REAL NOT NULL DEFAULT 0.0")
    cursor.execute("ALTER TABLE propostas ADD COLUMN prazo_atual INTEGER NOT NULL DEFAULT 0")

    # Certifique-se de comitar as mudanças
    conn.commit()

    # Fechar a conexão
    conn.close()

    print("Tabela alterada com sucesso!")

alterar_tabela()
