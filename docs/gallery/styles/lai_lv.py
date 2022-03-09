"""
Leaf area index, low vegetation
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 66  
     * - **shortName**
       - lai_lv  


 

Default style: 
--------------
**Contour shade (Level list : (0.1/1/2/3/4/5)** \[sh_grn_f0t5lst]  

.. image:: /_static/styles/lai_lv-sh_grn_f0t5lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Level list : (0.1/1/2/3/4/5)** \[sh_grn_f0t5lst]

.. image:: /_static/styles/lai_lv-sh_grn_f0t5lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lai_lv")

 

data =  magics.mgrib(grib_input_file_name = "lai_lv.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_grn_f0t5lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lai_lv-sh_grn_f0t5lst.png'

