from excel_manager import ExcelManager
from math import sin, cos, radians


discretizacion_angulo = 1  # Grados
discretizacion_radio = 1  # km/h

class ElementoArco():
    def __init__(self, angulos, radios, area_padre, frecuencia_padre):
        self.area = radians(angulos[1] - angulos[0])*(radios[1]**2 - radios[0]**2)/2
        angulo_medio = radians(angulos[1]+angulos[0])/2
        radio_medio = (radios[1]+radios[0])/2
        self.frecuencia = self.area/area_padre * frecuencia_padre
        self.yg = cos(angulo_medio) * radio_medio
        self.xg = sin(angulo_medio) * radio_medio


class FrecuenciaPolar():

    ang_por_direccion = {
        "N": 0,
        "EN": 45,
        "E": 90,
        "SE": 135,
        "S": 180,
        "SW": 225,
        "W": 270,
        "NW": 315,
    }

    def __init__(self, frecuencia, direccion, intensidad):
        try:
            self.frecuencia = frecuencia
            self.direccion = direccion
            self.radio_menor, self.radio_mayor = self .obtener_intensidades(intensidad)
            self.intensidad_media = (self.radio_mayor+self.radio_menor)/2
            angulo_medio = self.ang_por_direccion.get(direccion)
            self.ang_menor, self.ang_mayor = self.obtener_angulo_menor_y_mayor(angulo_medio)
            self.xg = sin(radians(angulo_medio)) * self.intensidad_media if angulo_medio is not None else 0
            self.yg = cos(radians(angulo_medio)) * self.intensidad_media if angulo_medio is not None else 0
            self.area = self.obtener_area()
            self.elementos = self.obtener_elementos()
        except TypeError as e:
            print(e)

    def obtener_elementos(self):
        resultado = []
        if self.frecuencia == 0:
            return resultado
        for ang in range(int(self.ang_menor-discretizacion_angulo/2), int(self.ang_mayor-discretizacion_angulo/2), discretizacion_angulo):
            for radio in range(self.radio_menor, self.radio_mayor, discretizacion_radio):
                resultado.append(ElementoArco(
                    angulos=(ang+discretizacion_angulo/2, ang+discretizacion_angulo*3/2),
                    radios=(radio, radio+discretizacion_radio),
                    area_padre=self.area,
                    frecuencia_padre=self.frecuencia
                ))
        return resultado

    def obtener_area(self):
        if self.ang_mayor == 361:  # En el caso del circulo completo, se debe realizar este ajuste
            return radians(self.ang_mayor-self.ang_menor-1)*(self.radio_mayor**2-self.radio_menor**2)/2
        return radians(self.ang_mayor-self.ang_menor)*(self.radio_mayor**2-self.radio_menor**2)/2

    def obtener_angulo_menor_y_mayor(self, angulo_medio):
        if angulo_medio is None:
            return 0, 361
        return angulo_medio - 45 / 2, angulo_medio + 45 / 2

    def obtener_intensidades(self, intensidad):
        return (int(x) for x in intensidad.split("-"))


class LineasIntensidad24():
    def __init__(self, angulo_vertical):
        angulo_vertical = radians(angulo_vertical)
        self.ecuacion_recta_1 = lambda x, y: cos(-angulo_vertical) * x + sin(-angulo_vertical) * y - 24  # Esta es la que está a la derecha
        self.ecuacion_recta_2 = lambda x, y: cos(-angulo_vertical) * x + sin(-angulo_vertical) * y + 24  # Esta es la que está a ala izquierda

    def saber_si_elemento_esta_entre_lineas(self, elemento: ElementoArco):
        """Recordatorio de algebra: sean dos ecuaciones de rectas paralelas Ax+By+C; si el producto
        de los resultados resulta negativo entonces el punto se encuentra entre las mismas líneas."""
        x, y = elemento.xg, elemento.yg
        return self.ecuacion_recta_1(x, y) * self.ecuacion_recta_2(x, y) <= 0


class ObtenerMayorOperatividadPista():

    def __init__(self, nombre_de_planilla, nombre_de_hoja):
        self.excel = ExcelManager(nombre_de_planilla, nombre_de_hoja)
        self.lista_frecuencias_polares = self.obtener_frecuencias_polares()

    def obtener_frecuencias_polares(self):
        resultado = []
        lista_columna = ['B', 'C', 'D', 'E', 'F']
        lista_filas = list(range(4, 13))
        for columna in lista_columna:
            for fila in lista_filas:
                direccion = self.excel.get_value("A", fila)
                intensidad = self.excel.get_value(columna, 3)
                frecuencia = self.excel.get_value(columna, fila) or 0
                frecuencia_polar = FrecuenciaPolar(frecuencia, direccion, intensidad)
                resultado.append(frecuencia_polar)
        return resultado

    def encontrar_operatividad_maxima_1_pista(self):
        angulos_que_dan_maxima_operatividad = [0]
        maxima_operatividad = self.operatividad_segun_angulo_1_pista(0)
        for angulo in range(1, 181):
            operatividad = self.operatividad_segun_angulo_1_pista(angulo)
            if operatividad > maxima_operatividad:
                angulos_que_dan_maxima_operatividad = [angulo]
                maxima_operatividad = operatividad
            elif operatividad == maxima_operatividad:  # Si es lo mismo lo sumamos a la lista de resultados
                angulos_que_dan_maxima_operatividad.append(angulo)
        return maxima_operatividad, angulos_que_dan_maxima_operatividad

    def encontrar_operatividad_maxima_2_pistas(self):
        angulos_que_dan_maxima_operatividad = []
        maxima_operatividad = 0
        for angulo_1 in range(0, 181):
            for angulo_2 in range(1, 182):
                if angulo_1 != angulo_2:
                    operatividad = self.operatividad_segun_angulo_2_pistas(angulo_1, angulo_2)
                    if operatividad > maxima_operatividad:
                        angulos_que_dan_maxima_operatividad = [(angulo_1, angulo_2)]
                        maxima_operatividad = operatividad
                    elif operatividad == maxima_operatividad:  # Si es lo mismo lo sumamos a la lista de resultados
                        angulos_que_dan_maxima_operatividad.append((angulo_1, angulo_2))
        return maxima_operatividad, angulos_que_dan_maxima_operatividad

    def operatividad_segun_angulo_1_pista(self, angulo):
        suma = 0
        lineas_intensidad_24 = LineasIntensidad24(angulo)
        for frecuencia_polar in self.lista_frecuencias_polares:
            for elemento in frecuencia_polar.elementos:
                esta_dentro = lineas_intensidad_24.saber_si_elemento_esta_entre_lineas(elemento)
                if esta_dentro:
                    suma = suma + elemento.frecuencia
        return suma

    def operatividad_segun_angulo_2_pistas(self, angulo_1, angulo_2):
        suma = 0
        lineas_intensidad_24_1 = LineasIntensidad24(angulo_1)
        lineas_intensidad_24_2 = LineasIntensidad24(angulo_2)
        for frecuencia_polar in self.lista_frecuencias_polares:
            for elemento in frecuencia_polar.elementos:
                esta_dentro_de_1 = lineas_intensidad_24_1.saber_si_elemento_esta_entre_lineas(elemento)
                esta_dentro_de_2 = lineas_intensidad_24_2.saber_si_elemento_esta_entre_lineas(elemento)
                if esta_dentro_de_1 or esta_dentro_de_2:
                    suma = suma + elemento.frecuencia
        return suma