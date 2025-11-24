import itertools
import math
import copy

# Definición de las clases de tipos de datos
class TipoAtomico:
    """Clase que implementa los tipos atómicos"""
    def __init__(self, nombre, representacion, alineacion):
        self.nombre = nombre
        self.representacion = representacion
        self.alineacion = alineacion

class TipoCompuesto:
    """Clase que implementa los registros y los registro variantes"""
    def __init__(self, nombre, campos,es_union=False):
        self.nombre = nombre
        self.campos = campos
        self.es_union = es_union

class MiClase:
    def __init__(self, nombre, campos):
        self.nombre = nombre
        self.campos = campos


class ManejadorTipos:
    """Clase que implementa el manejador de tipos de datos"""
    def __init__(self):
        self.tipos = {} # Diccionario para los tipos

    
    def agregar_tipo_atomico(self, nombre, representacion, alineacion):
        """Método que define un nuevo tipo atómico"""
        if nombre in self.tipos:
            print(f"Error: el tipo '{nombre}' ya existe.")
            return
        self.tipos[nombre] = TipoAtomico(nombre, representacion, alineacion)

    
    def agregar_tipo_compuesto(self, nombre, tipos_campos, es_union=False):
        """Método que define un nuevo registro o un nuevo registro variante"""
        if nombre in self.tipos:
            print(f"Error: el tipo '{nombre}' ya existe.")
            return
        for tipo in tipos_campos:
            if tipo not in self.tipos:
                print(f"Error: el tipo '{tipo}' no está definido.")
                return
        self.tipos[nombre] = TipoCompuesto(nombre, tipos_campos, es_union)


    def size_alineacion(self, tipo_nombre, es_union=False, optimo=False):
        """Método que calcula el tamaño y la alineación de un tipo"""

        tipo = self.tipos[tipo_nombre] # Se obtiene el tipo de dato del diccionario de tipos  
        size_empaquetado = 0  # Tamaño del tipo cuando los campos están empaquetados
        size_no_empaquetado = 0  # Tamaño del tipo cuando los campos no están empaquetados
        union_emp = 0  # Tamaño de la unión empaquetada
        union_no_emp =0 # Tamaño de la unión no empaquetada
        alineacion_empaquetado = 0  # Alineación del tipo empaquetado
        alineacion_no_empaquetado = 0  # Alineación del tipo no empaquetado
        PrimeraAlineacion = True  # Bandera para saber cual es la alineación del primer campo
        alineacion_Actual = 0  # Alineación actual del tipo
        bit_desperdiciados =0  # Bits desperdiciados en el tipo
        existeCompuesto = False  # Bandera para saber si existe un tipo compuesto dentro del tipo actual
        listaUnion= [] # Lista para almacenar las alineaciones de los campos en una unión
       

        # Para cada campo del tipo compuesto
        for campo in tipo.campos:
            # Se obtiene los detalles del campo desde el diccionario de tipos
            campo_dato = self.tipos[campo]
            if isinstance(campo_dato, TipoAtomico):  # Si el campo es un tipo atómico
                representacion = campo_dato.representacion
                alineacion = campo_dato.alineacion
                # Se establece la alineación del primer campo
                if PrimeraAlineacion:
                    alineacion_empaquetado = alineacion
                    alineacion_no_empaquetado = alineacion
                    PrimeraAlineacion = False
                # Cálculo si las alineaciones coinciden
                if (alineacion_Actual % alineacion) == 0:
                    size_no_empaquetado += representacion
                    alineacion_Actual += representacion 
                # Cálculo si las alineaciones no coinciden 
                else:
                    size_no_empaquetado += (alineacion - (alineacion_Actual % alineacion)) + representacion
                    if not es_union:
                        bit_desperdiciados += (alineacion - (alineacion_Actual % alineacion))
                    alineacion_Actual += (alineacion - (alineacion_Actual % alineacion)) + representacion
                    
                
            elif isinstance(campo_dato, TipoCompuesto):  # Si el campo es un tipo compuesto (struct o union)
                # Se hace la llamada recursiva para calcular tamaño y alineación del tipo compuesto  
                existeCompuesto = True
                # Para cuando se busca el mejor reordenamiento
                if optimo:
                    representacion_no_empaquetada, ali_empaquetado, bits =self.mejor_reordenamiento(campo_dato.nombre, self.size_alineacion)
                    representacion= representacion_no_empaquetada
                    alineacion = ali_empaquetado
                    bit_desperdiciados += bits
                # Calculo recursivo para averiguar el tamaño y alineación
                else:
                    representacion, representacion_no_empaquetada, ali_empaquetado, _, bits =self.size_alineacion(campo_dato.nombre, self.es_union(campo_dato.nombre))
                    alineacion = ali_empaquetado
                    bit_desperdiciados += bits
                # Se establece la alineación del primer campo compuesto
                if PrimeraAlineacion:
                    alineacion_empaquetado = alineacion
                    alineacion_no_empaquetado = alineacion
                    PrimeraAlineacion = False
                # Cálculo si las alineaciones coinciden
                if (alineacion_Actual % ali_empaquetado) == 0:
                    size_no_empaquetado += representacion_no_empaquetada
                    alineacion_Actual += representacion_no_empaquetada
                # Cálculo si las alineaciones no coinciden
                else:
                    size_no_empaquetado += (ali_empaquetado - (alineacion_Actual % ali_empaquetado)) + representacion_no_empaquetada
                    if not es_union:
                        bit_desperdiciados += (ali_empaquetado - (alineacion_Actual % ali_empaquetado))
                    alineacion_Actual += (ali_empaquetado - (alineacion_Actual % ali_empaquetado)) + representacion_no_empaquetada
                    

            else:
                raise TypeError(f"Tipo no reconocido: {campo}")

            

            if es_union:
             # Para uniones, el tamaño es el del campo más grande
                if isinstance(campo_dato, TipoAtomico):
                    representacion_no_empaquetada = representacion
                union_emp = max(union_emp, representacion)
                union_no_emp= max(union_no_emp, representacion_no_empaquetada)
                listaUnion.append(alineacion)
                if not existeCompuesto:
                    bit_desperdiciados =0
                
            
            # Para estructuras, se suman los tamaños de representación y no empaquetados
            size_empaquetado += representacion
    
            
        
        if es_union:
            # Para uniones
            size_empaquetado = union_emp
            size_no_empaquetado = union_no_emp
            alineacion_empaquetado = math.lcm(*listaUnion)
            alineacion_no_empaquetado = alineacion_empaquetado
        
        return size_empaquetado, size_no_empaquetado, alineacion_empaquetado, alineacion_no_empaquetado, bit_desperdiciados




    def mejor_reordenamiento(self, tipo_nombre, funcion_evaluadora):
        tipo_original = self.tipos[tipo_nombre]
        resultados = []

        # Guardar copia del orden original
        campos_originales = tipo_original.campos[:]

        for perm in itertools.permutations(campos_originales):
            # Crear una copia del tipo compuesto con los campos reordenados
            tipo_copia = copy.deepcopy(tipo_original)
            tipo_copia.campos = list(perm)

            # Evaluar con la función externa usando el nombre del tipo copia
            self.tipos[tipo_nombre] = tipo_copia
            resultado = funcion_evaluadora(tipo_nombre, self.es_union(tipo_nombre), True)

            size_no_empaquetado = resultado[1]
            alineacion_no_empaquetado = resultado[3]
            bit = resultado[4]

            resultados.append((size_no_empaquetado, alineacion_no_empaquetado, bit))

        # Restaurar el tipo original en el diccionario
        self.tipos[tipo_nombre] = tipo_original

        # Seleccionar el mínimo por size_no_empaquetado
        mejor_size, mejor_alineacion, bits = min(resultados, key=lambda x: x[0])
        return mejor_size, mejor_alineacion, bits





    def describir_tipo(self, nombre):
        """Método que proporciona la descripción de un tipo"""
        if nombre not in self.tipos:
            print(f"Error: el tipo '{nombre}' no está definido.")
            return
        tipo = self.tipos[nombre]
        if isinstance(tipo, TipoAtomico): # Si es atómico
            print(f"Tipo Atómico: {tipo.nombre}")
            print(f"Representación(Empaquetado,Optimo,Ordenado): {tipo.representacion} bytes")
            print(f"Alineación: {tipo.alineacion} bytes")
            print(f"Bytes desperdiciados: {0} bytes")
        elif isinstance(tipo, TipoCompuesto): # Si es compuesto
            es_union = self.es_union(nombre) # Se verifica si el tipo es union

            print(f"Tipo {'Union' if es_union else 'Struct'}: {tipo.nombre}")
            self.describir_registro(nombre, es_union)
        else:
            print(f"Tipo desconocido: {tipo}")

    def es_union(self, nombre):
        """Método que verifica si un tipo es union"""
        return self.tipos[nombre].es_union

    def describir_registro(self, nombre, es_union):
        """Método que proporciona la descripción de un registro"""
        size_empaquetado, size_no_empaquetado, alineacion_empaquetado, alineacion_no_empaquetado, bit_desperdiciados = self.size_alineacion(nombre, es_union)
        size_optimo, alineacion_optimo, bits_optimo = self.mejor_reordenamiento(nombre, self.size_alineacion)
        print(f"Tamaño empaquetado: {size_empaquetado} bytes")
        print(f"Alineación empaquetado: {alineacion_empaquetado} bytes")
        print(f"Tamaño no empaquetado: {size_no_empaquetado} bytes")
        print(f"Alineación no empaquetado: {alineacion_no_empaquetado} bytes")
        print(f"Tamaño óptimo: {size_optimo} bytes")
        print(f"Alineación óptimo: {alineacion_optimo} bytes")
        print(f"Bytes desperdiciados (empaquetado): {0} bytes")
        print(f"Bytes desperdiciados (no empaquetado): {bit_desperdiciados} bytes")
        print(f"Bytes desperdiciados (óptimo): {bits_optimo} bytes")

def main():
    """Método principal"""
    manejador = ManejadorTipos()
    while True:
        accion = input("Ingrese una acción: ")
        partes = accion.split() # Se separa en partes la acción ingresada 
        comando = partes[0]
        match comando:
            case "ATOMICO":
                if len(partes) != 4:
                    print("Error: faltan argumentos o hay argumentos de mas")
                    continue
                nombre = partes[1]
                representacion = int(partes[2])
                alineacion = int(partes[3])
                manejador.agregar_tipo_atomico(nombre, representacion, alineacion) 
            case "STRUCT":
                nombre = partes[1]
                tipos_campos = partes[2:]
                manejador.agregar_tipo_compuesto(nombre, tipos_campos)  
            case "UNION":
                nombre = partes[1]
                tipos_campos = partes[2:]
                manejador.agregar_tipo_compuesto(nombre, tipos_campos, es_union=True)
            case "DESCRIBIR":
                if len(partes) != 2:
                    print("Error: faltan argumentos o hay argumentos de mas")
                    continue
                nombre = partes[1]
                manejador.describir_tipo(nombre)
            case "SALIR":
                print("Saliendo")
                break
            case _:
                print(f"Accion {comando} desconocida")

if __name__ == "__main__":
    main()
