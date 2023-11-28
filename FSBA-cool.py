import streamlit as st
import plotly.graph_objects as go
import sectionproperties.pre.library.steel_sections as steel_geom
from sectionproperties.pre.pre import Material
from sectionproperties.analysis.section import Section
import calculations_FSBA as calc
from handcalcs.decorator import handcalc

##########################################
# BEAM ANALYSIS of I SECTION is an app that calculates the flexural capacity of an I section of different 
# class for a lateral braced or laterally unbraced condition. The app also calculates the shear capacity of an I 
# beam. The program assumes the I section bends about the major axis
##########################################

st.header('Beam Analysis of an I Section', divider='blue')

st.sidebar.subheader("Bracing Length Parameters")
L_min = st.sidebar.number_input("Minimum Unbraced Length ($mm$)", value=200)
L_max = st.sidebar.number_input("Maximum Unbraced Length ($mm$)", value=5000)
interval = st.sidebar.number_input("Unbraced length step interval ($mm$)", value=100)

# Section Properties
st.sidebar.subheader("Material Properties")


Lateral_cond = st.selectbox(
    'Choose Lateral support condition',
    ('Supported', 'Unsupported'))

data_frame = calc.aisc_w_section("aisc_w_si.csv")

design_section = st.text_input('Input your I section designation (ex. W460X52)', value="W460X52")

area = data_frame["A"].get(design_section)  #Area of section
d = data_frame["d"].get(design_section)     #Depth of section
b = data_frame["bf"].get(design_section)    #Flange width
t = data_frame["tf"].get(design_section)    #Flange thickness
w = data_frame["tw"].get(design_section)    #Web thickness
i_x = data_frame["Ix"].get(design_section)  #Second moment of inertia about major axis
i_y = data_frame["Iy"].get(design_section)  #Second moment of inertia about minor axis
s_x = data_frame["Sx"].get(design_section)  #Elastic Seciton Modulus about major axis
s_y = data_frame["Sy"].get(design_section)  #Elastic Seciton Modulus about minor axis
z_x = data_frame["Zx"].get(design_section)  #Plastic Seciton Modulus about major axis
z_y = data_frame["Zy"].get(design_section)  #Plastic Seciton Modulus about minor axis
J = data_frame["J"].get(design_section)     #Torsional constant
Cw = data_frame["Cw"].get(design_section)   #Warping constant
E = st.sidebar.number_input("Elastic modulus section (MPa)", value=200e3)
G = st.sidebar.number_input("Shear modulus of section (MPa)", value=77e3)
fy = st.sidebar.number_input("Yield strength of section (MPa)", value=350)
phi = 0.9 #material reduction factor of steel
flange_edge = st.selectbox(
    'Number of edges supporting the flange',
    (1, 2))
omega = 1.0


st.divider()

st.subheader('Class of a Section')
flange_class = calc.flange_class(b, t, fy)

st.markdown(f"The class of *flange section* of :blue[**{design_section}**] is **{flange_class}**")

# Classification of section from Cl.11.1 and Cl.11.2 of CSA S16-19

web_class = calc.web_class(d, t, w, fy)
st.markdown(f"The class of *web section* of :blue[**{design_section}**] is **{web_class}**")

st.divider()

st.subheader('Flexural Capacity')
## Analysis from CISC Handbook geometric properties of W460x60 section using Cl13.6 from CSA S16-19 code
Mr = calc.flexural_capacity(d, b, t, w, fy, phi, s_x, s_y, z_x, z_y, E, G, i_y, J, Cw, Lateral_cond, L_min, L_max, interval, flange_edge, omega)
if (Lateral_cond == "Unsupported"):
    rr = min(Mr[1])/1e6
    st.markdown(f"The flexural capacity of :blue[**{design_section}**] section using *CISC geometric properties* is **{rr:.3f} kN.m** ")
else:
    rr = Mr/1e6
    st.markdown(f"The flexural capacity of :blue[**{design_section}**] section using *CISC geometric properties* is **{rr:.3f} kN.m** ")

    
## Using Section Properties Program
k1=data_frame["kdes"].get(design_section)  # Distances given for I section in Canadian Steel Handbook CISC
w= data_frame["tw"].get(design_section) # web thickness

Wsection1 = steel_geom.i_section(
    d=data_frame["d"].get(design_section),
    b=data_frame["bf"].get(design_section),
    t_f=data_frame["tf"].get(design_section),
    t_w=data_frame["tw"].get(design_section),
    r=k1 - w/2,
    n_r=15,
)
Wsection1

Wsection1.plot_geometry()

#Mesh the section and create analysis section

Wsection1.create_mesh(mesh_sizes=10)
sec = Section(Wsection1, time_info=True)
sec.plot_mesh()

#Perform analysis

sec.calculate_geometric_properties()
sec.calculate_plastic_properties()
sec.calculate_warping_properties()

#Review results
sec.display_results()

# Retrieve individual properties from results

sec.calculate_frame_properties()
area = sec.get_area()
ixx_c, iyy_c, ixy_c = sec.get_ic()
angle = sec.get_phi()
j = sec.get_j()
sxx, syy = sec.get_s()   # defines plastic properties of section in section properties
zxx1, zyy1, zxx2, zyy2  = sec.get_z() # defines elastic properties of section in section properties
Iw = sec.get_gamma()

    # st.write(f"Area = {area:.1f} mm2")
    # st.write(f"Ixx = {ixx_c:.3e} mm4")
    # st.write(f"Iyy = {iyy_c:.3e} mm4")
    # st.write(f"Ixy = {ixy_c:.3e} mm4")
    # st.write(f"Principal axis angle = {angle:.1f} deg")
    # st.write(f"Torsion constant = {j:.3e} mm4")
    # st.write(f"Zxx = {sxx:.3e} mm3")
    # st.write(f"Zyy = {syy:.3e} mm3")
    # st.write(f"Sxx = {zxx1:.3e} mm3")
    # st.write(f"Syy = {zyy2:.3e} mm3")
    # st.write(f"Warping constant = {Iw:.3e} mm6")

Mr_secprop = calc.flexural_capacity(d, b, t, w, fy, phi, zxx1, zyy2, sxx, syy, E, G, iyy_c, j, Iw, Lateral_cond, L_min, L_max, interval, flange_edge, omega)
      
if(Lateral_cond == "Unsupported"):
    tt = min(Mr_secprop[1])/1e6
    st.markdown(f"The flexural capacity of :blue[**{design_section}**] section using *section properties program* is **{tt:.3f} kN.m**")
else:
    tt = Mr/1e6
    st.markdown(f"The flexural capacity of :blue[**{design_section}**] section using *section properties program* is **{rr:.3f} kN.m**")


perc_diff = (tt-rr)/100 * 100
st.markdown(f"The percentage difference between moment capacities is **{perc_diff:.2f}%**")

st.divider()

st.subheader('Shear Capacity')
Vr = calc.shear_capacity(d, w, t, fy, phi)
Vr_req = Vr/1e3
st.markdown(f"The shear capacity of :blue[**{design_section}**] section is **{Vr_req:.3f} kN**")

st.divider()
st.subheader('Moment Plot')
## Plotting figures for CSA geometric properties and Section Properties program
if(Lateral_cond == "Unsupported"):

    fig = go.Figure()

    # Plot lines
    fig.add_trace(
        go.Scatter(
        x=Mr[0], 
        y=Mr[1],
        line={"color": "red"},
        name="Mr capacity with LTB using CISC Hanbook properties"
        )
    )

    fig.add_trace(
        go.Scatter(
        x=Mr_secprop[0], 
        y=Mr_secprop[1],
        line={"color": "teal"},
        name="Mr capacity with LTB using Section Properties program"
        )
    )

    fig.layout.title.text = "Factored Moment Capacity of I-Section"
    fig.layout.xaxis.title = "Unbraced Length L, mm"
    fig.layout.yaxis.title = "Factored Moment Capacity, N"


    st.plotly_chart(fig)


