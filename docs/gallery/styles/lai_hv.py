"""
Leaf area index, high vegetation
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 67  
     * - **shortName**
       - lai_hv  


 

Default style: 
--------------
**Contour shade (Level list : (0./1/2/3/4/5/6/7)** \[sh_grn_f0t7lst]  

.. image:: /_static/styles/lai_hv-sh_grn_f0t7lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Level list : (0./1/2/3/4/5/6/7)** \[sh_grn_f0t7lst]

.. image:: /_static/styles/lai_hv-sh_grn_f0t7lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lai_hv")

 

data =  magics.mgrib(grib_input_file_name = "lai_hv.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_grn_f0t7lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lai_hv-sh_grn_f0t7lst.png'

