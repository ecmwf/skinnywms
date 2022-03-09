"""
Soil type
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 43  
     * - **shortName**
       - slt  


 

Default style: 
--------------
**Marker in all colours (Coarse range: 0 / 7) used for Soil type** \[mrk_all2_f0t7lst]  

.. image:: /_static/styles/slt-mrk_all2_f0t7lst.png  
    :width: 400

Other available styles:
-----------------------

**Marker in all colours (Coarse range: 0 / 7) used for Soil type** \[mrk_all2_f0t7lst]

.. image:: /_static/styles/slt-mrk_all2_f0t7lst.png  
    :width: 400
    
**Marker in all colours (Coarse range: 0 / 7) used for Soil type** \[mrk_all1_f0t7lst]

.. image:: /_static/styles/slt-mrk_all1_f0t7lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "slt")

 

data =  magics.mgrib(grib_input_file_name = "slt.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "mrk_all2_f0t7lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/slt-mrk_all2_f0t7lst.png'

