"""
Sub-surface runoff
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 9  
     * - **shortName**
       - ssro  


 

Default style: 
--------------
**Contour shade (Range: 0.5 / 20), used for Runoff** \[sh_blugrn_f05t20]  

.. image:: /_static/styles/ssro-sh_blugrn_f05t20.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.5 / 20), used for Runoff** \[sh_blugrn_f05t20]

.. image:: /_static/styles/ssro-sh_blugrn_f05t20.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "ssro")

 

data =  magics.mgrib(grib_input_file_name = "ssro.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blugrn_f05t20",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/ssro-sh_blugrn_f05t20.png'

