# Validações de exemplo (protótipo)

def is_valid_cliente(nome: str) -> bool:
    """
    Verifica se o texto do cliente atende às regras atuais do protótipo.
    A lógica pode ser expandida conforme a necessidade.
    """
    # Exemplo: poderia verificar se o nome não está vazio
    if not nome or len(nome.strip()) == 0:
       return False # Exigir que o cliente não seja vazio
    return True

def is_valid_preco(preco: str) -> bool:
    """
    Verifica se o texto do preço atende às regras atuais do protótipo.
    A lógica pode ser expandida conforme a necessidade.
    """
    # Exemplo: poderia tentar converter para float
    try:
       # Permite vazio, mas se não for vazio, deve ser número
       if preco.strip():
           float(preco.replace(',', '.'))
       return True
    except ValueError:
       return False
