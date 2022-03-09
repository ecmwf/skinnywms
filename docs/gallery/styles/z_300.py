"""
Geopotential (300 hPa)
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **levelist**
       - 300  
     * - **paramId**
       - 129  
     * - **shortName**
       - z  


 

Default style: 
--------------
**Contour (interval 5, thickness 2, black)** \[ct_blk_i5_t2]  

.. image:: /_static/styles/z-ct_blk_i5_t2.png  
    :width: 400

Other available styles:
-----------------------

**Contour (interval 5, thickness 2, black)** \[ct_blk_i5_t2]

.. image:: /_static/styles/z-ct_blk_i5_t2.png  
    :width: 400
    
**Contour (interval 5, thickness 2, blue)** \[ct_blue_i5_t2]

.. image:: /_static/styles/z-ct_blue_i5_t2.png  
    :width: 400
    
**Contour (interval 5, thickness 2, red)** \[ct_red_i5_t2]

.. image:: /_static/styles/z-ct_red_i5_t2.png  
    :width: 400
    
**Contour (interval 5, thickness 2, green)** \[ct_green_i5_t2]

.. image:: /_static/styles/z-ct_green_i5_t2.png  
    :width: 400
    
**Contour with no labels (interval 5, black)** \[ct_blk_i5_t1]

.. image:: /_static/styles/z-ct_blk_i5_t1.png  
    :width: 400
    
**Contour (interval 4, thickness 2, brown)** \[ct_brn_i4_t2]

.. image:: /_static/styles/z-ct_brn_i4_t2.png  
    :width: 400
    
**Contour (interval 2, thickness 4, black)** \[ct_blk_i2_t4]

.. image:: /_static/styles/z-ct_blk_i2_t4.png  
    :width: 400
    
**Contour (interval 2, thickness 4, green)** \[ct_green_i2_t4]

.. image:: /_static/styles/z-ct_green_i2_t4.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "z")

 

data =  magics.mgrib(grib_input_file_name = "z.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "ct_blk_i5_t2",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/z-ct_blk_i5_t2.png'

