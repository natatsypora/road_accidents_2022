import streamlit as st
from get_data import *
from plotly_charts_functions import *
from streamlit_extras.add_vertical_space import add_vertical_space as avs


# Check if the session state has been initialized
if 'df' not in st.session_state:
    st.session_state.data = None

# Read CSV data and store it in the session state
df = read_csv_data(url)
st.session_state.df = df

# Define the columns to display
columns_list = [ "SUG_DEREH", "HODESH_TEUNA", "SHAA", "SUG_YOM",
                 "YOM_LAYLA", "YOM_BASHAVUA", "HUMRAT_TEUNA", "SUG_TEUNA",
                "HAD_MASLUL", "RAV_MASLUL", "MEHIRUT_MUTERET", "TKINUT",
                "TEURA", "MEZEG_AVIR", "MAHOZ", "NAFA"]

# Define the properties for styling the dataframe
properties = {'background-color': 'rgba(255, 255, 255, 0.5)', 
              "font-size": "14px",  "font-weight":"bold"}
avs(1)
#---------------------------------------------------------------    
with st.expander("__VIEW DATA__"):
    st.divider()
    st.markdown('''
         Data processing was performed in Google Colab using Pandas and several additional libraries.
                 <br>For more information go to my [Google Drive](https://drive.google.com/drive/folders/1Y-uVmHcquxutZfa72oruXeIiWHldw9Jj?usp=sharing).'''
                , unsafe_allow_html=True)
    avs(1)

    tab_df, tab_info, tab_top = st.tabs(["Data preview", "Info", "Top and Frequency"]) 
    with tab_df:
        # Display the dataframe
        st.dataframe(df[columns_list].sample(50).style.set_properties(**properties), hide_index=True) 

    with tab_info:
        info =show_info(df[columns_list]) 
        st.dataframe(info.style.format(subset=['count', 'missing'], thousands=',').set_properties(**properties), use_container_width=True)
            
    with tab_top:
        st.dataframe(df[columns_list].describe(include='object').T.iloc[:, 2:].style
                     .format(subset='freq', thousands=',')
                     .set_properties(**properties), use_container_width=True)  
    avs(1)
avs(1)
#---------------------------------------------------------------
# Define the function to style the dataframe
def style_dataframe(df: pd.DataFrame, format="{:.1f}") -> pd.DataFrame: 
    return df.style\
        .format(format)\
        .highlight_max(props='color:rgba(255, 0, 0, 0.9);')\
        .highlight_min(props='color:rgba(0, 180, 0, 0.9);')\
        .set_properties(**properties)                      

#----------------------------------------------------------------
# Define the function to update the crosstab table
def update_crosstab_norm():    
    df_cnt_norm = 100*df[index_norm].value_counts(normalize=True).to_frame('% of total')
    df_norm_index = 100*pd.crosstab(df[index_norm],
                                    df['HUMRAT_TEUNA'], normalize='index')
    df_norm_colunm = 100*pd.crosstab(df[index_norm], 
                                     df['HUMRAT_TEUNA'], normalize='columns')
    st.session_state.df_cnt_norm = df_cnt_norm
    st.session_state.df_norm_index = df_norm_index
    st.session_state.df_norm_colunm = df_norm_colunm

    if index_norm == 'YOM_BASHAVUA':
        return df_cnt_norm.reindex(sort_week), df_norm_index.reindex(sort_week), df_norm_colunm.reindex(sort_week)
    elif index_norm == 'HODESH_TEUNA':
        return df_cnt_norm.reindex(sort_month), df_norm_index.reindex(sort_month), df_norm_colunm.reindex(sort_month)
    else:    
        return df_cnt_norm.sort_index(), df_norm_index, df_norm_colunm
    
#----------------------------------------------------------------
# Create the selectbox
index_norm = st.selectbox(
    'Select index for crosstab with normalize (%)',
    (columns_list), index=0, key='index_norm', on_change=update_crosstab_norm)

# Get the crosstab table
table_cnt_norm, crocctab_norm_index, crocctab_norm_col = update_crosstab_norm()

# Display the crosstab table
col_21, col_22, col_23 = st.columns([0.5, 1, 1])

with col_21:
    st.markdown("""<p style="text-align: center;">value counts</p>""", 
                unsafe_allow_html=True)  
    st.dataframe(style_dataframe(table_cnt_norm),
                  height=len(table_cnt_norm)*35+40, use_container_width=True)

with col_22:
    st.markdown("""<p style="text-align: center;">normalize = index</p>""", 
                unsafe_allow_html=True)  
    st.dataframe(style_dataframe(crocctab_norm_index),
                  height=len(crocctab_norm_index)*35+40, use_container_width=True)

with col_23:
    st.markdown("""<p style="text-align: center;">normalize = column</p>""", 
                unsafe_allow_html=True)
    st.dataframe(style_dataframe(crocctab_norm_col), 
                 height=len(crocctab_norm_col)*35+40, use_container_width=True)

avs(1)

#---------------------------------------------------------------
# Define the function to update the crosstab table
def update_crosstab():
    df_filtered = pd.crosstab(df[index], df[column])                             
    st.session_state.df = df_filtered
    if index == 'YOM_BASHAVUA':
        return df_filtered.reindex(sort_week)
    elif index == 'HODESH_TEUNA':
        return df_filtered.reindex(sort_month) 
    else:
        return df_filtered
    
#---------------------------------------------------------------  
# Create a selectbox for the index and column
col_index, col_column = st.columns(2)
with col_index:
    index = st.selectbox(
    'Select index for crosstab',
    (columns_list), index=0, key='index', on_change=update_crosstab)
        
with col_column:
    column = st.selectbox(
    'Select column for crosstab', 
    (columns_list), index=4, key='column', on_change=update_crosstab) 

# Display the data
crocctab_table = update_crosstab()
st.dataframe(style_dataframe(crocctab_table, format="{:,.0f}"), 
             height=len(crocctab_table)*35+40 , use_container_width=True)   

#---------------------------------------------------------------
  
 




