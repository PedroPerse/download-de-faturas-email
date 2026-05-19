from dataclasses import dataclass, field


@dataclass
class Provider:
    nome: str
    remetentes: list[str]
    palavras_chave: list[str]
    regex_vencimento: list[str]
