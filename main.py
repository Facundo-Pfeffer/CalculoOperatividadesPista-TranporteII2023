from calculo_de_operatividades import ObtenerMayorOperatividadPista


nombre_de_planilla = "Datos.xlsx"
nombre_de_hoja = "Grupo 6"


problema = ObtenerMayorOperatividadPista(nombre_de_planilla, nombre_de_hoja)
resultado_problema_1 = problema.encontrar_operatividad_maxima_1_pista()
print(f"La operatividad máxima para una pista es {resultado_problema_1[0]} para una pista y se da para las direcciones {resultado_problema_1[1]}")

resultado_problema_2 = problema.encontrar_operatividad_maxima_2_pistas()
print(f"La operatividad máxima para dos pistas es {resultado_problema_2[0]} para una pista y se da para las direcciones {resultado_problema_2[1]}")

resultado_operatividad = problema.operatividad_segun_angulo_2_pistas(60, 140)
print(resultado_operatividad)