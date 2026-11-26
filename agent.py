import os
import json
import requests
from dotenv import load_dotenv
from metrics import (
    receita_total,
    total_pedidos,
    ticket_medio,
    clientes_unicos,
    taxa_cancelamento,
    receita_media_por_cliente  # Sua melhoria
)

# Carrega a chave do .env
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Modelo gratuito com suporte a tool calling (verifique a disponibilidade na sua conta)
MODELO = "openrouter/free"
URL_API = "https://openrouter.ai/api/v1/chat/completions"

# ---------------------------------------------------------
# 1. DEFINIÇÃO DAS FERRAMENTAS (O que o modelo pode chamar)
# ---------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "receita_total",
            "description": "Calcula a soma da receita de todos os pedidos concluídos. Use quando o usuário perguntar sobre faturamento, receita total ou quanto a loja vendeu.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "total_pedidos",
            "description": "Retorna a quantidade de pedidos concluídos. Use quando o usuário perguntar quantos pedidos foram feitos ou o volume de vendas.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ticket_medio",
            "description": "Calcula o valor médio por pedido concluído. Use quando o usuário perguntar sobre ticket médio, valor médio das compras ou média por pedido.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clientes_unicos",
            "description": "Retorna o número de clientes distintos que fizeram pedidos concluídos. Use quando o usuário perguntar quantos clientes compraram ou o alcance da loja.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "taxa_cancelamento",
            "description": "Retorna a proporção de pedidos cancelados sobre o total. Use quando o usuário perguntar sobre cancelamentos, taxa de cancelamento ou pedidos perdidos.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "receita_media_por_cliente",
            "description": "Calcula a receita total dividida pelo número de clientes únicos. Use quando o usuário perguntar quanto cada cliente gasta em média ou receita por cliente.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

# ---------------------------------------------------------
# 2. MAPA DE FUNÇÕES (Liga o nome da string à função Python)
# ---------------------------------------------------------
FUNCTION_MAP = {
    "receita_total": receita_total,
    "total_pedidos": total_pedidos,
    "ticket_medio": ticket_medio,
    "clientes_unicos": clientes_unicos,
    "taxa_cancelamento": taxa_cancelamento,
    "receita_media_por_cliente": receita_media_por_cliente
}

# ---------------------------------------------------------
# 3. ORQUESTRAÇÃO DO AGENTE
# ---------------------------------------------------------
def perguntar_ao_agente(pergunta: str, df) -> str:
    """
    Envia a pergunta para o OpenRouter. Se o modelo pedir uma ferramenta,
    executa a função Python correspondente e devolve o resultado para o modelo.
    """
    if not OPENROUTER_API_KEY:
        return "Erro: Chave OPENROUTER_API_KEY não encontrada no .env"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Mensagem inicial do sistema para dar contexto ao modelo
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente de dados especializado em vendas. "
                "Você NUNCA inventa números. Sempre que precisar de um dado, "
                "use as ferramentas disponíveis. Se a ferramenta retornar um valor, "
                "explique o resultado de forma clara e concisa em português."
            )
        },
        {"role": "user", "content": pergunta}
    ]

    # Loop para permitir múltiplas chamadas de ferramentas (se necessário)
    # Limite de 5 iterações para evitar loops infinitos
    for _ in range(5):
        payload = {
            "model": MODELO,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto"
        }

        try:
            response = requests.post(URL_API, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return f"Erro na comunicação com o modelo: {str(e)}"

        if not data.get("choices"):
            return "O modelo não retornou uma resposta válida."

        choice = data["choices"][0]
        message = choice["message"]

        # CASO 1: O modelo quer chamar uma ferramenta
        if message.get("tool_calls"):
            # Adiciona a mensagem do assistente ao histórico (importante para o contexto)
            messages.append(message)

            for tool_call in message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                # O mapa resolve o nome da função para a função Python real
                function_to_call = FUNCTION_MAP.get(function_name)

                if function_to_call:
                    try:
                        # Executa a função passando o DataFrame
                        # (Assumimos que as funções de metrics.py aceitam df como argumento)
                        result = function_to_call(df)
                        
                        # Formata o resultado para JSON (string)
                        # Se for float, converte para string formatada
                        if isinstance(result, float):
                            # Formata para 2 casas decimais (ajuda o modelo a ler)
                            result_str = f"{result:.2f}"
                        else:
                            result_str = str(result)

                        # Adiciona o resultado da ferramenta ao histórico
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": function_name,
                            "content": result_str
                        })
                    except Exception as e:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": function_name,
                            "content": f"Erro ao executar a função: {str(e)}"
                        })
                else:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": f"Função '{function_name}' não encontrada."
                    })
            
            # Continua o loop para enviar os resultados de volta ao modelo
            continue

        # CASO 2: O modelo respondeu com texto (fim do fluxo)
        elif message.get("content"):
            return message["content"]

        else:
            return "O modelo não retornou conteúdo."

    return "Limite de chamadas de ferramentas excedido."