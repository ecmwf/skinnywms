"""
Large-scale snowfall
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 240  
     * - **shortName**
       - lsf  


 

Default style: 
--------------
**Contour shade (Range: 0.05 / 250, with isolines)** \[sh_blured_f001t25lst]  

.. image:: /_static/styles/lsf-sh_blured_f001t25lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.05 / 250, with isolines)** \[sh_blured_f001t25lst]

.. image:: /_static/styles/lsf-sh_blured_f001t25lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lsf")

 

data =  magics.mgrib(grib_input_file_name = "lsf.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blured_f001t25lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lsf-sh_blured_f001t25lst.png'

