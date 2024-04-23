#!/usr/bin/env python
# coding: utf-8

# In[1]:


import panel as pn
import pandas as pd
import numpy as np
import hvplot.pandas
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")
pn.extension('tabulator')


# In[2]:


df = pd.read_csv('new_df.csv')
df.head()


# In[3]:


# создание дополнительной таблицы для графика распределения энергопотребления по годам и времени суток
new_df = df.groupby(['year', 'Time_of_day'])['Value (kWh)'].mean().reset_index()
sum_by_year = new_df.groupby('year')['Value (kWh)'].sum()
new_df = new_df.merge(sum_by_year, on='year', how='left')
new_df = new_df.rename(columns={'Value (kWh)_y': 'Yearly_sum', 'Value (kWh)_x': 'Value (kWh)'})
new_df['Percentage'] = (new_df['Value (kWh)'] / new_df['Yearly_sum']) * 100


# In[4]:


new_df.head()


# In[5]:


new_idf = new_df.interactive()
idf = df.interactive()


# In[6]:


season_selection = pn.widgets.Select(
    description="Выберите отображаемое на графике время года",
    name="Время года:",
    options=["зима", "весна", "лето", "осень"],
)


# ## 1 график: общий тренд

# In[7]:


smoothing_slider = pn.widgets.FloatSlider(name='Сглаживание',
                                          start=1, end=20, step=2, value=1)


# In[8]:


temp_value = (
    idf
    .groupby(['Temp_avg'])['Value (kWh)']
    .mean()
    .reset_index()
    .rolling(smoothing_slider).mean()
)


# In[9]:


temp_value_plot = temp_value.hvplot(
    x='Temp_avg', 
    y='Value (kWh)', 
    kind='line',
    color='#DD5746',
    xlabel='Средняя температура, F', 
    ylabel='Среднее энергопотребление (кВтч)', 
    title='Тренд средней температуры и среднего энергопотребления')


# ## 2 график: по годам и времени суток

# In[10]:


radio_group_year = pn.widgets.RadioButtonGroup(
    name='Год', 
    description="Выберите год для отображения данных",
    options=['2016', '2017', '2018', '2019', '2020'], 
    button_type='default'
)


# In[11]:


value_year = (
    new_idf[
    new_idf.year.astype(str) ==  radio_group_year 
    ]
    .groupby(['year', 'Time_of_day'])['Percentage']
    .mean()
    .reset_index()
)


# In[12]:


value_year_bar = value_year.hvplot(
    x='Time_of_day',
    y='Percentage', 
    kind='bar',
    xlabel='Время суток',
    ylabel='Процент энергопотребления',
    color='#FFC470'                               
)


# ## 3 график: зависимость среднего энергопотребления от температуры по временам года

# In[13]:


temp_value_seasonal = (
    idf[
    idf.season == season_selection 
    ]
    .groupby(['Temp_avg', 'season'])['Value (kWh)']
    .mean()
    .reset_index()
)


# In[14]:


temp_value_seasonal_plot = temp_value_seasonal.hvplot(
    x='Temp_avg', 
    y='Value (kWh)', 
    kind='scatter',
    color='#4793AF',
    xlabel='Средняя температура, F', 
    ylabel='Среднее энергопотребление (кВтч)', 
    title='Связь средней температуры и среднего потребления энергии по сезонам'
)


# In[15]:


avg_energy_consumpt_seasonal = pn.indicators.Gauge(
    name='Среднее энергопотребление', 
    value=temp_value_seasonal['Value (kWh)'].mean().round(2), 
    bounds=(0.5, 1.2), 
    format='{value} кВтч', 
    colors=[(0.2, '#2e734f'), (0.8, '#FFC470'), (1, '#DD5746')]
)


# In[16]:


avg_temp_seasonal = pn.indicators.Number(
    name="Средняя температура",
    value=temp_value_seasonal['Temp_avg'].mean().round(1),
    format="{value} F",
    colors=[(65, "#4793AF"), (73, '#2e734f'), (100, '#DD5746')],
)


# ## Шаблон дашборда

# In[17]:


template = pn.template.FastListTemplate(
    title='Энергопотребление', 
    sidebar=[pn.pane.Markdown("# Температура и потребление энергии: исследование взаимосвязи"), 
             pn.pane.Markdown("#### Корректное учет температуры окружающей среды имеет огромное значение для прогнозирования потребления электроэнергии.Точные прогнозы потребления электроэнергии особенно критичны в контексте роста экологических вызовов и стремления к устойчивому развитию. Понимание влияния температуры на потребление энергии позволяет эффективно управлять ресурсами и минимизировать негативное воздействие на окружающую среду."),
             pn.pane.GIF('energy.gif', sizing_mode='scale_both')],
    main=[pn.Row(pn.Column(smoothing_slider, temp_value_plot.panel(width=550, height=350)), 
                 pn.Column(radio_group_year, value_year_bar.panel(width=550, height=350))), 
          pn.Row(pn.Column(
              pn.Row(avg_temp_seasonal), 
              pn.Row(avg_energy_consumpt_seasonal)), 
                 pn.Column(season_selection, temp_value_seasonal_plot.panel(width=700, height=400)))],
    accent_base_color="#4793AF",
    header_background="#4793AF",
)
#template.show()
template.servable()


# In[ ]:




