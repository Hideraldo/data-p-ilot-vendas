import pandas as pd

def _pedidos_concluidos(df):
    return df[df['status'] == 'concluido']

def receita_total(df):
    """Retorna a receita total dos pedidos concluídos."""
    return _pedidos_concluidos(df)['receita'].sum()

def total_pedidos(df):
    """Retorna a quantidade de pedidos concluídos."""
    return len(_pedidos_concluidos(df))

def ticket_medio(df):
    """Retorna a receita média por pedido concluído."""
    concluidos = _pedidos_concluidos(df)
    if len(concluidos) == 0:
        return 0.0
    return concluidos['receita'].mean()

def clientes_unicos(df):
    """Retorna o número de clientes distintos com pedidos concluídos."""
    return _pedidos_concluidos(df)['cliente_id'].nunique()

def taxa_cancelamento(df):
    """Retorna a proporção de pedidos cancelados sobre o total."""
    if len(df) == 0:
        return 0.0
    cancelados = len(df[df['status'] == 'cancelado'])
    return cancelados / len(df)

def receita_media_por_cliente(df):
    """Retorna a receita total dividida pelo número de clientes únicos."""
    clientes = clientes_unicos(df)
    if clientes == 0:
        return 0.0
    return receita_total(df) / clientes