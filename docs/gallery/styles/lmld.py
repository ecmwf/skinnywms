"""
Lake mix-layer depth
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228009  
     * - **shortName**
       - lmld  


 

Default style: 
--------------
**Contour shade (Range: 0 / 50), used for Lake mix-layer depth** \[sh_purple_f0t50]  

.. image:: /_static/styles/lmld-sh_purple_f0t50.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0 / 50), used for Lake mix-layer depth** \[sh_purple_f0t50]

.. image:: /_static/styles/lmld-sh_purple_f0t50.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lmld")

 

data =  magics.mgrib(grib_input_file_name = "lmld.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_purple_f0t50",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lmld-sh_purple_f0t50.png'

