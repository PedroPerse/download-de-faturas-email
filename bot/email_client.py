from datetime import date, timedelta
from typing import Optional

from imap_tools import MailBox, AND, MailMessage

from .config import Config
from .logger import get_logger
from .providers.base import Provider


class EmailClient:
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(config.log_dir)

    def buscar_emails_com_pdf(self, provider: Provider) -> list[tuple[str, bytes, str]]:
        """Retorna lista de (assunto, bytes_pdf, nome_arquivo) para o provider."""
        resultados = []
        data_inicio = date.today() - timedelta(days=60)

        self.logger.info(f"Conectando ao IMAP ({self.config.imap_host})")
        try:
            with MailBox(self.config.imap_host).login(
                self.config.email_address,
                self.config.email_password,
            ) as mailbox:
                self.logger.info(f"Conectado. Buscando e-mails de '{provider.nome}' desde {data_inicio}")

                mensagens = list(mailbox.fetch(
                    AND(date_gte=data_inicio),
                    mark_seen=False,
                ))
                self.logger.info(f"{len(mensagens)} e-mail(s) encontrado(s) no período")

                for msg in mensagens:
                    if not self._remetente_valido(msg, provider):
                        continue
                    if not self._assunto_valido(msg, provider):
                        continue

                    pdfs = self._extrair_pdfs(msg)
                    if not pdfs:
                        continue

                    self.logger.info(f"E-mail compatível: '{msg.subject}' — {len(pdfs)} PDF(s)")
                    for nome, conteudo in pdfs:
                        resultados.append((msg.subject or "", conteudo, nome))

        except Exception as e:
            self.logger.error(f"Erro ao acessar e-mail: {e}")
            raise

        return resultados

    def _remetente_valido(self, msg: MailMessage, provider: Provider) -> bool:
        remetente = (msg.from_ or "").lower()
        return any(dominio.lower() in remetente for dominio in provider.remetentes)

    def _assunto_valido(self, msg: MailMessage, provider: Provider) -> bool:
        assunto = (msg.subject or "").lower()
        return any(palavra.lower() in assunto for palavra in provider.palavras_chave)

    def _extrair_pdfs(self, msg: MailMessage) -> list[tuple[str, bytes]]:
        pdfs = []
        for anexo in msg.attachments:
            nome = (anexo.filename or "fatura.pdf").strip()
            if nome.lower().endswith(".pdf"):
                pdfs.append((nome, anexo.payload))
        return pdfs
