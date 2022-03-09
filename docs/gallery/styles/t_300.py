"""
Temperature (300 hPa)
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **level**
       - 300  
     * - **levelist**
       - 300  
     * - **levtype**
       - pl  
     * - **paramId**
       - 130  
     * - **shortName**
       - t  


 

Default style: 
--------------
**Contour shade (Range: -64 / 52)** \[sh_all_fM64t52i4]  

.. image:: /_static/styles/t-sh_all_fM64t52i4.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: -64 / 52)** \[sh_all_fM64t52i4]

.. image:: /_static/styles/t-sh_all_fM64t52i4.png  
    :width: 400
    
**Contour (Interval 2, red, dash)** \[ct_red_i2_dash]

.. image:: /_static/styles/t-ct_red_i2_dash.png  
    :width: 400
    
**Contour shade (Range: -76 / 56)** \[sh_gry_fM72t56lst]

.. image:: /_static/styles/t-sh_gry_fM72t56lst.png  
    :width: 400
    
**Additional 1 (Range: -80 / 56)** \[sh_all_fM80t56i4_v2]

.. image:: /_static/styles/t-sh_all_fM80t56i4_v2.png  
    :width: 400
    
**Additional 2 (Range: -50/58 by 2)** \[sh_all_fM50t58i2]

.. image:: /_static/styles/t-sh_all_fM50t58i2.png  
    :width: 400
    
**Contour (interval 4, thickness 3)** \[ct_red_i4_t3]

.. image:: /_static/styles/t-ct_red_i4_t3.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "t")

 

data =  magics.mgrib(grib_input_file_name = "t.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_all_fM64t52i4",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/t-sh_all_fM64t52i4.png'

