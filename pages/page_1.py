import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
from get_data import *
from plotly_charts_functions import *
from streamlit_extras.add_vertical_space import add_vertical_space as avs

# Initialize the session state
if 'df' not in st.session_state:
    st.session_state.df = None

if 'data_excel' not in st.session_state:
    st.session_state.data_excel = None

# Your code to read CSV and Excel data
df = read_csv_data(url)
data_excel = read_excel_data(url_3)

# Store data in the session state
st.session_state.df = df
st.session_state.data_excel = data_excel

st.markdown("<h2 style='text-align: center; color: darkred;'>Road Accidents with Casualties in Israel 2022 </h2>", unsafe_allow_html=True) 
#st.header(":rainbow[_Road Accidents with Casualties in Israel 2022_]",  divider='rainbow')
avs(1)
#---------------------------------------------------------------
# Calculate metric
total = df['HUMRAT_TEUNA'].count()
total_2021 = 11554 
delta = total/total_2021 - 1 
monthly = total/12
weekly = total/52
daily = total/365
urban = 6849 
non_urban = 3555

metrics_col = st.columns(6)
# Display metrics
metrics_col[0].metric(label="Total for the Year", value=f'{total:,.0f}', delta=f'-1,150 ( {delta:,.0%})', delta_color="inverse")
metrics_col[1].metric(label="Monthly", value=f'{monthly:,.0f}', delta=f'{monthly-total_2021/12:,.0f}', delta_color="inverse")
metrics_col[2].metric(label="Weekly", value=f'{weekly:,.0f}', delta=f'{weekly-total_2021/52:,.0f}', delta_color="inverse")
metrics_col[3].metric(label="Daily", value=f'{daily:,.0f}', delta=f'{daily-total_2021/365:,.0f}', delta_color="inverse")
metrics_col[4].metric(label="Urban road", value=f'{urban:,.0f}', delta=f'{-1107:,.0f}', delta_color="inverse")
metrics_col[5].metric(label="Non-urban road", value=f'{non_urban:,.0f}', delta=f'{-143:,.0f}', delta_color="inverse")

style_metric_cards(border_left_color='darkred',
                   background_color='c0d2d4')

#---------------------------------------------------------------
col_1, col_12 = st.columns([1, 3])

with col_1:
    ht = df['HUMRAT_TEUNA'].value_counts(normalize=True).to_frame(name='% of total')
    pie = go_pie_chart(ht, colors_name=['green', '#0B60B0', 'red'],
             annot_text=f'<b>Severity <br>of <br>Road Accidents<b>')
    pie.update_layout(margin_t=0)
    st.plotly_chart(pie, theme=None) 
    
with col_12:  
    st.success('**Slight**: A road accident that injured at least one person, and in which no one was killed or seriously injured.')
    st.info('**Serious**: A road accident that seriously injured at least one person, and that killed no one.')
    st.error('**Fatal**: A road accident that killed at least one person or   injured at least one person and died within 21 days.')
avs(1)

col_13, col_14, col_15 = st.columns([1.4, 1, 1])
with col_15:
    df_nafa = 100*df['NAFA'].value_counts(normalize=True).to_frame('% from total')[:7]
    categories = df_nafa.index
    x_val = df_nafa['% from total']
    max_value = max(x_val)
    color_list = ['darkred' if el == max_value else "#c2d0d2" for el in x_val]

    lolipop_fig = lolipop_shart(x_val, categories, color_list, 'Subdistricts').update_layout(margin_t=20, margin_r=50)
    st.plotly_chart(lolipop_fig, theme=None)
   
with col_13:
    df_speed = (100*df['MEHIRUT_MUTERET']
            .value_counts(normalize=True)
            .to_frame(name='% from total'))       
    speed_bar = go_bar_plotly(df_speed).update_layout(margin_t=30)
    st.plotly_chart(speed_bar, theme=None)

with col_14:
    df_sug_humra = df['SUG_TEUNA'].value_counts(normalize=True).to_frame().reset_index()
    # Represent only large numbers
    df_sug_humra.loc[df_sug_humra['proportion'] < 0.2, 'SUG_TEUNA'] = 'אחר'  
    
    labels_pie = [('<br>'). join(el.split(' ', 1)) for el in df_sug_humra['SUG_TEUNA'].values]
    pie2 = pie_hole_pull(labels=labels_pie, values=df_sug_humra['proportion']
                         ).update_layout(margin_t=0)            
    st.plotly_chart(pie2, theme=None)




   