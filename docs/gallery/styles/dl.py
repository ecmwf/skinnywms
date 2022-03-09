"""
Lake total depth
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228007  
     * - **shortName**
       - dl  


 

Default style: 
--------------
**Contour shade (Range: 0.5 / 9000), used for Lake depth** \[sh_blue_f05t9000]  

.. image:: /_static/styles/dl-sh_blue_f05t9000.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.5 / 9000), used for Lake depth** \[sh_blue_f05t9000]

.. image:: /_static/styles/dl-sh_blue_f05t9000.png  
    :width: 400
    
**Contour shade (Range: 0.5 / 9000), used for Lake depth** \[sh_blue_f1t9000]

.. image:: /_static/styles/dl-sh_blue_f1t9000.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "dl")

 

data =  magics.mgrib(grib_input_file_name = "dl.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blue_f05t9000",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/dl-sh_blue_f05t9000.png'

