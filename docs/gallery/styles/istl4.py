"""
Ice temperature layer 4
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 38  
     * - **shortName**
       - istl4  


 

Default style: 
--------------
**Contour shade (Range: -14 / -1.6)** \[sh_blu_fM14tM16]  

.. image:: /_static/styles/istl4-sh_blu_fM14tM16.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: -14 / -1.6)** \[sh_blu_fM14tM16]

.. image:: /_static/styles/istl4-sh_blu_fM14tM16.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "istl4")

 

data =  magics.mgrib(grib_input_file_name = "istl4.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blu_fM14tM16",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/istl4-sh_blu_fM14tM16.png'

