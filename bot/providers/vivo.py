from .base import Provider

VIVO = Provider(
    nome="Vivo",
    remetentes=["vivo.com.br", "vivoempresas.com.br", "claro.com.br"],
    palavras_chave=["vivo", "fatura", "conta"],
    regex_vencimento=[
        r"vencimento[:\s]+(\d{2}/\d{2}/\d{4})",
        r"vence[m]?\s+(\d{2}/\d{2}/\d{4})",
        r"venc\.?\s*(\d{2}/\d{2}/\d{4})",
        r"(\d{2}/\d{2}/\d{4})",
    ],
)
