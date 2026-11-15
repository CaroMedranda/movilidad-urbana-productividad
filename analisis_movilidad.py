# ==========================================
# PROYECTO: MOVILIDAD URBANA Y PRODUCTIVIDAD
# ==========================================

# PASO 1. CARGAR Y EXPLORAR LOS DATOS

# Importar librerías

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================
# PASO 2. CARGAR LOS ARCHIVOS
# ==========================================

# Cargar archivo de movilidad
traffic = pd.read_csv('data/tomtom_traffic.csv')

# Cargar archivo de economía
eco = pd.read_csv('data/oecd_city_economy.csv')

# Mostrar las primeras 5 filas de movilidad
print(traffic.head(5))

# Mostrar las primeras 5 filas de economía
print(eco.head(5))

# ==========================================
# PASO 3. EXAMINAR LA ESTRUCTURA DE LOS DATOS
# ==========================================

# Examinar la estructura de traffic

print(traffic.info())
print(traffic.head(3))


# Examinar la estructura de eco

print(eco.info())
print(eco.head(3))

# ==========================================
# PASO 4. RENOMBRAR LAS COLUMNAS
# ==========================================

# Estandarizar los nombres de las columnas de traffic

traffic = traffic.rename(columns={
    'Country': 'country',
    'City': 'city',
    'UpdateTimeUTC': 'update_time_utc',
    'JamsDelay': 'jams_delay',
    'TrafficIndexLive': 'traffic_index_live',
    'JamsLengthInKms': 'jams_length_in_kms',
    'JamsCount': 'jams_count',
    'TrafficIndexWeekAgo': 'traffic_index_week_ago',
    'UpdateTimeUTCWeekAgo': 'update_time_utc_week_ago',
    'TravelTimeLivePer10KmsMins': 'travel_time_live_per_10_kms_mins',
    'TravelTimeHistoricPer10KmsMins': 'travel_time_historic_per_10_kms_mins',
    'MinsDelay': 'mins_delay'
})

# Verificar cambios en traffic

print(traffic.columns)


# Estandarizar los nombres de las columnas de eco

eco = eco.rename(columns={
    'Country': 'country',
    'City GDP/capita': 'city_gdp_capita',
    'Unemployment %': 'unemployment_percent',
    'Year': 'year',
    'City': 'city',
    'PM2.5 (μg/m³)': 'pm25_level',
    'Population (M)': 'population_million'
})

# Verificar cambios en eco

print(eco.columns)

# ==========================================
# PASO 5. CORREGIR FORMATOS NUMÉRICOS Y DE FECHA
# ==========================================

# Convertir las columnas de traffic a formato datetime
traffic['update_time_utc'] = pd.to_datetime(
    traffic['update_time_utc'], errors='coerce', utc=True
)

traffic['update_time_utc_week_ago'] = pd.to_datetime(
    traffic['update_time_utc_week_ago'], errors='coerce', utc=True
)

# Verificar los cambios en traffic
print(traffic.info())


# Limpiar y convertir valores numéricos de eco

# Convertir city_gdp_capita a float
eco['city_gdp_capita'] = (
    eco['city_gdp_capita'].astype(str)
    .str.replace('.', '')
    .str.replace(',', '.')
    .astype(float)
)

# Convertir unemployment_percent a float
eco['unemployment_percent'] = (
    eco['unemployment_percent'].astype(str)
    .str.replace('%', '')
    .str.replace(',', '.')
    .astype(float)
)

# Convertir pm25_level a float
eco['pm25_level'] = (
    eco['pm25_level'].astype(str)
    .str.replace(',', '.')
    .astype(float)
)

# Convertir population_million a float
eco['population_million'] = (
    eco['population_million'].astype(str)
    .str.replace(',', '.')
    .astype(float)
)

# Calcular la población total en unidades absolutas
eco['population'] = eco['population_million'] * 1000000

# Verificar los cambios en eco
print(eco.info())
print(eco.head(3))

# ==========================================
# PASO 6. EXTRAER AÑO Y FILTRAR DATOS DE 2024
# ==========================================

# Extraer el año de las fechas en update_time_utc
traffic['year'] = traffic['update_time_utc'].dt.year

# Verificar el cambio
print(traffic.head(3))


# Filtrar los registros del año 2024
traffic_2024 = traffic[traffic['year'] == 2024].copy()

eco_2024 = eco[eco['year'] == 2024].copy()


# Revisar los nuevos DataFrames
print(display(traffic_2024.head()))
print(display(eco_2024.head()))

# ==========================================
# PASO 7. CALCULAR PROMEDIOS DE TRÁFICO POR CIUDAD
# ==========================================

# Calcular los promedios de tráfico por ciudad, país y año
traffic_city_year_2024 = traffic_2024.groupby(
    ['city', 'country', 'year']
).agg({
    'jams_delay': 'mean',
    'traffic_index_live': 'mean',
    'jams_length_in_kms': 'mean',
    'jams_count': 'mean',
    'mins_delay': 'mean',
    'travel_time_live_per_10_kms_mins': 'mean',
    'travel_time_historic_per_10_kms_mins': 'mean'
}).reset_index()

# Mostrar resultado
print(traffic_city_year_2024.head())


# Ordenar las ciudades por promedio de retraso de tráfico
traffic_city_year_2024.sort_values(
    ["jams_delay"], ascending=False
)

# PASO 8. UNIR MOVILIDAD Y ECONOMÍA

# Seleccionar columnas clave de tráfico y economía
left_cols = [
    'city', 'country', 'year', 'jams_delay',
    'traffic_index_live', 'jams_length_in_kms',
    'jams_count', 'mins_delay',
    'travel_time_live_per_10_kms_mins',
    'travel_time_historic_per_10_kms_mins'
]

right_cols = [
    'city', 'year', 'city_gdp_capita',
    'unemployment_percent', 'pm25_level', 'population'
]

# Crear los dos nuevos datasets reducidos
traffic_2024_small = traffic_city_year_2024[left_cols].copy()
eco_2024_small = eco_2024[right_cols].copy()

# Unir datasets
merged = pd.merge(
    traffic_2024_small,
    eco_2024_small,
    on=['city', 'year'],
    how='inner'
)

# Mostrar las primeras 5 filas
print(merged.head(5))

# Crear boxplot para observar el comportamiento de los minutos de congestión
# Obtener promedio para mostrarlo en título
mean_value = merged['jams_delay'].mean()

# Crear gráfico
sns.boxplot(data=merged, y='jams_delay', showmeans=True)

plt.title(f'Boxplot de JamsDelay (2024)\nPromedio: {mean_value:.2f}')

plt.show()

# Crear histograma para ver la distribución de la economía (city_gdp_capita)

sns.histplot(data=merged, x='city_gdp_capita')

plt.title('Distribución de la economía')

plt.xlabel('Valor promedio del per cápita (PIB)')

plt.ylabel('Frecuencia (Número de Registros)')

plt.show()

# Gráfico de barras para comparar jams_delay y city_gdp_capita por ciudad

merged.plot(
    kind='bar',
    x='city',
    y=['jams_delay', 'city_gdp_capita']
)

plt.xticks(rotation=90)

plt.show()

# Exportar el dataset final como CSV
merged.to_csv("ladb_mobility_economy_2024_clean.csv", index=False)
