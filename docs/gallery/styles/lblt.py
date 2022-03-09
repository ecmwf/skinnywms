"""
Lake bottom temperature
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228010  
     * - **shortName**
       - lblt  


 

Default style: 
--------------
**Contour shade (Range: 0 / 40)** \[sh_blured_f0t40_i4]  

.. image:: /_static/styles/lblt-sh_blured_f0t40_i4.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0 / 40)** \[sh_blured_f0t40_i4]

.. image:: /_static/styles/lblt-sh_blured_f0t40_i4.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lblt")

 

data =  magics.mgrib(grib_input_file_name = "lblt.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blured_f0t40_i4",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lblt-sh_blured_f0t40_i4.png'

