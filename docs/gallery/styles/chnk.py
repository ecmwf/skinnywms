"""
Charnock
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 148  
     * - **shortName**
       - chnk  


 

Default style: 
--------------
**Contour shade (Range: 0/0.1)** \[sh_red_f0t01_16]  

.. image:: /_static/styles/chnk-sh_red_f0t01_16.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0/0.1)** \[sh_red_f0t01_16]

.. image:: /_static/styles/chnk-sh_red_f0t01_16.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "chnk")

 

data =  magics.mgrib(grib_input_file_name = "chnk.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_red_f0t01_16",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/chnk-sh_red_f0t01_16.png'

