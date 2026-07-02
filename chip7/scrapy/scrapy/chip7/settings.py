# BOT

BOT_NAME         = 'chip7'
SPIDER_MODULES   = ['chip7.spiders']  # pasta onde o Scrapy procura spiders
NEWSPIDER_MODULE = 'chip7.spiders'    # pasta onde "scrapy genspider" cria novos spiders


# CHIP7 — CONSTANTES DO PROJETO

NAME_GPUS = 'gpus'                                     # nome do spider (usado nos FEEDS: output/gpus.csv)
URL_GPUS  = 'https://chip7.pt/componentes-hardware/placas-graficas'

NAME_PENS = 'pens'
URL_PENS =  'https://chip7.pt/armazenamento/pens-usb'

MAX_PAGES = 0                                       # 0 = sem limite; >0 = para nessa página


#BASE DE DADOS
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST     = os.getenv("DB_HOST")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME     = os.getenv("DB_NAME")
DB_TABLE_PRODUTOS   = os.getenv("DB_TABLE_PRODUTOS")
DB_TABLE_CATEGORIAS = os.getenv("DB_TABLE_CATEGORIAS")

#CATEGORIA
COL_CAT_ID_CATEGORIA   = os.getenv("COL_CAT_ID_CATEGORIA")
COL_CAT_NOME = os.getenv("COL_CAT_NOME")
COL_PROD_CODIGO = os.getenv("COL_PROD_CODIGO")
#PRODUTOS
COL_PROD_TITULO         = os.getenv("COL_PROD_TITULO")
COL_PROD_DESCRICAO      = os.getenv("COL_PROD_DESCRICAO")
COL_PROD_PRECO          = os.getenv("COL_PROD_PRECO")
COL_PROD_DISPONIBILIDADE= os.getenv("COL_PROD_DISPONIBILIDADE")
COL_PROD_ID_CATEGORIA   = os.getenv("COL_PROD_ID_CATEGORIA")



# USER_AGENT global do Scrapy (substituído pelo DEFAULT_REQUEST_HEADERS abaixo)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...'

# HEADERS — SIMULA BROWSER REAL PARA NÃO SER BLOQUEADO
DEFAULT_REQUEST_HEADERS = {
    'User-Agent'      : 'Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0',
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer'         : 'https://chip7.pt/',       # navegação interna no site
    'Sec-Fetch-Dest'  : 'document',                # indica que é um pedido de página HTML
    'Sec-Fetch-Mode'  : 'navigate',                # indica navegação normal (não XHR/fetch)
    'Sec-Fetch-Site'  : 'same-origin',             # simula clique dentro do mesmo site
}



# PLAYWRIGHT — BROWSER HEADLESS simula browser

# substitui o downloader padrão do Scrapy pelo Playwright (para sites com JS)
DOWNLOAD_HANDLERS = {
    'http' : 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
    'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
}

# O Playwright precisa de asyncio; isto substitui o reactor padrão do Twisted
#  Twisted é uma biblioteca de rede assíncrona para Python
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

PLAYWRIGHT_BROWSER_TYPE = 'chromium' 

PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,  # True = sem janela;
    'args': [
        '--no-sandbox',                                   # necessário em alguns ambientes Linux
        '--disable-blink-features=AutomationControlled',  # esconde flag de automação do Chromium
    ],
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000  # ms — tempo máximo para carregar uma página



# MIDDLEWARES
DOWNLOADER_MIDDLEWARES = {
    'chip7.middlewares.Chip7Middleware': 543,  # prioridade 543 (1=primeiro, 1000=último)
}



# PIPELINE — PROCESSAMENTO DOS ITEMS


# cada item extraído passa pelo pipeline antes de ser guardado
# número = prioridade (menor = executa primeiro)
ITEM_PIPELINES = {
    'chip7.pipeline.Chip7toPipeline': 300,
}



# FEEDS — FICHEIROS DE OUTPUT


# %(name)s é substituído pelo spider.name em runtime (ex: "gpus" → output/gpus.csv)
FEEDS = {
    'output/%(name)s.csv' : {'format': 'csv',
                             'overwrite': True,
                             'encoding': 'utf-8'},

    'output/%(name)s.json': {'format': 'json',
                             'overwrite': True,
                             'encoding': 'utf-8',
                             'indent': 4},
}



# THROTTLE & POLITENESS — EVITA BANS POR EXCESSO DE REQUESTS


DOWNLOAD_DELAY               = 1    # segundos mínimos entre requests
AUTOTHROTTLE_ENABLED         = True # ajusta o delay automaticamente consoante a latência do servidor
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0  # nº médio de requests simultâneos

ROBOTSTXT_OBEY = False  # chip7.pt não restringe scrapers no robots.txt



# LOGS

LOG_LEVEL = 'WARNING'  # WARNING oculta DEBUG/INFO — usa 'DEBUG' para diagnosticar problemas