import sys

from bot.config import Config
from bot.fatura_bot import FaturaBot
from bot.logger import get_logger
from bot.providers.vivo import VIVO
from bot.ui.pasta_window import PastaWindow

PROVIDERS = [VIVO]


def main():
    config = Config()
    logger = get_logger(config.log_dir)

    erros = config.validar()
    if erros:
        for erro in erros:
            logger.error(erro)
        logger.error("Configure o arquivo .env antes de executar. Veja .env.example.")
        sys.exit(1)

    logger.info("Selecione a pasta onde as faturas serão salvas")
    pasta = PastaWindow().obter_pasta()

    if not pasta:
        logger.warning("Nenhuma pasta selecionada. Encerrando.")
        sys.exit(0)

    logger.info("Carregando configurações da automação")
    logger.info(f"  E-mail     : {config.email_address}")
    logger.info(f"  Provedor   : {config.email_provider.capitalize()} ({config.imap_host})")
    logger.info(f"  Providers  : {', '.join(p.nome for p in PROVIDERS)}")
    logger.info(f"  Destino    : {pasta}")
    logger.info(f"  Logs       : ./{config.log_dir}/")

    try:
        bot = FaturaBot(config, pasta)
        resultados = bot.executar(PROVIDERS)
        sucessos = sum(1 for r in resultados if r.sucesso)
        logger.info(f"Automação finalizada — {sucessos}/{len(resultados)} fatura(s) baixada(s)")
        sys.exit(0 if not resultados or sucessos > 0 else 1)

    except KeyboardInterrupt:
        logger.warning("Automação interrompida pelo usuário")
        sys.exit(130)
    except Exception as erro:
        logger.error(f"Erro fatal: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
