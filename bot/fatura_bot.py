from datetime import date
from pathlib import Path
from typing import Optional

from .config import Config
from .email_client import EmailClient
from .extrator import extrair_vencimento, extrair_vencimento_pdf, vencimento_no_periodo
from .logger import get_logger
from .providers.base import Provider


class ResultadoFatura:
    def __init__(
        self,
        provider: str,
        arquivo: str,
        vencimento: Optional[date],
        sucesso: bool,
        erro: Optional[str] = None,
    ):
        self.provider = provider
        self.arquivo = arquivo
        self.vencimento = vencimento
        self.sucesso = sucesso
        self.erro = erro


class FaturaBot:
    def __init__(self, config: Config, pasta_destino: Path):
        self.config = config
        self.pasta_destino = pasta_destino
        self.logger = get_logger(config.log_dir)
        self._client = EmailClient(config)

    def executar(self, providers: list[Provider]) -> list[ResultadoFatura]:
        self.logger.info("=" * 60)
        self.logger.info("  INICIANDO — BOT DOWNLOAD DE FATURAS")
        self.logger.info("=" * 60)

        resultados = []
        for provider in providers:
            self.logger.info(f"Processando provider: {provider.nome}")
            resultados.extend(self._processar_provider(provider))

        self._exibir_resumo(resultados)
        return resultados

    def _processar_provider(self, provider: Provider) -> list[ResultadoFatura]:
        resultados = []
        try:
            emails = self._client.buscar_emails_com_pdf(provider)
        except Exception as e:
            return [ResultadoFatura(provider.nome, "", None, sucesso=False, erro=str(e))]

        if not emails:
            self.logger.info(f"Nenhum e-mail com PDF encontrado para {provider.nome}")
            return []

        for assunto, pdf_bytes, nome_original in emails:
            resultado = self._processar_pdf(provider, assunto, pdf_bytes, nome_original)
            if resultado:
                resultados.append(resultado)

        return resultados

    def _processar_pdf(
        self,
        provider: Provider,
        assunto: str,
        pdf_bytes: bytes,
        nome_original: str,
    ) -> Optional[ResultadoFatura]:
        vencimento = extrair_vencimento(assunto, provider.regex_vencimento)

        if vencimento is None:
            self.logger.info("Vencimento não encontrado no assunto — tentando no PDF")
            vencimento = extrair_vencimento_pdf(pdf_bytes, provider.regex_vencimento)

        if vencimento is None:
            self.logger.warning(f"Vencimento não identificado em '{assunto}' — ignorando")
            return None

        if not vencimento_no_periodo(vencimento):
            self.logger.info(f"Vencimento {vencimento.strftime('%d/%m/%Y')} fora do período — ignorando")
            return None

        nome_arquivo = self._nome_arquivo(provider.nome, vencimento)
        caminho = self.pasta_destino / nome_arquivo

        if caminho.exists():
            self.logger.info(f"Já existe: {nome_arquivo} — pulando")
            return ResultadoFatura(provider.nome, nome_arquivo, vencimento, sucesso=True)

        caminho.write_bytes(pdf_bytes)
        self.logger.info(f"Salvo: {caminho}")
        return ResultadoFatura(provider.nome, nome_arquivo, vencimento, sucesso=True)

    def _exibir_resumo(self, resultados: list[ResultadoFatura]):
        self.logger.info("-" * 60)
        self.logger.info("  RESUMO FINAL")
        self.logger.info("-" * 60)
        if not resultados:
            self.logger.info("  Nenhuma fatura baixada no período")
        for r in resultados:
            if r.sucesso:
                venc = r.vencimento.strftime("%d/%m/%Y") if r.vencimento else "?"
                self.logger.info(f"  [{r.provider}] {r.arquivo} — venc. {venc} ✓")
            else:
                self.logger.error(f"  [{r.provider}] FALHA — {r.erro}")
        self.logger.info("=" * 60)

    @staticmethod
    def _nome_arquivo(provider: str, vencimento: date) -> str:
        return f"{provider}_{vencimento.strftime('%Y-%m')}_venc-{vencimento.strftime('%d')}.pdf"
