import base64
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space as avs



# Define All Pages
p1 = st.Page("pages/page_1.py", title="Overview", icon=":material/directions_car:", default=True)
p2 = st.Page("pages/page_2.py", title="Data", icon=":material/dataset:")
p3 = st.Page("pages/page_3.py", title="Charts", icon=":material/bar_chart:")
p4 = st.Page("pages/page_4.py", title="Map", icon=":material/map:")

# Initialize the session state
if 'df' not in st.session_state:
    st.session_state['df'] = None

# Set the logo    
st.logo("images/road_accidents_logo240_22.png")

# Install Multipage
pg = st.navigation({"Home": [p1], "Data and Charts": [p2, p3], "Map": [p4],})
pg.run()

#=========== Using CSS Style =====================================
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

#========== Define the background image =========================
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_img_as_base64(png_file)
    page_bg_img = '''
    <style>
    [data-testid="stHeader"]{
    background-image: url("data:image/png;base64,%s");
    background-size: cover; 
    }
    </style>
    ''' % bin_str

    return st.markdown(page_bg_img, unsafe_allow_html=True)    

set_png_as_page_bg("images/header_for_app.png") 

#========Sidebar================================================
with st.sidebar.expander("**Data Sources**"):
    # Display an image with a hyperlink
    st.markdown(
        """
        <a href="https://data.gov.il/dataset/teunot2022">
            <img src="data:image/png;base64,{}" width="150">
    </a>""".format(
        base64.b64encode(open("images/GOV_LOGO.png", "rb").read()).decode()
    ),
        unsafe_allow_html=True) 
    st.write('')     
    st.markdown(
    """<a href="https://www.cbs.gov.il/he/publications/Pages/2024/%D7%AA%D7%90%D7%95%D7%A0%D7%95%D7%AA-%D7%93%D7%A8%D7%9B%D7%99%D7%9D-%D7%A2%D7%9D-%D7%A0%D7%A4%D7%92%D7%A2%D7%99%D7%9D-2022-%D7%A1%D7%99%D7%9B%D7%95%D7%9E%D7%99%D7%9D-%D7%9B%D7%9C%D7%9C%D7%99%D7%99%D7%9D.aspx">
    <img src="data:image/png;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("images/CBS_LOGO2.png", "rb").read()).decode()
    ),unsafe_allow_html=True)
    st.write('')

with st.sidebar.expander("**Other sources**"):
    st.markdown("Data visualization using the [Plotly](https://plotly.com/python/)")
    st.markdown("Creating Maps using the [Folium](https://python-visualization.github.io/folium/latest/)")

with st.sidebar:
    # Adds 5 vertical spaces
    avs(15)
    st.divider()
    # Display the GitHub-Logo with a hyperlink
    st.markdown(
        """
        <p style="text-align: center;">Made with love by Natalia</p>
        <a href="https://github.com/natatsypora" style="display: flex; justify-content: center; align-items: center;">
        <img src="data:image/png;base64,{}" width="50" alt="GitHub Logo">
        </a>""" .format(base64.b64encode(open("images\GitHub-Logo.png", "rb"
                                              ).read()).decode()
                ), unsafe_allow_html=True)

