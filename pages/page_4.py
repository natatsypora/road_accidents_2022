import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster, Fullscreen, GroupedLayerControl
from get_data import *
from branca.colormap import linear
from plotly_charts_functions import scatter_line_subplots
import time


LOCATION = (31.5, 34.85)

df = read_csv_data(url)
df.dropna(subset='Latitude', inplace=True)

if 'df' not in st.session_state:    
    st.session_state.df = df

data_for_geojson = load_json_data(url_2)

if 'data_for_geojson' not in st.session_state:    
    st.session_state.data_for_geojson = data_for_geojson

#------------------------------------------------------------------------------ 
nafot_to_replace = {'תל אביב':'Tel Aviv', 'גולן':'Golan', 'באר שבע':'Beersheba',
                    'אשקלון':'Ashkelon', 'השרון':'haSharon', 'חדרה':'Hadera',
                    'רמלה':'Ramla', 'פתח תקווה':'Petah Tikva', 'רחובות':'Rehovot',
                    'יזרעאל':'Jezreel', 'ירושלים':'Jerusalem', 'חיפה':'Haifa',
                    'כנרת':'Kinneret', 'חברון':'Judea and Samaria', 'צפת':'Safed', 'עכו':'Acre',}

df_gj = df[['Latitude', 'Longitude', 'HUMRAT_TEUNA', 'SUG_TEUNA', 'NAFA', 'MAHOZ', 'MEHIRUT_MUTERET']].copy()

df_gj['subdistrict'] = df_gj['NAFA'].map(nafot_to_replace)
df_nafot = df_gj.groupby('subdistrict', as_index=False).size()
dict_nafot = df_nafot.set_index('subdistrict')['size']

# add data to geojson dict
for el in data_for_geojson['features']:
   total = df_nafot[df_nafot['subdistrict']==el['properties']['subdistrict']]['size'].iloc[0].astype(float) #convert to float!!!
   el['properties'].update({'total accidents': total})

colormap = linear.YlOrRd_04 .scale(df_nafot['size'].min(),  df_nafot['size'].max())
colormap.caption = 'Road Accidents in Israel Sabdistricts 2022'
if 'colormap' not in st.session_state:    
    st.session_state.colormap = colormap

#==========Create folium Maps with markers and layers==========================
def folium_map_with_marker_cluster_and_layers(data, location, zoom=7.5, name=None):
    """
    Creates a folium map with marker cluster and layers based on the given data.
    Args:
        data (pandas.DataFrame): The data containing the necessary columns.
        location (tuple): The latitude and longitude of the map center.
        zoom (float, optional): The initial zoom level of the map. Defaults to 7.5.
        name (str, optional): The name of the map. Defaults to None.
    Returns:
        folium.Map: The created folium map object.
    """
    if data is None or data.empty:
        raise ValueError("Invalid or missing data provided for the map creation.")

    # Create folium map -------------------------------------------------------
    map_obj = folium.Map(location=location, zoom_start=zoom, max_zoom=16,
                         tiles='Cartodb Positron', name=name)
    Fullscreen(
        position="topleft",
        title="Full Screen",
        title_cancel="Exit",
        force_separate_button=True).add_to(map_obj)  

    fg = folium.FeatureGroup(name="Marker Clusters").add_to(map_obj)  
               
    # Create GeoJson ----------------------------------------------------------
    folium.GeoJson(
        data_for_geojson,
        zoom_on_click=True,
        name="Subdistrict boundaries",
        style_function=lambda feature: {
            "fillColor": colormap(dict_nafot[feature["properties"]['subdistrict']]),
            "color": "grey",
            "weight": 1,
            "dashArray": "5, 5", 
            "fillOpacity": 0.8 },
        tooltip=folium.GeoJsonTooltip(
            fields=['subdistrict', 'district', 'total accidents'],
            aliases=["Subdistrict", "District", 'Total'],
            localize=True ,
            style="""background-color: #F0EFEF;
                     border: 2px solid black;
                     border-radius: 10px;
                     box-shadow: 3px;
                     font-size: 14px; """,
            max_width=800),
        smooth_factor=2 ).add_to(map_obj)
    
    colormap.add_to(map_obj)

    # Create marker clusters ----------------------------------------------------------                                      
    mc_red_other = MarkerCluster(maxClusterRadius=100, name='red_other').add_to(fg)
    mc_green_other = MarkerCluster(maxClusterRadius=100, name='green_other').add_to(fg)
    mc_blue_other = MarkerCluster(maxClusterRadius=100, name='blue_other').add_to(fg)
    mc_red_pidestrian = MarkerCluster(maxClusterRadius=100, name='red_pidestrian').add_to(fg)
    mc_green_pidestrian = MarkerCluster(maxClusterRadius=100, name='green_pidestrian').add_to(fg)
    mc_blue_pidestrian = MarkerCluster(maxClusterRadius=100, name='blue_pidestrian').add_to(fg)

    color_dict = {'קטלנית': 'red', 'קלה': 'green', 'קשה': 'blue'}
    icons_dict = {'פגיעה בהולך רגל': 'person-falling-burst', 'other': 'car-burst'}

    for _, row in data.iterrows():
            color = color_dict.get(row['HUMRAT_TEUNA'], 'grey')
            icons = icons_dict.get(row['SUG_TEUNA'], 'car-burst')
            location = [row['Latitude'], row['Longitude']]
            tooltip=folium.Tooltip(
                f"Subdistrict: {row['NAFA']} <br>Severity: {row['HUMRAT_TEUNA']}\
                <br>Type of Accident: {row['SUG_TEUNA']} <br>Speed Limit: {row['MEHIRUT_MUTERET']}",
                style="font-size: 12px; border-radius: 10px;")
            icon = folium.Icon(color=color, icon=icons, prefix='fa')
            marker = folium.Marker(location=location, tooltip=tooltip, icon=icon)

            if row['HUMRAT_TEUNA'] == 'קטלנית' and row['SUG_TEUNA'] == 'פגיעה בהולך רגל':
                marker.add_to(mc_red_pidestrian)
            elif row['HUMRAT_TEUNA'] == 'קלה' and row['SUG_TEUNA'] == 'פגיעה בהולך רגל':
                marker.add_to(mc_green_pidestrian)
            elif row['HUMRAT_TEUNA'] == 'קשה' and row['SUG_TEUNA'] == 'פגיעה בהולך רגל':
                marker.add_to(mc_blue_pidestrian)
            elif row['HUMRAT_TEUNA'] == 'קטלנית' and row['SUG_TEUNA'] != 'פגיעה בהולך רגל':
                marker.add_to(mc_red_other)
            elif row['HUMRAT_TEUNA'] == 'קלה' and row['SUG_TEUNA'] != 'פגיעה בהולך רגל':
                marker.add_to(mc_green_other)
            elif row['HUMRAT_TEUNA'] == 'קשה' and row['SUG_TEUNA'] != 'פגיעה בהולך רגל':
                marker.add_to(mc_blue_other) 
            
    # Add layer control ----------------------------------------------------------
    folium.LayerControl(collapsed=True, position='topleft').add_to(map_obj)
    GroupedLayerControl(
    groups={'פגיעה בהולך רגל': [mc_red_pidestrian, mc_green_pidestrian, mc_blue_pidestrian],
            'אחר': [mc_red_other, mc_green_other, mc_blue_other]},
            exclusive_groups=False, collapsed=True, position='topleft').add_to(map_obj)
    
    return map_obj

#========Display Map==========================================================
map1, map2 = st.columns([1.5, 1])

with map1:
    with st.spinner('Please wait until the map loads completely...'):
        time.sleep(5)
        map = folium_map_with_marker_cluster_and_layers(df_gj, LOCATION, name="Subdistricts of Israel")
        with st.container(height=700):
            folium_static(map, width=625, height=660)          

    with st.expander("Districts and Subdistricts of Israel"):
            st.write('''* **Central** (subdistricts: HaSharon, Petah Tikva, Ramla, Rehovot)\
                    \n* **Haifa** ( subdistricts: Haifa, Hadera)\
                    \n* **Jerusalem**\
                    \n* **North** (subdistricts: Acre,Golan, Jezreel, Kinneret, Safed)\
                    \n* **South** (subdistricts: Ashkelon, Beersheba)\
                    \n* **Tel Aviv**\
                    \n* **Judea and Samaria**(Unofficial district)''') 
            st.link_button("Go to Wikipedia", "https://en.wikipedia.org/wiki/Districts_of_Israel")

with map2:
    df_nafa_humra = pd.crosstab(df['NAFA'] , df['HUMRAT_TEUNA'], margins=True
                                ).sort_values(by='All', ascending=False).iloc[1:, :-1]
    df_nafa_humra = df_nafa_humra.div(df_nafa_humra.sum(axis=1), axis=0)

    scatter_loli_chart = scatter_line_subplots(df_nafa_humra[::-1]).update_layout(
        title='Severity of Road Accidents in each Subdistrict', plot_bgcolor='#e7eff2',
        height=700, width=430, margin_t=80, margin_l=80).update_traces(mode='markers+text'
        ).for_each_xaxis(lambda x : x.update(range=[min(x), max(x)]))
    # update subtitle positions
    for annotation in scatter_loli_chart['layout']['annotations']:
            annotation['xanchor']='center'
            annotation['y']=1.03  
    
    config = {'displayModeBar': False}
    st.plotly_chart(scatter_loli_chart, theme=None, config=config)

    with st.expander("View table"):
        table_sub_severity = pd.crosstab(df['NAFA'] , df['HUMRAT_TEUNA'], 
                                 margins=True, margins_name='סה"כ',
                                ).sort_values(by='סה"כ', ascending=False
                                ).iloc[1:, :]
        table_sub_severity.index.name = None
        table_sub_severity.columns.name = None
        st.dataframe(table_sub_severity, width=390, height=600)
       