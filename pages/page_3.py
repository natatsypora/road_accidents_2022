import streamlit as st
import pandas as pd
from get_data import *
from plotly_charts_functions import *

# read CSV and Excel data
data_excel = read_excel_data(url_3)
df = read_csv_data(url)
# Store data in the session state
st.session_state.df = df
st.session_state.data_excel = data_excel

#---------------------------------------------------------------
def crosstab_with_normindex_top_n (df, index, column, top=7):
    try:
        table = pd.crosstab(df[index], [ df[column]], margins=True
                                ).sort_values(by='All', ascending=False).iloc[1:, :-1] 
        table.index = [('<br>').join(el.split(' ', 1)) for el in table.index.values]                               
        return table.div(table.sum(axis=1), axis=0).iloc[:top, :]        
    except Exception as e:
      st.error(f'Error: {e} {e.__class__}') 
      
#---------------------------------------------------------------  
 
df_month_day = data_excel['month_day_all'].fillna(0)

df_shaa = 100*df['SHAA'].value_counts(normalize=True).to_frame('% from total')

df_shaa_humra = 100*pd.crosstab( df['SHAA'],
                                 df['HUMRAT_TEUNA'],
                                 normalize='columns')

df_day_humra = data_excel['month_type_all']

#----------Create tabs-------------------------------------------

chart_tabs = st.tabs(["YOY", "Month and Day", "Hour", 
                      "Day of the Week", "Type", "Speed and Road"])

#===============Plotly charts===================================

#---------------YOY---------------------------------------------
with chart_tabs[0]:  
    df_vs_last = data_excel['yoy'] 
    df_changes = df_vs_last.sum(axis=0).to_frame().T
    col_names = df_changes.columns.values
    
    # add metrics
    cards = st.columns(4)
    for i in range(4): 
        delta = df_changes[col_names[i]] - df_changes[col_names[i+4]]              
        my_metric = create_metric_card(df_vs_last.iloc[:, i], delta).update_layout(margin_t=0)    
        cards[i].plotly_chart(my_metric, theme=None, config = {'displayModeBar': False }) 
    
    # add yoy chart
    df_vs_last = df_vs_last.assign(Diff = df_vs_last['Total_2022'] - df_vs_last['Total_2021'])
    yoy_chart = yoy_subplots(df_vs_last, title="<b>Severity of Road Accidents vs PY<b>",
                subtitles=['Total', 'Slight', 'Serious', 'Fatal'], sort_month=sort_month_en[::-1])
    yoy_chart.update_layout(margin_t=100, margin_l=100, width=1100)
    st.plotly_chart(yoy_chart, theme=None) 

#---------------Month and Day-----------------------------------
with chart_tabs[1]:
    heatmap = heatmap_bar_subplots(
        df_month_day, title='Road Accidents by Month and Day'
        ).update_yaxes(categoryorder='array', categoryarray=sort_month_en[::-1]
        ).update_layout( margin_b=50 )
    if heatmap:
        st.plotly_chart(heatmap, theme=None) 

    heatmap_bar = heatmap_separate_by_columns2(df_day_humra,
                                               title='Road Accidents by Severity and Day')
    heatmap_bar.update_layout(margin_l=80, margin_b=20 )
    if heatmap_bar:
        st.plotly_chart(heatmap_bar, theme=None)

#---------------Hour -------------------------------------------         
with chart_tabs[2]:
    col_31, col_32 = st.columns([2.5, 1])

    with col_31:
        line_chart = line_plot_with_minmax(df_shaa, 
        title = 'The frequency of Road Accidents by Hours<br><sub>(as a percentage of total)<sub>')
        st.plotly_chart(line_chart, theme=None) 

        line_sub = line_subplots(df_shaa_humra, 
                title="The Severity of Road Accidents by Hours <br><sub>(% of total in each category)</sub>")
        st.plotly_chart(line_sub, theme=None) 

        df_shaa_index = 100*pd.crosstab(df['SHAA'], df['HUMRAT_TEUNA'] , normalize='index')
        bar_plot = bar_relative(df_shaa_index, 
                                title='The ratio of Severity Road Accidents <br><sub>(% during each hour)<sub>')
        st.plotly_chart(bar_plot, theme=None) 

    with col_32:        
        st.markdown('<p style="text-align: center; background-color: rgba(195,215,220, 0.7);\
                     border-radius: 10px; font-size: 20px;"\
                    >Road Accidents <br>by Severity and Hours</p>', unsafe_allow_html=True)
        
        df_shaa = pd.crosstab(df['SHAA'], df['HUMRAT_TEUNA'],
                              margins=True, margins_name='סה"כ').iloc[:-1, : ]
        df_shaa.index.name = None
        df_shaa.columns.name = None      

        df2 = df_shaa.style.highlight_max(props='color:white; background-color:rgba(255,0,0,0.7);'
            ).highlight_min(props='color:white; background-color:rgba(0,100,0,0.6);')
        st.write(df2.to_html(), unsafe_allow_html=True)    

#---------------Day of the Week --------------------------------
with chart_tabs[3]:
    
    col_area, col_bar = st.columns([1.4, 1])

    with col_area:
        df_week_perc = df['YOM_BASHAVUA'].value_counts().to_frame('cnt').assign(perc=lambda x : x/df.shape[0]*100)
        area_chart =area_plot_with_minmax(df_week_perc, sort_week,
                      title = 'The frequency of Road Accidents by Day of the Week').update_layout(margin=dict(t=100, b=50))
        st.plotly_chart(area_chart, theme=None)

    with col_bar:
        df_day_of_week = 100*pd.crosstab(df['YOM_BASHAVUA'], df['HUMRAT_TEUNA'] , normalize='index')           
        bar_text = bar_text_relative_mode(df_day_of_week, sort_week,
                        title='The ratio of Severity Road Accidents\
                                <br><sub>(% of total during each day of the week)</sub>').update_layout(margin=dict(l=50, r=20, t=100, b=50))
        st.plotly_chart(bar_text, theme=None)

    df_day_hours = crosstab_with_normindex_top_n(df, index='YOM_BASHAVUA',
                                                column='SHAA', top=7).T.reindex(columns=sort_week)
    scatter_line = scatter_line_subplots(df_day_hours,
                                         title = 'Road Accidents by Day of the Week and Hours')
    scatter_line.update_layout(plot_bgcolor='#e7eff2', yaxis_range=[0.5, 24.5],
                               margin=dict(l=20, r=20, t=100, b=20))                                
    scatter_line.for_each_yaxis(lambda y : y.update(tickmode="array",
                                tickvals=[7, 15, 17],))                                
    scatter_line.update_traces(textposition='middle left', texttemplate=None, 
                               line_color='#376274', opacity=0.8)

    annot_params = {'ax':-25, 'ay':-3, 'font_color':'red', 'arrowcolor':'red',
                    'yanchor':'top', 'xanchor':'right',}
    for i, el in enumerate(df_day_hours.columns, 1):
        ind_max = df_day_hours[el].idxmax(axis=0)
        val_max = df_day_hours[el].max()  
        if i == 1: 
            scatter_line.add_annotation(x=val_max, y=ind_max, text=f'{val_max:.1%}',
                            **annot_params, xref='x', yref='y') 
        else:    
            scatter_line.add_annotation(x=val_max, y=ind_max, text=f'{val_max:.1%}',
                            **annot_params, xref='x'+str(i), yref='y'+str(i))

    st.plotly_chart(scatter_line, theme=None)

#---------------Type--------------------------------------------
with chart_tabs[4]:
    df_humra_type = pd.crosstab(df['SUG_TEUNA'],
                                df['HUMRAT_TEUNA'],
                                margins='True', margins_name='all'
                                )[:-1].sort_values(by='all', ascending=True)
    df_humra_type['סה"כ'] = df_humra_type['all']/df_humra_type['all'].sum()
    df_norm = pd.crosstab(df['SUG_TEUNA'], df['HUMRAT_TEUNA'], normalize='columns')
    df_humra_type_merged = df_humra_type.join(df_norm, lsuffix="_cnt")[-7:]

    four_subplots_chart = four_subplots(df_humra_type_merged,     
                                        title="<b>Severity distribution for 7 major types of Road Accidents<b>",
                                        subtitles=['Total', 'Fatal', 'Slight', 'Serious', ]).update_layout(margin=dict(t=100, l=200, b=20))
    st.plotly_chart(four_subplots_chart, theme=None)

    df_teuna_road = crosstab_with_normindex_top_n(df, index='SUG_TEUNA', 
                                                  column='SUG_DEREH', top=7 )
     # replace  columns names     
    df_teuna_road.columns = [('<br>').join(el.split(' ', 1)) for el in df_teuna_road.columns.values]
    
    scatter_sub = scatter_subplots(df_teuna_road.T
                                   ).update_layout(margin=dict(l=80, t=80, r=20, b=20), plot_bgcolor='#e7eff2')
    st.plotly_chart(scatter_sub, theme=None)

    df_sig_yom_norm = crosstab_with_normindex_top_n(df, index='SUG_TEUNA',
                                                    column='YOM_BASHAVUA', top=7).T 
    loli_sub = lolipop_subplots(df_sig_yom_norm , sort_week[::-1]
                 ).update_traces(textposition='middle right',                  
                 ).update_layout(margin=dict(l=70, t=70, r=20, b=20), )

    st.plotly_chart(loli_sub, theme=None)

#---------------Speed and Road----------------------------------
with chart_tabs[5]:
    df_dereh = pd.crosstab(df['SUG_DEREH'],df['HUMRAT_TEUNA'], )
    pie_sub = pie_4_subplots(df_dereh.iloc[::-1]).update_layout(margin_t=50)
    st.plotly_chart(pie_sub, theme=None)  

    df_speed_dereh = 100*pd.crosstab(df['SUG_DEREH'],df['MEHIRUT_MUTERET'], normalize='all').T
    df_speed_dereh = df_speed_dereh.assign(urban = df_speed_dereh['עירונית בצומת'] + df_speed_dereh['עירונית לא בצומת'],
                      non_urban = df_speed_dereh['לא-עירונית בצומת'] + df_speed_dereh['לא-עירונית לא בצומת'],
                      at_intersection = df_speed_dereh.iloc[:, 0] + df_speed_dereh.iloc[:, 2],
                      not_at_intersection = df_speed_dereh.iloc[:, 1] + df_speed_dereh.iloc[:, 3])

    bar_scatter_1 = bar_scatter_bar_subplots(df_speed_dereh.iloc[:, 4:6].sort_values(by='urban'), 
                         sub_titles=['Urban Road','Speed Limit', 'Non Urban Road'])
    bar_scatter_2 = bar_scatter_bar_subplots(df_speed_dereh.iloc[:, -2:].sort_values(by='at_intersection'), 
                         sub_titles=['At intersection','Speed Limit', 'Not at intersection'])
    
    col_33, col_34 = st.columns(2)

    with col_33:
        st.plotly_chart(bar_scatter_1, theme=None)
    with col_34:
        st.plotly_chart(bar_scatter_2, theme=None)

    speed_to_sort = ['עד 50 קמ"ש', 'קמ"ש 60', 'קמ"ש 70', 'קמ"ש 80', 'קמ"ש 90',
                 'קמ"ש 100', 'קמ"ש 110', 'קמ"ש 120', 'לא ידוע']

    df_speed_humra = 100*pd.crosstab(df['MEHIRUT_MUTERET'],
                                     df['HUMRAT_TEUNA'],
                                     normalize='index')   
    
    marker_colors ={'קלה':'green', 'קשה':'#0B60B0', 'קטלנית':'red'}
    bar_area = bar_area_subplots(df_speed_humra, title='Speed Limit by Severity',
                                order_array=speed_to_sort, 
                                marker_colors ={'קלה':'green', 'קשה':'#0B60B0', 'קטלנית':'red'}).update_layout(margin_l=100, margin_r=50, margin_t=20, margin_b=20)
    st.plotly_chart(bar_area, theme=None, config={'displayModeBar': False})

#---------------------------------------------------------------
   
     



