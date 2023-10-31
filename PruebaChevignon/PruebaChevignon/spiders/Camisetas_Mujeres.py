import PruebaChevignon.items as items
from dotenv import load_dotenv
from datetime import datetime
import requests
import scrapy
import json
import ast
import os 

class CamisetasMujeresSpider(scrapy.Spider):
    load_dotenv()
    name = "Camisetas_Mujeres"
    allowed_domains = ["www.chevignon.com.co"]
    Camiseta = os.environ.get("Chgn_Camiseta")
    start_urls = [os.environ.get("Chgn_Ropa_Hombre")]

    def parse(self, response):
        ChevignonHombres = items.DatosChevignonCSV()
        if response.status == 200:
            Respuesta = response.css(os.environ.get("Primer_Etiqueta"))[int(os.environ.get("Posicion_info"))].css(os.environ.get("Segunda_Etiqueta")+'::text').get()
            Productos = json.loads(Respuesta)
            idProducto = ""
            PrimerNivel = os.environ.get("Primer_Nivel_Json")
            SegundoNivel = os.environ.get("Segundo_Nivel_Json")
            PosicionValue = int(os.environ.get("Posicion_Values"))
            if os.environ.get("Validacion_Producto") in str(Productos):
                for Producto in Productos:
                    if os.environ.get("Nombre_Producto") in Productos[Producto]:
                        idProducto = Productos[Producto][os.environ.get("productId")]
                        ChevignonHombres['date'] = datetime.today().strftime("%d/%m/%Y")
                        ChevignonHombres['canal'] = Productos[Producto][os.environ.get("Marca")]
                        #ChevignonHombres['category'] = ast.literal_eval(os.environ.get("categorias"))[Productos[Producto][os.environ.get("Categoria")]]
                        ChevignonHombres['subcategory'] = os.environ.get("Chgn_Camiseta")
                        ChevignonHombres['marca'] = Productos[Producto][os.environ.get("Marca")]
                        ChevignonHombres['modelo'] = Productos[os.environ.get("productSp")+idProducto+os.environ.get("Color")][PrimerNivel][SegundoNivel][PosicionValue]
                        ChevignonHombres["sku"] = Productos[Producto][os.environ.get("sku")]
                        ChevignonHombres['item'] = Productos[Producto][os.environ.get("Nombre_Producto")]
                        ChevignonHombres['item_characteristics'] = f"""{Productos[os.environ.get("productSp")+idProducto+os.environ.get("Descripcion")]['name']}
                                                                    {Productos[os.environ.get("productSp")+idProducto+os.environ.get("Descripcion")][PrimerNivel][SegundoNivel][PosicionValue]} |
                                                                    {Productos[os.environ.get("productSp")+idProducto+os.environ.get("Lavado")]['name']}
                                                                    {Productos[os.environ.get("productSp")+idProducto+os.environ.get("Lavado")][PrimerNivel][SegundoNivel][PosicionValue]} |
                                                                    {Productos[os.environ.get("productSp")+idProducto+os.environ.get("Composicion")]['name']}
                                                                    {Productos[os.environ.get("productSp")+idProducto+os.environ.get("Composicion")][PrimerNivel][SegundoNivel][PosicionValue]}"""
                        ChevignonHombres["url_sku"] = os.environ.get("Dominio")
                        ChevignonHombres['price'] = Productos["$"+os.environ.get("productSp")+idProducto+os.environ.get("Precio_SinDescuento")]["highPrice"]
                        ChevignonHombres['sale_price'] = Productos["$"+os.environ.get("productSp")+idProducto+os.environ.get("Precio_Producto")]["highPrice"]
                        ChevignonHombres['sales_flag'] = 100 - ((ChevignonHombres['sale_price']*100)/ChevignonHombres['price'])
                        ChevignonHombres['stock'] = Productos[os.environ.get("productSp")+idProducto+os.environ.get("Tallas")][PrimerNivel][SegundoNivel][PosicionValue]
                        ChevignonHombres['upc_wm'] = ChevignonHombres["sku"]
                        ChevignonHombres['final_Price'] = ChevignonHombres['sale_price']
                        ChevignonHombres['upc_wm2'] = ChevignonHombres['upc_wm']
                        ChevignonHombres['composition'] = Productos[os.environ.get("productSp")+idProducto+os.environ.get("Composicion")][PrimerNivel][SegundoNivel][PosicionValue]
                        ChevignonHombres['made_in'] = Productos[os.environ.get("productSp")+idProducto+os.environ.get("Made_In")][PrimerNivel][SegundoNivel][PosicionValue]                
                    if 'Image' in str(Producto) and Productos[Producto]['imageLabel'] == "1":
                            ChevignonHombres['image'] = Productos[Producto]['imageUrl']
                            DescargarImagenes(str(ChevignonHombres['image']), str(ChevignonHombres['item']), str(idProducto))
                    if '4.sellers.0.commertialOffer' in Producto:
                        if ChevignonHombres is not None:
                            stocks = ChevignonHombres['stock']
                            if len(stocks) > 1 and type(stocks) is list:
                                for i in stocks:
                                    ChevignonHombres['stock'] = i
                                    ChevignonHombres['upc'] = f"{ChevignonHombres['sku']}_{ChevignonHombres['modelo']}_{i}"
                                    yield ChevignonHombres
                            else:
                                ChevignonHombres['stock'] = stocks
                                yield ChevignonHombres
            else:
                print("No hay productos en la página")
        else:
            print(f"No se pudo obtener la información de la página, error ${response.status}")
        #yield response.follow(f"https://www.chevignon.com.co/ropa-hombre/camisetas?page=2", callback = self.parse)
    
def DescargarImagenes(Url, nombre, idProducto):
    DirectorioImagen = f"Imagenes/{nombre}-{idProducto}.png"
    try:
        if not os.path.exists(DirectorioImagen):
            imagen = requests.get(Url).content
            with open(DirectorioImagen, 'wb') as handler:
                handler.write(imagen)
    except:
        print("No se pudo guardar la imagen")