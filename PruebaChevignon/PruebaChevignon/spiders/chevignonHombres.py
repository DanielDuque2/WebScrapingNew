import PruebaChevignon.items as items
from dotenv import load_dotenv
from datetime import datetime
import requests
import scrapy
import json
import os 

class ChevignonhombresSpider(scrapy.Spider):
    load_dotenv()
    iteradorPage = 1
    iteradorPagina = 0
    name = "chevignonHombres"
    allowed_domains = [os.environ.get("Dominio")]
    start_urls = [os.environ.get("Chgn_Ropa_Hombre"),
                    os.environ.get("Chgn_Ropa_Mujer"),
                    os.environ.get("Chgn_Ropa_Kid")]
    

    def parse(self, response):
        ChevignonHombres = items.DatosChevignonCSV()
        if response.status == 200:
            Respuesta = response.css(os.environ.get("Primer_Etiqueta"))[int(os.environ.get("Posicion_info"))].css(os.environ.get("Segunda_Etiqueta")+'::text').get()
            Productos = json.loads(Respuesta)
            idProducto = ""
            Lavado = None
            Descripcion = None
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
                        if 'Hombre' in ChevignonHombres['item']:
                            ChevignonHombres['category'] = 'Men'
                        elif 'Mujer' in ChevignonHombres['item']:
                            ChevignonHombres['category'] = 'Women'
                        elif 'Niño' in ChevignonHombres['item']:
                            ChevignonHombres['category'] = 'Kids'
                        ChevignonHombres["sku"] = Productos[Producto][os.environ.get("sku")]
                        ChevignonHombres['upc_wm'] = ChevignonHombres["sku"]
                        ChevignonHombres['upc_wm2'] = ChevignonHombres['upc_wm']
                        print(idProducto)
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
                        if(Productos[Producto]['name'] == os.environ.get('Lavado')):
                            Lavado = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                        if(Productos[Producto]['name'] == os.environ.get('Descripcion')):
                            Descripcion = Productos[Producto][os.environ.get("Primer_Nivel_Json")][os.environ.get("Segundo_Nivel_Json")][int(os.environ.get("Posicion_Color"))]
                    if Lavado is not None and Descripcion is not None:
                        ChevignonHombres['item_characteristics'] = f"""Descripción: {str(Descripcion).strip()} | Lavado {str(Lavado).strip()} | Composición : """
                        Lavado = None
                        Descripcion = None
                    if 'Image' in str(Producto) and Productos[Producto]['imageLabel'] == "1":
                        ChevignonHombres['image'] = Productos[Producto]['imageUrl']
                        #DescargarImagenes(str(ChevignonHombres['image']), str(ChevignonHombres['item']), str(idProducto))
                    if ("$"+os.environ.get("productSp")+idProducto+os.environ.get("Fin_Producto")) == str(Producto):
                        if ChevignonHombres is not None:
                            stocks = ChevignonHombres['stock']
                            if len(stocks) > 1 and type(stocks) is list:
                                for i in stocks:
                                    ChevignonHombres['stock'] = i
                                    #ChevignonHombres['upc'] = f"{ChevignonHombres['sku']}_{ChevignonHombres['modelo']}_{i}"
                                    yield ChevignonHombres
                            else:
                                if type(stocks) is list:
                                    ChevignonHombres['stock'] = stocks[0]
                                else:
                                    ChevignonHombres['stock'] = stocks
                                #ChevignonHombres['upc'] = f"{ChevignonHombres['sku']}_{ChevignonHombres['modelo']}_{ChevignonHombres['stock']}"
                                yield ChevignonHombres
                self.iteradorPage += 1
                yield response.follow(f"{self.start_urls[self.iteradorPagina]}{self.iteradorPage}", callback = self.parse)
            else:
                self.iteradorPage = 1
                if self.iteradorPagina < len(self.start_urls):
                    self.iteradorPagina += 1
        else:
            print(f"No se pudo obtener la información de la página, error ${response.status}")
    
def DescargarImagenes(Url, nombre, idProducto):
    DirectorioImagen = f"Imagenes/{nombre}-{idProducto}.png"
    try:
        if not os.path.exists(DirectorioImagen):
            imagen = requests.get(Url).content
            with open(DirectorioImagen, 'wb') as handler:
                handler.write(imagen)
    except:
        print("No se pudo guardar la imagen")