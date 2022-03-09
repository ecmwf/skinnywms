"""
Lake ice surface temperature
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228013  
     * - **shortName**
       - lict  


 

Default style: 
--------------
**Contour shade (Range: -68 / 0)** \[sh_blue_fM68t0_i4]  

.. image:: /_static/styles/lict-sh_blue_fM68t0_i4.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: -68 / 0)** \[sh_blue_fM68t0_i4]

.. image:: /_static/styles/lict-sh_blue_fM68t0_i4.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lict")

 

data =  magics.mgrib(grib_input_file_name = "lict.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blue_fM68t0_i4",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lict-sh_blue_fM68t0_i4.png'

