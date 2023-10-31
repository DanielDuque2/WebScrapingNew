import scrapy
import json

class VelezHombreCamisetasSpider(scrapy.Spider):
    name = "Velez_Hombre_Camisetas"
    allowed_domains = ["www.velez.com.co"]
    start_urls = ["https://www.velez.com.co/hombre/ropa/camisetas-y-polos"]

    def parse(self, response):
        cuerpoJson = response.css('script')
