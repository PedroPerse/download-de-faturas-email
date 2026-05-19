import re
from datetime import date, datetime
from typing import Optional


def extrair_vencimento(texto: str, padroes: list[str]) -> Optional[date]:
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d/%m/%Y").date()
            except (ValueError, IndexError):
                continue
    return None


def extrair_vencimento_pdf(pdf_bytes: bytes, padroes: list[str]) -> Optional[date]:
    try:
        import io
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text() or ""
                resultado = extrair_vencimento(texto, padroes)
                if resultado:
                    return resultado
    except Exception:
        pass
    return None


def vencimento_no_periodo(vencimento: Optional[date]) -> bool:
    if vencimento is None:
        return False
    hoje = date.today()
    mes_atual = hoje.replace(day=1)
    if mes_atual.month == 12:
        mes_seguinte = mes_atual.replace(year=mes_atual.year + 1, month=1)
    else:
        mes_seguinte = mes_atual.replace(month=mes_atual.month + 1)
    venc_mes = vencimento.replace(day=1)
    return venc_mes in (mes_atual, mes_seguinte)
