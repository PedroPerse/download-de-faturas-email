# Bot Download de Faturas por E-mail

Automação RPA em Python para baixar automaticamente faturas em PDF diretamente do seu e-mail, filtrando pelo mês de vencimento.

Compatível com **Gmail** e **Outlook**. Extensível para qualquer operadora.

---

## O Que a Automação Faz

1. Lê as credenciais do arquivo `.env`
2. Abre um seletor de pasta para escolher onde salvar as faturas
3. Conecta ao e-mail via IMAP
4. Busca e-mails dos últimos 60 dias que correspondam aos provedores configurados
5. Identifica a data de vencimento no assunto, corpo ou no próprio PDF
6. Baixa apenas faturas com vencimento no **mês atual ou no próximo**
7. Salva os PDFs com nome padronizado: `Vivo_2026-06_venc-15.pdf`
8. Não baixa duplicatas — se o arquivo já existir, pula

---

## Pré-requisitos

- Python 3.10+
- pip
- Conta Gmail ou Outlook com IMAP habilitado

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/PedroPerse/download-de-faturas-email.git
cd download-de-faturas-email

# 2. Instale as dependências
python -m pip install -r requirements.txt

# 3. Configure as credenciais
cp .env.example .env
# Edite o .env com seu e-mail e senha de app
```

---

## Configuração do `.env`

```env
EMAIL_ADDRESS=seu-email@gmail.com
EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
EMAIL_PROVIDER=gmail
```

`EMAIL_PROVIDER` aceita: `gmail`, `outlook`, `hotmail`

### Gmail — Senha de App (obrigatório)

O Gmail não aceita sua senha normal para acesso via IMAP. É necessário criar uma **Senha de App**:

1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Ative a **verificação em duas etapas** (se ainda não tiver)
3. Acesse **Segurança → Senhas de app**
4. Crie uma senha para "E-mail" e use ela no `EMAIL_PASSWORD`
5. Habilite o IMAP em: Gmail → Configurações → Ver todos → Encaminhamento e POP/IMAP

### Outlook / Hotmail

1. Acesse [outlook.live.com](https://outlook.live.com)
2. Configurações → Email → Sincronizar email → POP e IMAP
3. Habilite o IMAP
4. Use sua senha normal no `EMAIL_PASSWORD`

---

## Como Executar

```bash
python main.py
```

Ou pelo **VS Code**: selecione **"Bot Download Faturas"** no dropdown de debug e pressione `F5`.

---

## Provedores Suportados

| Provedor | Remetentes Monitorados |
|---|---|
| **Vivo** | `vivo.com.br`, `vivoempresas.com.br`, `claro.com.br` |

### Adicionando um Novo Provedor

1. Crie um arquivo em `bot/providers/sua_operadora.py`:

```python
from .base import Provider

CLARO = Provider(
    nome="Claro",
    remetentes=["claro.com.br", "net.com.br"],
    palavras_chave=["claro", "fatura", "conta"],
    regex_vencimento=[
        r"vencimento[:\s]+(\d{2}/\d{2}/\d{4})",
        r"(\d{2}/\d{2}/\d{4})",
    ],
)
```

2. Importe e adicione à lista em `main.py`:

```python
from bot.providers.claro import CLARO

PROVIDERS = [VIVO, CLARO]
```

---

## Estrutura do Projeto

```
bot_download_faturas/
├── main.py                  # Ponto de entrada
├── requirements.txt         # Dependências Python
├── .env.example             # Modelo de configuração (não contém dados reais)
├── .gitignore               # .env e faturas baixadas são ignorados pelo git
├── bot/
│   ├── config.py            # Lê o .env e define configurações
│   ├── logger.py            # Logger centralizado (console + arquivo)
│   ├── email_client.py      # Conexão IMAP e busca de e-mails
│   ├── extrator.py          # Extração de data de vencimento (assunto/corpo/PDF)
│   ├── fatura_bot.py        # Orquestrador principal
│   ├── providers/
│   │   ├── base.py          # Estrutura base de um provedor
│   │   └── vivo.py          # Configuração do provedor Vivo
│   └── ui/
│       └── pasta_window.py  # Seletor de pasta (tkinter)
└── logs/
    └── log_faturas.txt      # Log acumulativo de todas as execuções
```

---

## Dependências

| Pacote | Uso |
|---|---|
| `python-dotenv` | Leitura do arquivo `.env` |
| `imap-tools` | Acesso ao e-mail via IMAP |
| `pdfplumber` | Extração de texto de PDFs para identificar vencimento |
