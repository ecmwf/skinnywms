"""
U component of wind (300 hPa)
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **levelist**
       - 300  
     * - **levtype**
       - pl  
     * - **paramId**
       - 131  
     * - **shortName**
       - u  


 

Default style: 
--------------
**Contour shade for wind components at pressure levels** \[sh_blue_red_100]  

.. image:: /_static/styles/u-sh_blue_red_100.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade for wind components at pressure levels** \[sh_blue_red_100]

.. image:: /_static/styles/u-sh_blue_red_100.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "u")

 

data =  magics.mgrib(grib_input_file_name = "u.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blue_red_100",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/u-sh_blue_red_100.png'

