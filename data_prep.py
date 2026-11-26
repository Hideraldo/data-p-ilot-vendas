import os
import pandas as pd

# 1. Extrair dados
df = pd.read_csv("data/sales.csv")

# ---------- DIAGNÓSTICO INICIAL ----------
print("---- Diagnóstico Inicial ----")
print(df.head())
print("Shape:", df.shape)          # sem parênteses
print(df.dtypes)
print("=" * 40)

# ---------- LIMPEZA ----------
# 2. Converter data (inválidos viram NaT)
df['data'] = pd.to_datetime(df['data'], errors='coerce')

# 3. Padronizar status (strip + lower)
df['status'] = df['status'].str.strip().str.lower()

# 4. Remover duplicados pela chave do pedido
df = df.drop_duplicates(subset=['pedido_id'])

# 5. Remover linhas com data inválida (NaT)
df = df.dropna(subset=['data'])

# 6. Criar coluna de receita
df['receita'] = df['quantidade'] * df['preco_unitario']

# ---------- DIAGNÓSTICO PÓS-LIMPEZA ----------
print("\n---- Diagnóstico Pós-Limpeza ----")
print("Shape:", df.shape)
print("Nulos por coluna:\n", df.isna().sum())
print("Status únicos:", df['status'].unique())
print("Data mínima:", df['data'].min())
print("Data máxima:", df['data'].max())
print("Receita total:", df['receita'].sum())

# ---------- VALIDAÇÕES ----------
assert df['receita'].min() >= 0, "Receita negativa encontrada"
assert df['data'].notna().all(), "Datas inválidas restantes"
assert df['pedido_id'].is_unique, "pedido_id duplicado"

# ---------- SALVAR ----------
os.makedirs("data", exist_ok=True)
df.to_csv("data/sales_clean.csv", sep=';', decimal=',', index=False)
print("\n✅ Arquivo salvo em data/sales_clean.csv")