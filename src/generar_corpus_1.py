import pandas as pd
import json

from datetime import datetime


'''

Corpus 1:

En este caso se utilizan solo los registros cuyos timestamp se encuentre presente tanto en 
el archivo del aparato como en el de consumo agregado. 
Se mantienen registros exactos pero se desperdician demasiados datos.

MODELO BINARIO donde se considera encendido el aparato si su consumo supera cierto valor de standby.

Cada vector de entrada  tiene la siguientes forma:

-- ENCENDIDO_ANT
-- HORAS_APAGADO
-- CONSUMO_AGREGADO
-- DIA_MEDICION

'''


def generar_corpus_1(path_data, path_aggregate, consumo_standby, escribir_archivo):

    # Cargo los dataframes utilizando los timestamps como indice
    agg_file_panda = pd.read_csv(path_aggregate, sep=" ", header=None)
    agg_file_panda.columns = ["Timestamp", "Consumo"]
    agg_file_panda = agg_file_panda.set_index("Timestamp")

    app_file_panda = pd.read_csv(path_data, sep=" ", header=None)
    app_file_panda.columns = ["Timestamp", "Consumo"]
    app_file_panda = app_file_panda.set_index("Timestamp")

    # Vectores de entrenamiento
    vectores_entrada = []
    predicciones_entrada = []

    encendido_ant = 0
    horas_apagado = 0
    registro_horario_ant = 0

    # Para cada registro
    for index, row in app_file_panda.iterrows():

        # Si existe timestamp en el archivo de consumo agregado
        if index in agg_file_panda.index:

            consumo_medicion = row["Consumo"]

            # Caracteristica CONSUMO_AGREGADO
            consumo_agregado = agg_file_panda.loc[index]["Consumo"]

            # Caracteristica FIN_SEMANA
            dia_medicion = datetime.fromtimestamp(index).strftime("%A")

            if dia_medicion == 'Saturday' or dia_medicion == 'Sunday':
                dia_medicion = 1
            else:
                dia_medicion = 0

            # Caracteristica HORAS_APAGADO
            if registro_horario_ant > 0:

                # Segundos desde la medicion anterior
                seconds_past = datetime.fromtimestamp(index - registro_horario_ant).strftime("%S")
                horas_apagado += float(seconds_past)

            # Genero vector de caracteristicas
            vector_entrada = [encendido_ant, horas_apagado, consumo_agregado, dia_medicion]
            vectores_entrada.append(vector_entrada)

            # Actualiza caracteristica de encendido
            if consumo_medicion <= consumo_standby:
                encendido_ant = 0
                registro_horario_ant = int(index)
            else:
                encendido_ant = 1
                horas_apagado = 0
                registro_horario_ant = 0

            # Genera el vector de salida
            predicciones_entrada.append(encendido_ant)

    if escribir_archivo:

        store = {
            "features": vectores_entrada,
            "activations": predicciones_entrada
        }

        file = open("generar_corpus_1", "w+")
        file.write(json.dumps(store))
        file.close()

    return vectores_entrada, predicciones_entrada


if __name__ == "__main__":
    _path_data = ""
    _path_aggregate = ""
    _consumo_standby = 0
    _escribir_archivo = True

    generar_corpus_1(_path_data, _path_aggregate, _consumo_standby, _escribir_archivo)
