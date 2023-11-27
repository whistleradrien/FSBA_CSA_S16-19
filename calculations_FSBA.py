import sectionproperties.pre.library.steel_sections as steel_geom
from sectionproperties.pre.pre import Material
from sectionproperties.analysis.section import Section
from handcalcs.decorator import handcalc
import pandas as pd
import math


def flange_class(flange_width:float, 
                     flange_thickness:float, 
                     fy:float) -> int:
        """
        This function Returns a float representing the the classification of flange of an I section either
        Class 1, 2, 3 and 4 according to Table 2 of CSA S16-19
        assumptions: Bending about major axis
        """
        flange_class = 0
        effective_width = flange_width/2

        if (effective_width /flange_thickness) <= (145 / math.sqrt(fy)):
            flange_class = 1
            return flange_class  
        elif (effective_width /flange_thickness) <= (170 / math.sqrt(fy)):
            flange_class = 2
            return flange_class
        elif (effective_width /flange_thickness) <= (200 / math.sqrt(fy)):
            flange_class = 3
            return flange_class 
        else: 
            flange_class = 4
            return flange_class 
        
def web_class(beam_depth:float,
              flange_thickness:float, 
                web_thickness:float, 
                fy:float) -> int:
        """
        This function Returns a float representing the the classification of web of an I section either
        Class 1, 2, 3 and 4 according to Table 2 of CSA S16-19
        """
        web_class = 0
        h = beam_depth - 2*flange_thickness

        if (h /web_thickness) <= (1100 / math.sqrt(fy)):
            web_class = 1
            return  web_class  
        elif (h /web_thickness) <= (1700 / math.sqrt(fy)):
            web_class = 2
            return web_class
        elif (h /web_thickness) <= (1900 / math.sqrt(fy)):
            web_class = 3
            return web_class 
        else: 
            web_class = 4
            return web_class 
        

# def createList(L_min:int, L_max:int, interval:int):
#     L = np.arange(L_min, L_max+1, interval)
#     return L
     
        
def flexural_capacity(beam_depth:float,
                        flange_width:float, 
                          flange_thickness:float,
                          web_thickness:float, 
                          fy:float,
                          phi:float, 
                          sx:float,
                          sy:float, 
                          zx:float, 
                          zy:float,
                          E:float, 
                          G:float, 
                          i_y:float, 
                          J:float, 
                          Cw:float, 
                          Lateral_cond:str, 
                          L_min:float,
                          L_max:float,
                          interval:float,
                          flange_edge:float = 2,
                          omega:float = 1.0) -> list:
    """
    This function calculates the flexural capacity of laterally supported or unsupported
    I section Classes 1, 2, 3 or 4

    Lateral_cond defines lateral condition of the beam whether it is laterally supported or unsupported
    assume bending is about the major axis
    """

    # Classification of flange of I section
    fl_class = flange_class(flange_width, flange_thickness, fy)

    wb_class = web_class(beam_depth, flange_thickness, web_thickness, fy )
    
    h = beam_depth - 2*flange_thickness #web heigth

    # Shear area
    Aw = beam_depth * web_thickness

    #Flange area
    Af = 2 * flange_width * flange_thickness

    # Elastic and Plastic moment capacities in major and minor axes
    My_x = phi * sx * fy
    Mp_x = phi * zx * fy

    # My_y = phi * sy * fy
    # Mp_y = phi * zy * fy

    #factored moment 
    Mf = 50e6
    
    L = list(range(L_min, L_max+interval, interval))
    
    if (Lateral_cond == "Supported"):
            if (fl_class == 1) or (fl_class == 2):  
            #Cl.3.5(a)
                Mr = Mp_x
                return Mr 

            elif ((fl_class == 3) and (wb_class == 1)):
                #Cl.3.5(b)
                Mr = My_x
                return Mr 

            elif ((fl_class == 3) and (wb_class == 4)):
                #Cl.3.5(c)(ii)
                Mr = My_x * (1-0.0005*(Aw/Af)*(h/web_thickness)-(1900/(math.sqrt(Mf/phi*sx)))) #Cl.3.5(c)(ii)
                return Mr 

            elif ((fl_class == 4) and (wb_class == 3 or 2 or 1)): 
                #Cl.3.5(c)(iii)
                if (flange_edge == 2):
                    Se = (670 * flange_thickness) / (math.sqrt(fy))
                    Mr = phi * Se * fy 
                    return Mr 
        
                else:
                    Se = (200 * flange_thickness) / (math.sqrt(fy)) 
                    Mr = phi * Se * fy
                    return Mr 
            else:
                return print("Mr shall be computed in accordance with CSA S136") 
    
    else:
        #Critical Elastic moment of unbraced segment
        Mr = []
        Mu = []

        for i in L:
            Mui = ((omega * math.pi)/(1.2*i)) * math.sqrt(E*i_y*G*J + ((math.pi*E) / i)**2 * i_y * Cw)
            if ((fl_class == 1 or 2) and (wb_class == 1 or 2) and (Mui > 0.67*Mp_x)):
                Mri = min(1.15*phi*Mp_x * (1 - ((0.28*Mp_x)/Mui)), phi*Mp_x)
                Mu.append(Mui)
                Mr.append(Mri)
            elif ((fl_class == 1 or 2) and (wb_class == 1 or 2) and (Mui <= 0.67*Mp_x)):
                Mri = phi*Mui
                Mu.append(Mui)
                Mr.append(Mri)
            elif ((fl_class == 3) and (wb_class == 3) and (Mui > 0.67*My_x)):
                Mri = min(1.15*phi*My_x * (1 - ((0.28*My_x)/Mui)), phi*My_x)
                Mu.append(Mui)
                Mr.append(Mri)
            elif ((fl_class == 4) and (wb_class == 4) and (Mui > 0.67*My_x)):
                if (flange_edge == 2):
                    Se = (670 * flange_thickness) / (math.sqrt(fy))
                    Mri = min(1.15*phi*My_x * (1 - ((0.28*My_x)/Mui)), phi*Se * fy)
                    Mu.append(Mui)
                    Mr.append(Mri)

                else:
                    Se = (200 * flange_thickness) / (math.sqrt(fy)) 
                    Mri = min(1.15*phi*My_x * (1 - ((0.28*My_x)/Mui)), phi*Se * fy)
                    Mu.append(Mui)
                    Mr.append(Mri)
            else:
                Mri = phi*Mui
                Mu.append(Mui)
                Mr.append(Mri)
              
    return L, Mr

def shear_capacity(beam_depth:float, 
                    web_thickness:float,
                    flange_thickness:float, 
                    fy:float,
                    phi:float,  
                    ) -> float:
    """
    This function calculates the shear capacity of an I section assuming the webs are unstiffened
    """
    
    Aw = beam_depth * web_thickness

    h = beam_depth - (2*flange_thickness)


    if ((h/web_thickness) <= 1014/(math.sqrt(fy))):
            Fs = 0.66*fy
            Vr = phi*Aw*Fs
            return Vr

    elif (h/web_thickness) >= (1014/(math.sqrt(fy))) and (h/web_thickness) <= (1435/(math.sqrt(fy))):
            Fs = (670*(math.sqrt(fy)))/(h/web_thickness)
            Vr = phi*Aw*Fs
            return Vr

    else: 
         Fs = (961200)/(h/web_thickness)**2
         Vr = phi*Aw*Fs
         return Vr
        

    

def aisc_w_section(filename: str)-> object:
    """This functionn read a CSV file and return a dataframe. The csv file uses SI system units.
    """
    
    # filename = __file__

    # newfile = filename.replace(filename,"asic_w_si.csv")

    if filename  == "aisc_w_si.csv":
        df = pd.read_csv(filename)
        sub_df = df.copy()
        

        sub_df["Ix"] = sub_df["Ix"]*1e6
        sub_df["Zx"] = sub_df["Zx"]*1e3
        sub_df["Sx"] = sub_df["Sx"]*1e3
        sub_df["Iy"] = sub_df["Iy"]*1e6
        sub_df["Zy"] = sub_df["Zy"]*1e3
        sub_df["Sy"] = sub_df["Sy"]*1e3
        sub_df["J"] = sub_df["J"]*1e3
        sub_df["Cw"] = sub_df["Cw"]*1e9

        mod_df = sub_df.set_index('Section')
        
        return mod_df
    else:
        df = pd.read_csv(filename)
        sub_df = df.copy()

        mod_df = sub_df.set_index('Section')

    return mod_df
