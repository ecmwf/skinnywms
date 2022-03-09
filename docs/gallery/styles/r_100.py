"""
Relative humidity (100 hPa)
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **levelist**
       - 100  
     * - **levtype**
       - pl  
     * - **paramId**
       - 157  
     * - **shortName**
       - r  


 

Default style: 
--------------
**Contour shade (Range: 65 / 100)** \[sh_grnblu_f65t100i15]  

.. image:: /_static/styles/r-sh_grnblu_f65t100i15.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 65 / 100)** \[sh_grnblu_f65t100i15]

.. image:: /_static/styles/r-sh_grnblu_f65t100i15.png  
    :width: 400
    
**Contour shade (Range: 65 / 100)** \[sh_grnblu_f65t100i15_light]

.. image:: /_static/styles/r-sh_grnblu_f65t100i15_light.png  
    :width: 400
    
**Contour (Range: 65 / 100)** \[ct_grnblu_f65t100i15]

.. image:: /_static/styles/r-ct_grnblu_f65t100i15.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "r")

 

data =  magics.mgrib(grib_input_file_name = "r.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_grnblu_f65t100i15",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/r-sh_grnblu_f65t100i15.png'

