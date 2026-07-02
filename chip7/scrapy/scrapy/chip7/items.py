import scrapy

class Gpus(scrapy.Item):
    descricao       = scrapy.Field()    
    titulo          = scrapy.Field()    
    preco           = scrapy.Field()
    disponibilidade = scrapy.Field()
    codigo          = scrapy.Field()


class Pens(scrapy.Item):
    descricao       = scrapy.Field()
    titulo          = scrapy.Field()
    preco           = scrapy.Field()
    disponibilidade = scrapy.Field()
    codigo          = scrapy.Field()
