"""
Potential evaporation
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228251  
     * - **shortName**
       - pev  


 

Default style: 
--------------
**Contour shade (Range: 0 / 1), used for Evaporation** \[sh_blugrn_f0t1_i01]  

.. image:: /_static/styles/pev-sh_blugrn_f0t1_i01.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0 / 1), used for Evaporation** \[sh_blugrn_f0t1_i01]

.. image:: /_static/styles/pev-sh_blugrn_f0t1_i01.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "pev")

 

data =  magics.mgrib(grib_input_file_name = "pev.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blugrn_f0t1_i01",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/pev-sh_blugrn_f0t1_i01.png'

