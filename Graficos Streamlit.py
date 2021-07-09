#!/usr/bin/env python
# coding: utf-8

# # Inicialização do ambiente
# Essentials
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

import warnings, time
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Plots
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

# Estebelece limites para visualização no notebook
pd.set_option('display.max_columns',100)
pd.set_option('display.max_rows',500)

# Limita a 3 casas decimais a apresentação das variaveis tipo float
pd.set_option('display.float_format', lambda x: '{:.3f}'.format(x))

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# ==========================================================
# Carrega base de dados do instrumento
df1 = pd.read_csv('df_instrumento.csv', sep=';', encoding='utf-8', parse_dates=['data'], index_col=['data'])
df_host = pd.read_csv('df_host.csv', sep=';', encoding='utf-8', index_col=['host'])

paginas = ['Intro', 'Dados']
pagina = st.sidebar.selectbox('Selecione a página que deseja visualizar', paginas)

if pagina == 'Intro':
	st.markdown('## **Descrição Geral**')
	
	'''
	Este app foi criado para apresentar de forma rápida e interativa gráficos criados a partir de 
	consolidações dos dados capturados pelos sensores de temperatura instalados nas salas de servidor.
	
	
	Os dados aqui apresentados foram devidamente tratados e **anonimizados** por questões de segurança e governança. 
	
	Representam somente as coletas de temperatura.
	
	Esse app é uma demonstração simples do que pode ser feito em Python utilizando a biblioteca Streamlit. Maiores informações sobre a biblioteca
	podem ser encontradas no site https://streamlit.io/
	
	'''

elif pagina == 'Dados':
	var = st.selectbox('Escolha o instrumento',df1.columns)
	site = df_host.loc[var, 'site']
	st.write('Este instrumento está em ', site)

	tmax = round(df1[var].max(),2)
	tmin = round(df1[var].min(),2)

	# Tabela 1 - Médias diária e semanal
	st.markdown('### Médias diárias dos valores de temperatura capturados pelo sensor')
	x = pd.DataFrame(df1[var].resample('1H').mean())
	x.reset_index(inplace=True, drop=False)
	x.columns = ['data', 'media_diaria']
	#st.line_chart(x)
	st.write(x)

	st.text('Valores extremos observados no periodo:')
	st.write('Máximo - ', tmax)
	st.write('Mínimo - ', tmin)

	# mapeia ambiente para construção de 5 gráficos 
	st.markdown('## Gráficos')

	f, axes = plt.subplots(nrows=4, ncols=5)
	plt.rcParams['figure.figsize'] = [22, 22]
	plt.subplots_adjust(wspace=0.25, hspace=0.23)

	ax1 = plt.subplot2grid((4, 5), (0, 0), colspan=5, rowspan=2)
	ax2 = plt.subplot2grid((4, 5), (2, 0), colspan=5, rowspan=1)
	ax3 = plt.subplot2grid((4, 5), (3, 0), colspan=2, rowspan=1)
	ax4 = plt.subplot2grid((4, 5), (3, 2), colspan=2, rowspan=1)
	ax5 = plt.subplot2grid((4, 5), (3, 4))

	# Graficos
	tipo = 'Temperatura Interna'

	# Gráfico 1 - Médias diária e semanal
	x = df1[var].resample('1H').apply([np.mean])
	y = df1[var].resample('W').apply([np.mean])

	ax1.plot(x, label='Média a cada hora')
	ax1.plot(y, label='Média semanal')
	ax1.set_title('Médias de ' + tipo + ' de ' +var, fontsize=25)
	ax1.set_xlabel('')
	ax1.set_ylabel(tipo, fontsize=15)
	ax1.legend(fontsize=14)
	ax1.grid(color='lightgray', linestyle='-', linewidth=0.5)
	
	# Grafico 2 - Estatisicas de cada semana
    
	df2 = df1[var].copy()
	df2 = pd.DataFrame(df2)
	(df2.assign(periodo=lambda df: df1.index.weekofyear)
	    .groupby('periodo')[var].agg(["mean", "median", "min", "max"])
        .plot(ax=ax2, marker="o",linewidth=1))
	
	ax2.set_title('Estatísticas a cada semana', fontsize=25)
	ax2.set_xlabel('')
	ax2.set_ylabel(tipo, fontsize=15)
	

	# Gráfico 3 - Histograma
	#sns.distplot(df1[var] , ax=ax3, fit=norm)
	df1[var].hist(bins = 30, ax=ax3)
	ax3.set_xlabel(tipo, fontsize=16)
	ax3.set_ylabel('Ocorrências', fontsize=16)
	ax3.set_title('Distribuição no periodo todo', fontsize=18)

	# Gráfico 4 - Boxplot
	sns.boxplot(x=df1.index.month, y=var, data=df1, ax=ax4, orient="v", palette="Set2")
	ax4.set_xlabel('Meses', fontsize=16)
	ax4.set_ylabel('')
	ax4.set_title('Distribuição nos meses', fontsize=18)

	# Gráfico 5 - Distribuição
	sns.stripplot(x=df1.index.month, y=var, data=df1, ax=ax5)
	ax5.set_xlabel('Meses', fontsize=16)
	ax5.set_ylabel('')
	ax5.set_title('Distribuição nos meses', fontsize=18)

	plt.show()
	st.pyplot(f)

