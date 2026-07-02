import scrapy
from scrapy_playwright.page import PageMethod
from chip7.items import Gpus
from chip7.settings import NAME_GPUS, URL_GPUS, MAX_PAGES

# seletor dos cards
CARD_SEL = 'div.flex.flex-col.flex-grow.px-2.pb-2'

class GpusSpider(scrapy.Spider):
    name   = NAME_GPUS   # nome do spider; usado pelo FEEDS: output/gpus.csv + output/gpus.json

    async def start(self):
        yield self._make_request(page=1, callback=self.parse)

    async def parse(self, response, page=1):
        pw_page = response.meta['playwright_page']    # TAB do Playwright aberto só para esta página
        await pw_page.close()  # já temos o HTML; não precisamos manter o tab aberto

        # seleciona todos os cards de produto
        cards = response.css(CARD_SEL)
        if not cards:
            return  # página vazia → termina paginação

        for card in cards:
            yield self._parse_card(card)

        # MAX_PAGES=0 → infinito (page +1 2,3...);
        if MAX_PAGES == 0 or page < MAX_PAGES:
            # pede a página seguinte como um Request novo e independente (tab novo)
            yield self._make_request(page=page + 1, callback=self.parse)

    @staticmethod  # não precisa de self nem cls — é utilitária pura
    def _make_request(page, callback):
        """Cria um Request Playwright para a página dada."""
        return scrapy.Request(
            url=f'{URL_GPUS}?category_page={page}',
            meta={
                'playwright': True,                 # activa o Playwright neste request
                'playwright_include_page': True,    # expõe o tab (pw_page) no response.meta para reutilizar o TAB
                'playwright_page_methods': [        # métodos executados pelo Playwright ANTES de chamar o callback
                    # aguarda o CARD_SEL ser carregado
                    PageMethod('wait_for_selector', CARD_SEL, timeout=10000),
                ],
            },
            callback=callback,
            cb_kwargs={'page': page},
            dont_filter=True,  # sem isto, o Scrapy ignora URLs "repetidos" no filtro de duplicados
        )

    @staticmethod
    def _parse_card(card):
        """Extrai os dados de um card de produto."""
        #  Combina os dois seletores de disponibilidade numa linha
        disp = card.css('span.text-brand-available::text, span.text-brand-unavailable::text').get()
        return Gpus(

            titulo          = card.css('p.uppercase.font-brand::text').get(),
            descricao       = card.css('p.text-gray-400.text-xs::text').get(),
            preco           = card.css('p.text-gray-800.text-2xl::text').get(),
            disponibilidade = disp.strip() if disp else None,
            codigo          = card.css('p.text-xs.text-gray-500::text').get(),
        )