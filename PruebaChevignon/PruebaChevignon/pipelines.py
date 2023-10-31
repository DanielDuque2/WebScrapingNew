# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import logging
import os
import re

load_dotenv()

class PruebachevignonPipeline:
    def process_item(self, item, spider):
        try:
            try:
                Homologados_Colores = pd.read_excel("Homologado.xlsx", sheet_name="Colores")

                Colores_Homologados = Homologados_Colores.set_index('Color_Marca').to_dict()['Color_Homologado']
            except Exception as Error:
                Error.add_note("Error en la importación del archivo de homologación excel")
                log = open("log_"+ datetime.today().strftime("%Y_%m_%d-%H-%M-%S")+".txt", "w")
                log.write(str(Error))
                log.close()
            else:
                if item is not None:
                    adaptador = ItemAdapter(item)
                    datos_item = adaptador.field_names()
                    for datos in datos_item:
                        if datos == 'modelo' and adaptador.get(datos) in Colores_Homologados:
                            adaptador['homogenized_color'] = Colores_Homologados[adaptador.get(datos)]
                        elif datos == 'modelo' and not adaptador.get(datos) in Colores_Homologados:
                            adaptador['homogenized_color'] = adaptador.get(datos)
                        if datos == 'made_in' and adaptador[datos] is not None:
                            made_in = adaptador.get(datos)
                            vector = made_in.split(" ")
                            adaptador[datos] = ((vector[len(vector)-1]).lower()).capitalize()
                        elif datos == 'made_in' and adaptador[datos] is None:
                            adaptador[datos] = None
                        if datos == 'subcategory':
                            categorias = adaptador.get(datos)
                            if type(categorias) is list:
                                categoriasSplit = categorias[0].split("/")
                            else:
                                categoriasSplit = categorias.split("/")
                            for i in range(0,len(categoriasSplit)-1):
                                match i:
                                    case 1:
                                        adaptador['subcategory'] = categoriasSplit[i]
                                    case 2:
                                        adaptador['subcategory2'] = categoriasSplit[i]
                                    case 3: 
                                        adaptador['subcategory3'] = categoriasSplit[i]
                            if 'Hombre' in adaptador['subcategory']:
                                adaptador['category'] = 'Men'
                            if 'Mujer' in adaptador.get(datos):
                                adaptador['category'] = 'Women'
                            if 'Ninos' in adaptador.get(datos):
                                adaptador['category'] = 'Kids'
                        if datos == 'item_characteristics':
                            patron = re.compile('<.*?>')
                            caracteristicas = re.sub(patron, '', adaptador.get(datos))
                            caracteristicas = str(caracteristicas).replace("•", "")
                            caracteristicas = caracteristicas.replace("\n", "")
                            caracteristicas = caracteristicas.replace("\r", "")
                            adaptador[datos] = caracteristicas
                        if datos == 'price' and adaptador[datos] != 0:
                            descuento = float(adaptador['sale_price'])/float(adaptador['price'])
                            if descuento == 1:
                                adaptador['sales_flag'] = None
                            else: 
                                adaptador['sales_flag'] = descuento
                        elif datos == 'price' and adaptador[datos] == 0:
                            adaptador['sales_flag'] = None
                        if datos == 'stock':
                            adaptador['upc'] = f"{adaptador['sku']}_{adaptador['modelo']}_{adaptador[datos]}"
                    
                return item
        except Exception:
            log = open("log_"+ datetime.today().strftime("%Y_%m_%d-%H-%M-%S")+".txt", "w")
            log.write(logging.exception("\n Error en pipelines"))
            log.close()
