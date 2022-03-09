"""
Type of high vegetation
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 30  
     * - **shortName**
       - tvh  


 

Default style: 
--------------
**Marker in all colours (Coarse range: 0 / 19) used for Type of high vegetation** \[mrk_grn_f0t19lst]  

.. image:: /_static/styles/tvh-mrk_grn_f0t19lst.png  
    :width: 400

Other available styles:
-----------------------

**Marker in all colours (Coarse range: 0 / 19) used for Type of high vegetation** \[mrk_grn_f0t19lst]

.. image:: /_static/styles/tvh-mrk_grn_f0t19lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "tvh")

 

data =  magics.mgrib(grib_input_file_name = "tvh.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "mrk_grn_f0t19lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/tvh-mrk_grn_f0t19lst.png'

