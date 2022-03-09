"""
Cloud base height
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228023  
     * - **shortName**
       - cbh  


 

Default style: 
--------------
**Contour shade (Range: 0/22000)** \[sh_cbh_blk_f0t22000]  

.. image:: /_static/styles/cbh-sh_cbh_blk_f0t22000.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0/22000)** \[sh_cbh_blk_f0t22000]

.. image:: /_static/styles/cbh-sh_cbh_blk_f0t22000.png  
    :width: 400
    
**Contour shade (Range: 0/22000)** \[sh_cbh_f0t22000]

.. image:: /_static/styles/cbh-sh_cbh_f0t22000.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "cbh")

 

data =  magics.mgrib(grib_input_file_name = "cbh.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_cbh_blk_f0t22000",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/cbh-sh_cbh_blk_f0t22000.png'

