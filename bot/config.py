import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    email_address: str = field(default_factory=lambda: os.getenv("EMAIL_ADDRESS", ""))
    email_password: str = field(default_factory=lambda: os.getenv("EMAIL_PASSWORD", ""))
    email_provider: str = field(default_factory=lambda: os.getenv("EMAIL_PROVIDER", "gmail").lower())
    imap_port: int = 993
    log_dir: str = "logs"

    @property
    def imap_host(self) -> str:
        return {
            "gmail": "imap.gmail.com",
            "outlook": "imap.outlook.com",
            "hotmail": "imap-mail.outlook.com",
        }.get(self.email_provider, "imap.gmail.com")

    def validar(self) -> list[str]:
        erros = []
        if not self.email_address:
            erros.append("EMAIL_ADDRESS não configurado no .env")
        if not self.email_password:
            erros.append("EMAIL_PASSWORD não configurado no .env")
        return erros
