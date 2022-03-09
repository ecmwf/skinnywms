"""
Lake shape factor
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228012  
     * - **shortName**
       - lshf  


 

Default style: 
--------------
**Contour shade (Range: 0.6 / 0.8), used for Lake shape factor** \[sh_blugrn_f06t08_i002]  

.. image:: /_static/styles/lshf-sh_blugrn_f06t08_i002.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.6 / 0.8), used for Lake shape factor** \[sh_blugrn_f06t08_i002]

.. image:: /_static/styles/lshf-sh_blugrn_f06t08_i002.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lshf")

 

data =  magics.mgrib(grib_input_file_name = "lshf.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blugrn_f06t08_i002",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lshf-sh_blugrn_f06t08_i002.png'

