"""
Geopotential (100 hPa)
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **levelist**
       - 100  
     * - **paramId**
       - 129  
     * - **shortName**
       - z  


 

Default style: 
--------------
**Contour (interval 8, thickness 2, black)** \[ct_blk_i8_t2]  

.. image:: /_static/styles/z-ct_blk_i8_t2.png  
    :width: 400

Other available styles:
-----------------------

**Contour (interval 8, thickness 2, black)** \[ct_blk_i8_t2]

.. image:: /_static/styles/z-ct_blk_i8_t2.png  
    :width: 400
    
**Contour (interval 10, thickness 2, black)** \[ct_blk_i10_t2]

.. image:: /_static/styles/z-ct_blk_i10_t2.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "z")

 

data =  magics.mgrib(grib_input_file_name = "z.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "ct_blk_i8_t2",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/z-ct_blk_i8_t2.png'

