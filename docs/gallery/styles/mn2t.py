"""
Minimum temperature at 2 metres since previous post-processing
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 202  
     * - **shortName**
       - mn2t  


 

Default style: 
--------------
**Contour shade (Range: -48 / 56)** \[sh_all_fM48t56i4]  

.. image:: /_static/styles/mn2t-sh_all_fM48t56i4.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: -48 / 56)** \[sh_all_fM48t56i4]

.. image:: /_static/styles/mn2t-sh_all_fM48t56i4.png  
    :width: 400
    
**Contour shade (Range: -64 / 52)** \[sh_all_fM64t52i4]

.. image:: /_static/styles/mn2t-sh_all_fM64t52i4.png  
    :width: 400
    
**Contour (Interval 2, red, dash)** \[ct_red_i2_dash]

.. image:: /_static/styles/mn2t-ct_red_i2_dash.png  
    :width: 400
    
**Contour shade (Range: -32 / 42, interval 2)** \[sh_all_fM32t42i2]

.. image:: /_static/styles/mn2t-sh_all_fM32t42i2.png  
    :width: 400
    
**Contour and shade (Range: -48 / 56, interval 2)** \[sh_all_fM48t56i4_ct_wh]

.. image:: /_static/styles/mn2t-sh_all_fM48t56i4_ct_wh.png  
    :width: 400
    
**Contour shade (Range: -52 / 48)** \[sh_all_fM52t48i4]

.. image:: /_static/styles/mn2t-sh_all_fM52t48i4.png  
    :width: 400
    
**Contour shade (Range: -52 / 48)** \[sh_all_fM52t48i4_light]

.. image:: /_static/styles/mn2t-sh_all_fM52t48i4_light.png  
    :width: 400
    
**Contour shade (Range: -76 / 56)** \[sh_gry_fM72t56lst]

.. image:: /_static/styles/mn2t-sh_gry_fM72t56lst.png  
    :width: 400
    
**Contour (interval 4, thickness 3)** \[ct_red_i4_t3]

.. image:: /_static/styles/mn2t-ct_red_i4_t3.png  
    :width: 400
    
**Additional 1 (Range: -80 / 56)** \[sh_all_fM80t56i4_v2]

.. image:: /_static/styles/mn2t-sh_all_fM80t56i4_v2.png  
    :width: 400
    
**Additional 2 (Range: -50/58 by 2)** \[sh_all_fM50t58i2]

.. image:: /_static/styles/mn2t-sh_all_fM50t58i2.png  
    :width: 400
    
**Temperature below 0 C** \[transparent_zero_blue]

.. image:: /_static/styles/mn2t-transparent_zero_blue.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "mn2t")

 

data =  magics.mgrib(grib_input_file_name = "mn2t.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_all_fM48t56i4",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/mn2t-sh_all_fM48t56i4.png'

