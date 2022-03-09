"""
Snowmelt
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 45  
     * - **shortName**
       - smlt  


 

Default style: 
--------------
**Contour shade (Level list : 0./0.05/0.1/0.15/0.2/0.25/0.3/0.35/0.4)** \[sh_all_f0t04lst]  

.. image:: /_static/styles/smlt-sh_all_f0t04lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Level list : 0./0.05/0.1/0.15/0.2/0.25/0.3/0.35/0.4)** \[sh_all_f0t04lst]

.. image:: /_static/styles/smlt-sh_all_f0t04lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "smlt")

 

data =  magics.mgrib(grib_input_file_name = "smlt.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_all_f0t04lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/smlt-sh_all_f0t04lst.png'

