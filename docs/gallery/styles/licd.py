"""
Lake ice total depth
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228014  
     * - **shortName**
       - licd  


 

Default style: 
--------------
**Contour shade (Range: 0.5 / 3), used for Lake ice depth** \[sh_blue_f03t3]  

.. image:: /_static/styles/licd-sh_blue_f03t3.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.5 / 3), used for Lake ice depth** \[sh_blue_f03t3]

.. image:: /_static/styles/licd-sh_blue_f03t3.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "licd")

 

data =  magics.mgrib(grib_input_file_name = "licd.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blue_f03t3",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/licd-sh_blue_f03t3.png'

