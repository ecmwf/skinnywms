"""
Lake cover
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 26  
     * - **shortName**
       - cl  


 

Default style: 
--------------
**Contour shade (Range: 0.1 / 1), used for Lake cover** \[sh_purple_f01t1]  

.. image:: /_static/styles/cl-sh_purple_f01t1.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.1 / 1), used for Lake cover** \[sh_purple_f01t1]

.. image:: /_static/styles/cl-sh_purple_f01t1.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "cl")

 

data =  magics.mgrib(grib_input_file_name = "cl.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_purple_f01t1",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/cl-sh_purple_f01t1.png'

