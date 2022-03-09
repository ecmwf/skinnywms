"""
Convective avail. pot.energy
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 59  
     * - **shortName**
       - cape  


 

Default style: 
--------------
**Shade from 100 to 4500 (orange-blue)** \[range_100_4500]  

.. image:: /_static/styles/cape-range_100_4500.png  
    :width: 400

Other available styles:
-----------------------

**Shade from 100 to 4500 (orange-blue)** \[range_100_4500]

.. image:: /_static/styles/cape-range_100_4500.png  
    :width: 400
    
**Shade from 50 to 9000** \[range_50_9000]

.. image:: /_static/styles/cape-range_50_9000.png  
    :width: 400
    
**Contour red lines (Range: 50/8000)** \[ct_red_f50t8000]

.. image:: /_static/styles/cape-ct_red_f50t8000.png  
    :width: 400
    
**Contour green lines (Range: 10/8000)** \[ct_green_f10t8000]

.. image:: /_static/styles/cape-ct_green_f10t8000.png  
    :width: 400
    
**Shading (50 to 8000)** \[cape_extra1]

.. image:: /_static/styles/cape-cape_extra1.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "cape")

 

data =  magics.mgrib(grib_input_file_name = "cape.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "range_100_4500",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/cape-range_100_4500.png'

