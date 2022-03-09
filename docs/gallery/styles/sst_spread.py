"""
Specified sea surface temperature
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 34  
     * - **shortName**
       - sst  
     * - **type**
       - es  


 

Default style: 
--------------
**Contour shade (Range: 0 / 5)** \[sh_blue_f0t5_i1]  

.. image:: /_static/styles/sst-sh_blue_f0t5_i1.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0 / 5)** \[sh_blue_f0t5_i1]

.. image:: /_static/styles/sst-sh_blue_f0t5_i1.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "sst")

 

data =  magics.mgrib(grib_input_file_name = "sst.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blue_f0t5_i1",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/sst-sh_blue_f0t5_i1.png'

