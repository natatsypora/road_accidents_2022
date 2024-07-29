import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
 
# define templates
pio.templates["my_rules"] = go.layout.Template(
    layout=go.Layout(
        colorway=['#FF0000', '#88b37c', '#4085bb', '#808080',
                  '#d67b3d', '#c6b756', 'rgb(166,118,29)', 'rgb(102,102,102)'])
                    )

pio.templates.default = 'simple_white+my_rules'

# define parameters for charts
charts_params = {'font_size':14,
                 'plot_bgcolor':'rgba(0, 0, 0, 0)',
                 'paper_bgcolor':'rgba(255, 255, 255, 0.5)',
                 'margin':{'l':10, 'r':10, 't':70, 'b':10}
                }

def hex_to_rgba(h, alpha):
     #converts color value in hex format to rgba format with alpha transparency    
    return tuple([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [alpha])

#========== Heatmap and bar subplots=============================
@st.cache_data
def heatmap_bar_subplots(df, colorscale='OrRd', title=None,
                         max_color_name = 'rgb(127,0,0)',
                         other_color_name= 'rgb(254,232,200)',
                         sort_array=None):

    max_row = max(df.sum(axis=0))
    max_column = max(df.sum(axis=1))
    color_index = [max_color_name  if el == max_row else other_color_name for el in df.sum(axis=0)]
    color_columns = [max_color_name  if el == max_column else other_color_name for el in df.sum(axis=1)]

    # make subplots
    fig = make_subplots(rows=2, cols=2,
                        column_widths=[0.9, 0.1],
                        row_heights=[0.2, 0.8],
                        shared_yaxes=True,
                        horizontal_spacing=0,
                        vertical_spacing=0 )

    # first plot
    heatmap = px.imshow(df)

    # second plot
    bar_index = px.bar(df.sum(axis=0), text_auto='.0f')

    # third plot
    bar_columns = px.bar(df.sum(axis=1), orientation='h', text_auto='.0f')
    bar_columns.update_yaxes(categoryorder='array', categoryarray=sort_array)

    # add plots to subplots
    fig.add_trace(heatmap.data[0], row=2, col=1)
    fig.add_trace(bar_index.data[0], row=1, col=1)
    fig.add_trace(bar_columns.data[0], row=2, col=2)

    # add grid line to imshow plot
    for i in range(len(df.columns)):
        fig.add_shape(type="line", x0=1.5 + i, y0=-0.5, x1=1.5 + i,
                      y1=len(df.index) - 0.5,
                      line=dict(color="white", width=2), row=2, col=1)
    for i in range(len(df.index)):
        fig.add_shape(type="line", x0=-0.5, y0=0.5 + i,
                      x1=len(df.columns) - 0.5, y1=0.5 + i,
                      line=dict(color="white", width=2), row=2, col=1)

    # update the properties for figure and plots
    fig.update_layout(height=500, width=1200, **charts_params,
                      title_text=title, title_x=0.5,                      
                      coloraxis_showscale=False, showlegend=False)
    fig.update_xaxes(tickmode='linear', range=[0.5, 31.5], row=2, col=1)
    fig.update_yaxes(showticklabels=False, ticks="", range=[200, 450],
                     visible=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, ticks="", row=2, col=2)
    fig.update_xaxes(showticklabels=False, ticks="", range=[400, 1200],
                     visible=False, row=2, col=2)
    fig.update_coloraxes(colorscale=colorscale)
    # update traces for plots
    fig.update_traces(
        hovertemplate = "<b>Day: %{x}</b><br>" + "<b>Total: %{y}</b><br>",
        marker_color=color_index, name='',
        textposition='outside', row=1, col=1)
    fig.update_traces(
        hovertemplate = "<b>Month: %{y}</b><br>" + "<b>Total: %{x}</b><br>",
        marker_color=color_columns, name='',
        textposition='outside', row=2, col=2)
    fig.update_traces(hovertemplate = "<b>Month: %{y}</b><br>"+
                                      "<b>Day: %{x}</b><br>" +
                                      "<b>Total: %{z}<b>",
                       name='', row=2, col=1)
    return fig

#========== Line_plot_with_minmax================================
@st.cache_data
def line_plot_with_minmax(df, title=None,  colors=['red', 'green']):
  max_shaa, min_shaa = max(df['% from total']), min(df['% from total'])
  minmax_color = [colors[0] if el == max_shaa else (colors[1] if el == min_shaa
                                                else 'white') for el in df['% from total']]

  fig = px.area(df, markers=True)

  fig.update_traces(
      marker=dict(size=7, symbol="circle",
                  color=minmax_color, line_width=1),
      line=dict(width=1, color='rgba(0, 70, 100, 0.7)'),
                fillcolor = 'rgba(0, 70, 100, 0.1)',
      hovertemplate = "<b>Value: %{y:.1f}% </b><br>" + "<b>Hour: %{x}</b><br>",
      name="")
  # add annotation with min and max values
  for ind, v_tx in zip(df.idxmax().values, df.max().values):
      fig.add_annotation(x=ind, y=v_tx,
                        text=f'Max Value={v_tx:.1f}%<br>Hour={ind}',
                        font_color='red', arrowhead=1, )
  for ind, v_tx in zip(df.idxmin().values, df.min().values):
      fig.add_annotation(x=ind, y=v_tx,
                        text=f'Min Value={v_tx:.1f}%<br>Hour={ind}',
                        font_color='green', arrowhead=1,)
  fig.update_layout(
      title=title, title_x=0.2, showlegend=False, **charts_params,
      width=800, height=340, yaxis_title='% ', xaxis_title='hours',
      xaxis_tickmode='linear', xaxis_range=[0.8, 24.2],)
  return fig

#========== Line_subplots========================================
@st.cache_data
def line_subplots(df, title):
    fig = px.line(df, markers=True)

    fig.update_layout(title=title,  title_x=0.2, **charts_params,                     
                      yaxis_title='%', xaxis_title='hours',
                      hovermode='x unified', xaxis_tickmode='linear',
                      height=340, width=800, xaxis_range=[0.8, 24.2],
                      legend=dict(orientation="h", title="",
                                  yanchor="top", y=1.15,
                                  xanchor="right", x=1))

    fig.update_traces(marker=dict(symbol='circle', size=7, color='white',
                                  line=dict(width=1,)), line_width=1,
                      hovertemplate = "<b>Severity</b><br>" +
                                      "<b>Value: %{y:.1f}% </b><br>")
    return fig

#========== Bar_relative=========================================
@st.cache_data
def bar_relative(df, title=None):
  fig = go.Figure()
  for col, w in zip(df.columns, [0.3, 0.5, 0.3]):
    # add plots to fugire
    fig.add_bar(opacity=0.9,
                x=df.index,
                y=df[col],
                width=w,
                name=col,
                hovertemplate='%{y:.1f}')

  # update the propeties for figure
  fig.update_layout(title=title, title_x=0.2,                     
                    width=800, height=345, **charts_params,
                    xaxis_tickmode='linear', hovermode='x unified',
                    barmode='relative', yaxis_title='%', xaxis_title='hours',
                    legend=dict(orientation="h",
                                 yanchor="bottom", y=10.5,
                                 xanchor="right", x=1 ))
  return fig

#==========Go_pie_chart==========================================
@st.cache_data
def go_pie_chart(df, colors_name=None, annot_text=None):
    fig = go.Figure(
       go.Pie(
            hole=0.7, name='',  
            marker_colors=colors_name,            
            values = df[df.columns[0]],
            labels = df.index,
            text = df.index, textposition='outside',
            texttemplate='%{label}<br>%{percent:.0%}',
            hovertemplate = "Severity: %{label} <br> %{percent} of total")
    )
    fig.update_traces(textfont_color=fig.data[0].marker.colors)
    fig.add_annotation(x=0.5, y=0.5, text=annot_text, 
                       showarrow=False, font_size=14)
    fig.update_layout(width=250, height=200, showlegend=False, **charts_params)
    return fig

#==========YOY_subplots==========================================
@st.cache_data
def yoy_subplots(df, title=None, subtitles=None, sort_month=None):
    y = df.index
    args_bar = {'orientation':'h', 'width':0.6,}
    # make subplots
    fig = make_subplots(rows=1, cols=4, 
                        subplot_titles=subtitles,
                        shared_yaxes=True,
                        column_widths=[0.8, 0.7, 0.5, 0.5],
                        horizontal_spacing=0.02,
                        )
    # add charts to subplots
    for i, col in enumerate(zip(df.columns[:4],
                                df.columns[4:]), start=1):
        x = df[col[0]] - df[col[1]]
        max_color = ['#376274' if bar <=0 else 'red' for bar in x ]
        fig.add_trace(
            go.Bar(x=x, y=y, opacity=0.9,
                   text=x, textposition='outside',
                   textfont_color=max_color, marker_cornerradius=10,
                   hovertemplate='%{y} 2022 <br>Changes vs PY = %{x:.0f}',
                   name=col[0].split('_')[0],
                   marker_color=max_color,  **args_bar),
            row=1, col=i)
        fig.update_yaxes(visible=False,)
        fig.update_xaxes(range=[min(x)-35, max(x)+20], row=1, col=i)
    # update layout for whole figure
    fig.update_layout(title=title, title_x=0.5, **charts_params,
                      hovermode="y unified",
                      height=500, width=1000, showlegend=False)
    # update subtitle positions
    for annotation in fig['layout']['annotations']:
            annotation['yanchor']='middle'
            annotation['xanchor']='center'
            annotation['y']=1.1

    fig.update_yaxes(categoryorder='array', categoryarray=sort_month)
    fig.update_xaxes(zeroline=True )
    fig.update_yaxes(visible=True, row=1, col=1)
    return fig

#==========Heatmap_separate_by_columns2==========================
@st.cache_data
def heatmap_separate_by_columns2(df, title=None, text_auto=False):
    fig_hm = make_subplots(
        rows=3, cols=2, 
        column_widths=[0.9, 0.1],
        vertical_spacing=0.05,
        horizontal_spacing=0,
        specs=[[{}, {"rowspan": 3}],
              [{}, None],[{}, None]]
        )
    data_for_bar = df.sum(axis=1).to_frame(name='total'
                   ).sort_values(by='total', ascending=False).reset_index()
    bar = px.bar(data_for_bar, y='index', x='total', orientation='h', text_auto=',.0f')
    bar.update_traces(marker_color=[ 'green', '#0B60B0', 'red'], 
                      textposition='outside')                      
    fig_hm.add_trace(bar.data[0], row=1, col=2) 
    
    # Create the heatmaps and add them to the subplots
    for i, (x, y) in enumerate(zip(['x', 'x3', 'x4'], ['y', 'y3', 'y4'])):
        hm = px.imshow(df.iloc[[i]], text_auto=text_auto)
        fig_hm.add_trace(hm.data[0], row=i+1, col=1)           
        # add vertical lines
        for j in range(len(df.columns)+1):
            fig_hm.add_shape(
                type="line",
                y0=-0.5, x0=0.5 + j,
                y1=1 - 0.5, x1=0.5 + j,
                line=dict(color="grey", width=2), xref=x, yref=y)
        # add horizontal lines
        for n in range(0, 2):
          fig_hm.add_shape(
                type="line",
                x0=0.5, y0=-0.5 + n,
                x1=len(df.columns) + 0.5, y1=-0.5 + n,
                line=dict(color="black", width=1), xref=x, yref=y)   
    
    # # Update coloraxis and hovertemplate for each subplot
    for n in range(1, 4):
        fig_hm.data[n].update(coloraxis=f'coloraxis{n+1}')
    fig_hm.update_traces(
        hovertemplate='Day: %{x}<br>Severity: %{y}<br>Total: %{z}<extra></extra>')
    fig_hm.data[0].hovertemplate = 'Total: %{x:,.0f}<br>Severity: %{y}<extra></extra>'

    # Update the layout settings
    fig_hm.update_layout(**charts_params,
        hovermode="x unified", title=title, title_x=0.5,
        coloraxis2=dict(colorscale='reds', showscale=False),                   
        coloraxis3=dict(colorscale='blues', showscale=False),
        coloraxis4=dict(colorscale='greens', showscale=False),        
        xaxis_visible=False, xaxis3_visible=False, xaxis4_visible=False, xaxis2_visible=False,
        yaxis2_visible=False, width=1200, height=180,
        xaxis2_range=[0, data_for_bar['total'].max()+10_000], 
        # set the color of the y-axis text labels       
        yaxis=dict(tickfont_color='red'),  
        **{f"yaxis{n}": {"tickfont_color": color}
          for n, color in enumerate(['#0B60B0', 'green'], start=3)}
    )
    return fig_hm

#==========Pie_hole_pull=========================================
@st.cache_data
def pie_hole_pull(labels, values ):      
    colors = ["darkred",   "black", "#c2d0d2"]
    fig = go.Figure(data=[go.Pie(labels=labels, texttemplate='%{label} <br>%{value:,.0%}',
                                 values=values, name='', 
                                 pull=[0, 0.2, 0 ], hole=0.7,
                                 marker=dict(colors=colors,
                                             line=dict(color='#000000', width=1),
                                             pattern=dict(shape=["",  "-", ""]))
                                )])                                
    fig.update_traces(hoverinfo="label+percent",
                      textposition='outside',
                      textfont_color=colors)
    fig.update_layout(**charts_params,
                      xaxis_autorange='reversed', xaxis_zeroline=True,                       
                      width=450, height=300, showlegend=False)
    fig.add_annotation(text='<b>Type<br> of <br>Road Accident<b>',
                       x=0.5, y=0.5, font_size=14, showarrow=False)
    return fig

#=================Go_bar_plotly=================================
@st.cache_data
def go_bar_plotly(df):
    x_bar = df.iloc[:,0]
    max_color_bar = ['darkred' if x == max(x_bar) else "#c2d0d2" for x in x_bar]
    fig =go.Figure(go.Bar(y=df.index, x=x_bar, orientation='h', marker_cornerradius=10,
                          marker_color=max_color_bar, hoverinfo='skip',
                          text=x_bar, texttemplate='%{text:.01f}%',
                          textposition='outside',))
    #fig.update_traces(textfont_color=fig.data[0].marker.color,)
    
    fig.update_layout(showlegend=False, **charts_params,
                      title='Road Accidents<br>by Speed Limit',
                      title_x=0.85, title_y=0.3,
                      yaxis={'categoryorder':'total ascending'}, yaxis_title='',
                      xaxis_range=[0, 65], width=450, height=300,)
    fig.add_annotation(x=45, y=7,
                       text='More than half of all road accidents<br> were within speed limits of 50 km/h',
                       font_color='darkred', arrowhead=1, arrowwidth=2, arrowcolor='darkred', ax=-10, ay=50 )
    return fig

#=================Pie_3_subplots=================================
#@st.cache_data
def lolipop_shart(x_val, y_val, color_list, title):
    # create figure
    fig = go.Figure()
    # add lines(bar)
    for x, y, c in zip(x_val, y_val, color_list):
        fig.add_trace(go.Scatter(x=[0, x], y=[y, y],
                                 mode='lines', hoverinfo='skip',
                                 showlegend=False, stackgaps='interpolate',
                                 line=dict(color=c, width=5)))
    # add markers
    fig.add_trace(go.Scatter(x=x_val,
                             y=y_val, textposition='middle right',
                             mode='markers+text', text=x_val, texttemplate='%{text:.1f}%',
                             textfont_size = 14, hoverinfo='skip',
                             marker=dict(color='white', size=20, line_width=4, line_color=color_list )))
    # set layout
    fig.update_layout(**charts_params,
                      xaxis_range=[0, 35], xaxis_visible=False, 
                      yaxis={'categoryorder':'total ascending'},
                      width=320, height=300, showlegend=False, 
                      title=title, title_x=0.95, title_y=0.1,)
    # add annotation
    fig.add_annotation(x=28, y=5, font_size=14, 
                       text='1/4 of all <br>road accidents<br>occur in Tel Aviv <br>Subdistrict',
                       font_color='darkred', arrowhead=1, #bgcolor='lightgrey', 
                       arrowwidth=2, arrowcolor='darkred', ax=25, ay=60 )
    return fig

#=================Pie_4_subplots=================================
@st.cache_data
def pie_4_subplots(df):
    specs = [[{'type':'domain'}]*4]
    labels = df.columns.values
    names = df.index.values
    fig = make_subplots(rows=1, cols=4,
                        specs=specs, subplot_titles=names,
                        horizontal_spacing=0.05,
                        vertical_spacing=0.1)
     # define pie charts
    for i in range(4):
        fig.add_trace(go.Pie(labels=labels, hole=0.6, opacity=0.8,
                             marker_colors=['red', 'green', '#0B60B0'],
                             values=df.iloc[i, :].values,
                             name=names[i]),
                       row=1, col=i+1)  
            
    # update subtitle positions
    for annotation in fig['layout']['annotations']:
        annotation['yanchor']='middle'
        annotation['xanchor']='center'
        annotation['y']=1.2
    # update layout and hover info
    fig.update_traces(hoverinfo='label+percent', texttemplate='%{percent:.0%}')
    fig.update_layout(**charts_params,
                      showlegend=False, height=200,  width=1140)

    fig = go.Figure(fig)
    return fig

#=================Bar_scatter_bar_subplots=======================
@st.cache_data
def bar_scatter_bar_subplots(df, sub_titles=None, 
                             colors_name=['#376274', '#C2D4D2']):
    fig = make_subplots(rows=1, cols=3, #shared_yaxes=True,
                          subplot_titles=sub_titles,
                          horizontal_spacing=0.01, 
                           column_widths=[1, 0.5, 1])
    val_y = df.index
    for i , name, color in zip([1, 3], df.columns.values, colors_name):
        fig.add_trace(go.Bar(x=df[name],
                             y=val_y, name=name,
                             width=0.7, hoverinfo='skip',
                             orientation='h', marker_cornerradius=10,
                             marker_color = color, 
                             marker_line_color='gray',
                             texttemplate='%{x:,.1f}%'),
                      row = 1, col = i)
        fig.add_vline(x=0, line_width=2, row = 1, col = i)

    fig.add_scatter(x=[1,] * len(val_y),
                    y=val_y,
                    text=val_y , mode='text',
                    textposition='middle center',
                    hoverinfo='skip',
                    row = 1, col = 2)

    # update subtitle positions
    for annotation in fig['layout']['annotations']:
            annotation['yanchor']='middle'
            annotation['xanchor']='center'
            annotation['y']=1.1

    fig.for_each_xaxis(lambda x: x.update(visible=False))
    fig.for_each_yaxis(lambda y: y.update(visible=False))

    fig.update_layout(**charts_params, showlegend=False,
                      width=550, height=400, xaxis3_range=[0, df.max()[0]],                      
                      xaxis_autorange='reversed')
    return fig

#=================Bar_text_relative_mode=========================
@st.cache_data
def bar_text_relative_mode(df, sort_week=None, title=None):
  col_names = df.columns.values
  fig = go.Figure()
  for col, w in zip(col_names, [0.8, 0.5, 0.8]):
    # add plots to fugire
    fig.add_bar(opacity=0.9, 
                x=df.index,
                y=df[col],  marker_cornerradius=10,
                width=w, texttemplate='%{y:.0f}', customdata=[col,]*7,
                hovertemplate='Severity: %{customdata} <br>Day of the Week :%{x}\
                               <br> %{y:.1f}% of total',
                name='')
  # add text to red bar --> mode="text"        
  fig.add_trace(
    go.Scatter(x=df.index, textfont_color='red', hoverinfo='skip',
               y=df[col_names[0]], mode='text', name='',
               texttemplate='%{y:.1f}', textposition='top center',
              ))
  fig.data[0].texttemplate=None
  fig.data[1].textfont.color='black'
  # update the propeties for figure
  fig.update_layout(title=title, title_x=0.1, 
                    **charts_params,
                    width=450, height=350, 
                    showlegend=False, barmode='relative' ) 
  fig.update_xaxes(categoryorder='array',
                   categoryarray=sort_week)                   
  return fig

#=================Area_plot_with_minmax==========================
@st.cache_data
def area_plot_with_minmax(df, sort_array, title=None, 
                          colors=['red', 'green', 'rgba(0, 70, 100, 0.5)']):
    max_val, min_val= max(df['cnt']), min(df['cnt'])
    minmax_color = [colors[0] if el == max_val else (colors[1] if el == min_val
                                                else colors[2]) for el in df['cnt']]
    fig = go.Figure(go.Scatter(x=df.index, y=df['perc'], 
                               mode='lines+markers+text',
                               textposition='middle right', text=df['cnt'], 
                               fill='tozeroy', texttemplate='%{y:.0f}% <BR><br>%{text:,.0f}',
                               fillcolor = 'rgba(0, 70, 100, 0.1)',
                               ))
    fig.update_traces(textfont_color=minmax_color,
                      marker=dict(size=10, symbol="circle", 
                                  color=minmax_color, line_width=1),
                      line=dict(width=1, color=colors[2]),  
                      hovertemplate = "<b>Day of the Week: %{x}</b><br>" + "<b>%{y:.1f}% of total </b><br>" ,
                      name="")
    fig.update_xaxes(tickmode = 'array',
                     tickvals = [0, 1, 2, 3, 4, 5, 6],
                     ticktext = sort_array)
    fig.update_layout(title=title, title_x=0.1, showlegend=False, 
                      xaxis_range=[-0.1, 6.5], yaxis_range=[5, 18],
                      **charts_params, yaxis_title='', xaxis_title=None,
                      width=800, height=350)
    return fig

#=================Four_subplots==================================
@st.cache_data
def four_subplots(df, title=None, subtitles=None, 
                  marker_colours= ['#376274', 'red', 'green', '#0B60B0']):
    args_bar = {'orientation':'h', 'width':0.6, 'marker_cornerradius':10, 'opacity':0.8}
    # make subplots
    fig = make_subplots(rows=1, cols=4,
                        subplot_titles=subtitles,
                        shared_yaxes=True,
                        horizontal_spacing=0.01)
    
    # add charts to subplots
    for i, col in enumerate(df.columns[4:]):  
        fig.add_trace(
            go.Bar(x=df[col], y=df.index, 
                   text=df[col], textposition='outside',
                   hovertemplate='%{y}<br> %{x:.1%}', 
                   texttemplate='%{x:.0%}',
                   name=col, marker_color=marker_colours[i],
                   **args_bar),
            row=1, col=i+1)
        #add vertical line instead of yaxis
        fig.add_vline(x=0, line_width=2, line_color='black', row=1, col=i+1)
        fig.update_yaxes(visible=False)
       
    fig.update_xaxes(range=[0, 0.55], visible=False )
    # update layout for whole figure
    fig.update_layout(title=title, title_x=0.5, 
                      #hovermode="y unified",
                      height=350, width=1100,
                      showlegend=False, **charts_params,)
    # update subtitle positions
    for annotation in fig['layout']['annotations']:
            annotation['xanchor']='right'
            annotation['y']=1.07            
    # return yaxis labels for first subplot
    fig.update_yaxes(visible=True, title=None, row=1, col=1)

    return fig

#=================Scatter_subplots===============================
@st.cache_data 
def scatter_subplots(df):
    col_names, categories = df.columns.values, df.index.values

    fig = make_subplots(rows=1, cols=len(col_names),
                         subplot_titles=col_names,
                         shared_yaxes=True,
                         horizontal_spacing=0.02)

    # add charts to subplots
    for i, col in enumerate(col_names):
            x_val =  df[col]
            colors = ['red' if x == max(x_val) else '#376274' for x in x_val]
            marker_size = [20 if x == max(x_val) else 15 for x in x_val]           
            
            fig.add_trace(
                go.Scatter(x=x_val, y=categories, 
                          mode='markers+text', #opacity=1.0,
                          texttemplate='%{x:.0%}', 
                          textposition='bottom center',
                          textfont_color=colors, 
                          name = col_names[i], 
                          hovertemplate=' %{y}<br> %{x:.1%} of total<extra></extra>',
                          marker=dict(color='white', size=marker_size,
                                      line_width=2, line_color=colors)),
                row=1, col=i+1)
            fig.update_xaxes(visible=False, range=[-0.02, 0.6], row=1, col=i+1)
            
    # update subtitle positions
    for annotation in fig['layout']['annotations']:
                annotation['yanchor']='middle'
                annotation['xanchor']='center'
                annotation['y']=1.1
    fig.update_yaxes(ticks='')
    fig.update_layout(**charts_params, template='seaborn', 
                      showlegend=False, width=1100, height=350,)
    
    return fig

#=================Scatter_line_subplots==========================
@st.cache_data
def scatter_line_subplots(df, title=None):
    col_names, categories = df.columns.values, df.index.values
    # create figure with subplots
    fig = make_subplots(rows=1, cols=len(col_names),
                        subplot_titles=col_names,
                        shared_yaxes=True, 
                        horizontal_spacing=0.02)
    # add charts to subplots
    for i, col in enumerate(col_names):
            x_val =  df[col]
            loli_colors = ['red' if x == max(x_val) else '#376274' for x in x_val]
            marker_size = [15 if x == max(x_val) else 10 for x in x_val] 

            fig.add_trace(
                go.Scatter(x=x_val, y=categories,
                           mode='markers+text+lines',
                           texttemplate='%{x:.0%}',
                           textposition='bottom center',
                           textfont_color=loli_colors,
                           name = col_names[i],
                           hovertemplate=' %{y}<br> %{x:.1%} of total<extra></extra>',
                           marker=dict(color='white', size=marker_size, opacity=1.0, 
                                       line_width=2, line_color=loli_colors)),
                row=1, col=i+1)
            fig.update_xaxes(visible=False, range=[-0.02, max(x_val)*1.15], row=1, col=i+1)

    # update subtitle positions
    for annotation in fig['layout']['annotations']:
                annotation['yanchor']='middle'
                annotation['xanchor']='center'
                annotation['y']=1.05
                
    fig.update_yaxes(ticks='')
    fig.update_layout(**charts_params,
                      title=title, template='seaborn',
                      showlegend=False, width=1100, height=600,)

    return fig

#=================Lolipop_subplots===============================
@st.cache_data
def lolipop_subplots(df, sort_week=None):
    col_names, categories = df.columns.values, df.index.values

    fig = make_subplots(rows=1, cols=len(col_names),
                         subplot_titles=col_names,  
                         shared_yaxes=True,     
                         horizontal_spacing=0.02)

    # add charts to subplots
    for i, col in enumerate(col_names):
            x_val =  df[col]
            loli_colors = ['red' if x == max(x_val) else '#376274' for x in x_val]
            marker_size = [20 if x == max(x_val) else 15 for x in x_val]

            for x, y, c in zip(x_val, categories, loli_colors):
                fig.add_trace(
                  go.Scatter(x=[0, x], y=[y, y], stackgaps='infer zero',
                            mode='lines+text', opacity=0.8,  hoverinfo='skip',
                            line_color=c, line_width=3,
                            name = col_names[i]),
                row=1, col=i+1)

            fig.add_trace(
                go.Scatter(x=x_val, y=categories,
                          mode='markers+text',
                          texttemplate='%{x:.0%}',
                          textposition='bottom center',
                          textfont_color=loli_colors,
                          name = col_names[i],
                          hovertemplate=' %{y}<br> %{x:.1%} of total<extra></extra>',
                          marker=dict(color='white', size=marker_size, opacity=1.0, 
                                      line_width=2, line_color=loli_colors)),
                row=1, col=i+1)
            fig.update_xaxes(visible=False, range=[0, max(x_val)*1.5], row=1, col=i+1)
    
    # update subtitle positions
    for annotation in fig['layout']['annotations']:
                annotation['yanchor']='middle'
                annotation['xanchor']='center'
                annotation['y']=1.1
    fig.update_yaxes(ticks='', categoryorder='array', categoryarray= sort_week)
    fig.update_layout(**charts_params, 
                      showlegend=False, width=1100, height=350,)
    return fig

#=================Metric_card====================================
@st.cache_data
def create_metric_card(df, delta):
    fig = make_subplots(rows=2, cols=2, 
                        vertical_spacing=0, horizontal_spacing=0,
                        row_heights =[0.7, 1],
                        specs=[[{}, {}],
                              [{"colspan": 2}, None]])    
    text = df.name.split('_')[0]
    sum = df.sum()
    # add scatter with text and sum value
    fig.add_scatter(x=[0], y=[2],
                    text=f'{text}<br><b>{sum:,.0f}<b>', 
                    mode='text', textposition='middle left',
                    hoverinfo='skip', textfont_size=18,
                    row = 1, col = 1)        
    # define color and symbol
    change_color = ['#376274' if el <=0 else 'red' for el in delta]
    symbol = ['triangle-down' if el <=0 else 'triangle-up' for el in delta]
    # add scatter with text and delta
    fig.add_scatter(x=[0], y=[5], 
                      text=delta , mode='markers+text', texttemplate='<b>%{text:,.0f}<b>',
                      textposition='middle right',
                      hoverinfo='skip', textfont_size=14, textfont_color=change_color,
                      marker=dict(symbol=symbol, size=16, color = change_color), 
                      row = 1, col = 2)
    # add line chart
    fig.add_scatter(x=df.index,  y=df.values, 
                    mode='lines', fill = 'tozeroy', name='',
                    hovertemplate='Month : %{x}<br>Value : %{y}',                      
                    line_width=2, line_color='rgba(0, 70, 100, 0.5)',
                    fillcolor = 'rgba(0, 70, 100, 0.1)',
                    row = 2, col = 1)
    # add scatter with max and min values
    fig.add_scatter(x=[df.idxmax(), df.idxmin()], 
                     y=[df.max(), df.min()],
                    mode='markers', marker_color=['red', 'rgba(0, 70, 100, 0.8)'],
                    name='', row = 2, col = 1)
    # update layout
    fig.for_each_xaxis(lambda t: t.update(visible=False))
    fig.for_each_yaxis(lambda t: t.update(visible=False))
    fig.update_layout(showlegend=False, **charts_params,                      
                      width=300, height=150) 
     
    return fig

#==================Bar_area_subplots================================
@st.cache_data
def bar_area_subplots(df, title=None, order_array=None, marker_colors=None):
    fig = make_subplots(rows=2, cols=2, 
                        vertical_spacing=0, horizontal_spacing=0,
                        row_heights =[0.4, 1], column_widths=[1, 0.4],
                        specs=[[{}, {}],
                              [{"colspan": 2}, None]])
    # add bar charts
    for col in df.columns.values:
        fig.add_bar(x=df.index, y=df[col], 
                    opacity=0.8, marker_cornerradius=10,
                    marker_color = marker_colors.get(col), 
                    texttemplate='%{y:.1f}', textposition='outside',
                    name=col,              
                    row = 2, col = 1)
     # add area charts 
    area = px.area(df)
    for el in area.data:
        fig.add_trace(el, row = 1, col = 2, )
    fig.for_each_trace(
         lambda t: t.update(textfont_color=marker_colors.get(t.name),
                            hovertemplate='Speed Limit :%{x}<br>%{y:.1f}% of total'))    
    # update subtitle positions
    for annotation in fig['layout']['annotations']:
                annotation['xanchor']='right'
                annotation['y']=0.95 
     # update legend and fill color         
    for i in range (3, 6) :
      fig.data[i].showlegend = False
      fig.data[i].fillcolor = f"rgba{hex_to_rgba(fig.data[i].line.color, 0.8)}" 
    # update xaxis and yaxis
    fig.for_each_xaxis(lambda t: t.update(categoryorder='array', categoryarray=order_array))
    fig.for_each_yaxis(lambda t: t.update(range=[0, 90]))
    # update layout
    fig.update_layout(legend=dict(orientation="h", title="", 
                                  yanchor="top", y=0.98,
                                  xanchor="right", x=0.7), 
                      showlegend=True, width=1100, height=350,
                      title=title, title_x=0.3, title_y=0.85,
                      **charts_params, xaxis2_visible=False,
                      yaxis2_visible=False, yaxis3_title='% of total')
                      
    return fig

#==================Other_subplots================================

