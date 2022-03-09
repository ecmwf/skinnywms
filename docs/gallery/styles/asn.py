"""
Snow albedo
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 32  
     * - **shortName**
       - asn  


 

Default style: 
--------------
**Shade (Range: 0/1)** \[sh_brown_f0t1]  

.. image:: /_static/styles/asn-sh_brown_f0t1.png  
    :width: 400

Other available styles:
-----------------------

**Shade (Range: 0/1)** \[sh_brown_f0t1]

.. image:: /_static/styles/asn-sh_brown_f0t1.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "asn")

 

data =  magics.mgrib(grib_input_file_name = "asn.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_brown_f0t1",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/asn-sh_brown_f0t1.png'

