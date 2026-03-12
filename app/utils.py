

def formatar_bilhoes_milhoes(valor):
    """
    Formata valores numéricos para notação compacta brasileira (B para Bilhões, M para Milhões).
    """
    if valor is None or abs(valor) == 0:
        return "R$ 0,00"
        
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor / 1_000_000_000:.2f} B"
    elif abs(valor) >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} M"
    
    return f"R$ {valor:,.2f}"