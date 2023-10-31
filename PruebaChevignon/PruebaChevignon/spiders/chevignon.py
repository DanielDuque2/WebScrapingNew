import PruebaChevignon.items as items
from dotenv import load_dotenv
from datetime import datetime
import logging
import requests
import scrapy
import time
import json
import os 

class ChevignonSpider(scrapy.Spider):
    name = "chevignon"
    allowed_domains = ["www.chevignon.com.co"]
    load_dotenv()
    iteradorPage = 1
    iteradorPagina = 0
    start_urls = [os.environ.get("Chgn_Ropa_Hombre"),
                    os.environ.get("Chgn_Ropa_Mujer"),
                    os.environ.get("Chgn_Ropa_Kid")]

    def parse(self, response):
        ChevignonHombres = items.DatosChevignonCSV()
        try:
            if response.status == 200:
                InicializarItem(ChevignonHombres)
                Respuesta = response.css(os.environ.get("Primer_Etiqueta"))[int(os.environ.get("Posicion_info"))].css(os.environ.get("Segunda_Etiqueta")+'::text').get()
                Productos = json.loads(Respuesta)
                idProducto = ""
                if os.environ.get("Validacion_Producto") in str(Productos):
                    for Producto in Productos:
                        if os.environ.get("Nombre_Producto") in Productos[Producto]:
                            ChevignonHombres['date'] = datetime.today().strftime("%d/%m/%Y")
                            ChevignonHombres['canal'] = Productos[Producto][os.environ.get("Marca")]
                            ChevignonHombres['marca'] = Productos[Producto][os.environ.get("Marca")]
                            idProducto = Productos[Producto][os.environ.get("productId")]
                            ChevignonHombres['subcategory'] = Productos[Producto][os.environ.get('Categoria')][os.environ.get('Segundo_Nivel_Json')]
                            ChevignonHombres['item'] = Productos[Producto][os.environ.get("Nombre_Producto")]
                            ChevignonHombres["url_sku"] = os.environ.get("Dominio")
                            ChevignonHombres["sku"] = Productos[Producto][os.environ.get("sku")]
                            ChevignonHombres['upc_wm'] = ChevignonHombres["sku"]
                            ChevignonHombres['upc_wm2'] = ChevignonHombres['upc_wm']
                        if (os.environ.get("productSp")+idProducto+os.environ.get("Precio_Producto")) in str(Producto):
                            ChevignonHombres['sale_price'] = Productos[Producto]["highPrice"]
                            ChevignonHombres['final_Price'] = Productos[Producto]["highPrice"]
                        if (os.environ.get("productSp")+idProducto+os.environ.get("Precio_SinDescuento")) in str(Producto):
                            ChevignonHombres['price'] = Productos[Producto]["highPrice"]
                        if (os.environ.get("productSp")+idProducto+os.environ.get("Caracteristicas")) in str(Producto):
                            if os.environ.get("Color") == Productos[Producto]['name']:
                                ChevignonHombres['modelo'] = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                            if os.environ.get("Composition") == Productos[Producto]['name']:
                                ChevignonHombres['composition'] = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                            if os.environ.get("Made_In") == Productos[Producto]['name']:
                                ChevignonHombres['made_in'] = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                            if os.environ.get("Tallas") == Productos[Producto]['name']:
                                ChevignonHombres['stock'] = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")]
                            if os.environ.get('Lavado') == Productos[Producto]['name']:
                                ChevignonHombres['item_characteristics'] = ChevignonHombres['item_characteristics'] + Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                            if os.environ.get("Descripcion") == Productos[Producto]['name']:
                                ChevignonHombres['item_characteristics'] = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                        if 'Image' in str(Producto) and Productos[Producto]['imageLabel'] == "1":
                            ChevignonHombres['image'] = Productos[Producto]['imageUrl']
                            #DescargarImagenes(str(ChevignonHombres['image']), str(ChevignonHombres['item']), str(ChevignonHombres['modelo']))
                        if ("$"+os.environ.get("productSp")+idProducto+os.environ.get("Fin_Producto")) == str(Producto):
                            if ChevignonHombres is not None:
                                yield ChevignonHombres
                                # stocks = ChevignonHombres['stock']
                                # if len(stocks) > 1 and type(stocks) is list:
                                #     for i in stocks:
                                #         ChevignonHombres['stock'] = i
                                #         yield ChevignonHombres
                                # else:
                                #     if type(stocks) is list:
                                #         ChevignonHombres['stock'] = stocks[0]
                                #     else:
                                #         ChevignonHombres['stock'] = stocks
                                #     yield ChevignonHombres
                    self.iteradorPage += 1
                    time.sleep(2)
                    print("************************************************")
                    print(str(len(self.start_urls)) + "  " + str(self.iteradorPagina))
                    yield response.follow(f"{self.start_urls[self.iteradorPagina]}{self.iteradorPage}", callback = self.parse)
                else:
                    time.sleep(2)
                    self.iteradorPage = 1
                    if self.iteradorPagina < (len(self.start_urls) - 1):
                        self.iteradorPagina += 1
            else:
                print(f"No se pudo obtener la información de la página, error ${response.status}")
        except Exception:
            log = open("log_"+ datetime.today().strftime("%Y_%m_%d-%H-%M-%S")+".txt", "w")
            log.write(logging.exception("\n Error en la lectura de datos"))
            log.close()
    
def DescargarImagenes(Url, Nombre, Color):
    DirectorioImagen = f"Imagenes/{Nombre}-{Color}.png"
    try:
        if not os.path.exists(DirectorioImagen):
            imagen = requests.get(Url).content
            with open(DirectorioImagen, 'wb') as handler:
                handler.write(imagen)
    except Exception as Error:
        Error.add_note(f"Error en la descarga de imagen del articulo {Nombre}-{Color}")
        log = open("log_"+ datetime.today().strftime("%Y_%m_%d-%H-%M-%S")+".txt", "w")
        log.write(str(Error))
        log.close()
    
def InicializarItem(item):
    item['date'] = None
    item['canal'] = None
    item['category'] = None
    item['subcategory'] = None
    item['subcategory2'] = None
    item['subcategory3'] = None
    item['marca'] = None
    item['modelo'] = None
    item['subcategory'] = None
    item['sku'] = None
    item['upc'] = None
    item['item'] = None
    item['item_characteristics'] = ""
    item['url_sku'] = ""
    item['image'] = None
    item['price'] = None
    item['sale_price'] = None
    item['sales_flag'] = None
    item['stock'] = None
    item['upc_wm'] = None
    item['final_Price'] = None
    item['upc_wm2'] = None
    item['composition'] = None
    item['homogenized_clothing'] = None
    item['homogenized_subcategory'] = None
    item['homogenized_category'] = None
    item['homogenized_color'] = None
    item['made_in'] = None