# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field 

class PruebachevignonItem(Item):
    Nombre = Field()
    Precio = Field()
    PrecioAlto = Field()
    PrecioBajo = Field()
    Color = Field()
    Composicion = Field()

class DatosChevignonCSV(Item):
    date = Field()#Listo
    canal = Field()#Listo
    category = Field()#Listo
    subcategory = Field()#Listo
    subcategory2 = Field()#Listo
    subcategory3 = Field()#Listo
    marca = Field()#Listo
    modelo = Field()#Listo
    sku = Field()#Listo
    upc = Field()
    item = Field()#Listo
    item_characteristics = Field()
    url_sku = Field()#Listo
    image = Field()#Listo
    price = Field()#Listo
    sale_price = Field()#Listo
    sales_flag = Field()
    stock = Field()
    upc_wm = Field()
    final_Price = Field()
    upc_wm2 = Field()
    composition = Field()#Listo
    homogenized_clothing = Field()
    homogenized_subcategory = Field()
    homogenized_category = Field()
    homogenized_color = Field()
    made_in = Field()#Listo
    Descripcion = Field()
    Lavado = Field()