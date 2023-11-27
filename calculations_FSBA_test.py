
from pytest import approx, raises
import calculations_FSBA as calc


data_frame = calc.aisc_w_section("aisc_w_si.csv")

design_section = "W460X158"

area = data_frame["A"].get(design_section)
d = data_frame["d"].get(design_section)
b = data_frame["bf"].get(design_section)
t = data_frame["tf"].get(design_section)
w = data_frame["tw"].get(design_section)
i_x = data_frame["Ix"].get(design_section)
i_y = data_frame["Iy"].get(design_section)
s_x = data_frame["Sx"].get(design_section)
s_y = data_frame["Sy"].get(design_section)
z_x = data_frame["Zx"].get(design_section)
z_y = data_frame["Zy"].get(design_section)
J = data_frame["J"].get(design_section)
Cw = data_frame["Cw"].get(design_section)
fy = 350
phi = 0.9

E = 200e3 #Steel Elastic Modulus
G = 77e3  #Shear Modulus
L_min = 200
L_max = 5000
interval = 100
Lateral_cond = "Supported"
flange_edge = 1
omega=1.0

def test_flange_class():
    flange_class = calc.flange_class(b, t, fy)  
    assert flange_class == 1

def test_web_class():
    web_class = calc.web_class(d, t, w, fy)  
    assert web_class == 1
    
def test_flexural_capacity():
    Mr = calc.flexural_capacity(d, b, t, w, fy, phi, s_x, s_y, z_x, z_y, E, G, i_y, J, Cw, Lateral_cond, L_min, L_max, interval, flange_edge, omega)
    if (Lateral_cond == "Unsupported"):
        rr = min(Mr[1])/1e6
        assert rr == approx(141.14716)
    else:
        rr = Mr/1e6 
        assert rr == approx(1187.55000)
    

def test_shear_capacity():

    Vr = calc.shear_capacity(d, w, t, fy, phi)
    Vr_req = Vr/1e3
    assert Vr_req == approx(1481.2875)

def test_aisc_w_section():
    database = calc.aisc_w_section("aisc_w_si.csv")

    assert database.loc["W1100X390", "Ix"] == 10000000000.0 
