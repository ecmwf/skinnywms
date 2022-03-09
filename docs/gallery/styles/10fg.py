"""
10 metre wind gust since previous post-processing
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 49  
     * - **shortName**
       - 10fg  


 

Default style: 
--------------
**Contour shade (Range: 10 / 70, yellow-red)** \[sh_red_f10t70lst]  

.. image:: /_static/styles/10fg-sh_red_f10t70lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 10 / 70, yellow-red)** \[sh_red_f10t70lst]

.. image:: /_static/styles/10fg-sh_red_f10t70lst.png  
    :width: 400
    
**Contour shade (Range: 2 / 50, interval 2)** \[sh_all_f2t50i2]

.. image:: /_static/styles/10fg-sh_all_f2t50i2.png  
    :width: 400
    
**Contour shade (Range: 10 / 100, green)** \[sh_grn_f10t100lst]

.. image:: /_static/styles/10fg-sh_grn_f10t100lst.png  
    :width: 400
    
**Contour shade (Range: 0.3 / 50, Beaufort wind scale)** \[sh_all_f03t70_beauf]

.. image:: /_static/styles/10fg-sh_all_f03t70_beauf.png  
    :width: 400
    
**Contour (Interval 5, orange-red)** \[ct_red_i5]

.. image:: /_static/styles/10fg-ct_red_i5.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "10fg")

 

data =  magics.mgrib(grib_input_file_name = "10fg.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_red_f10t70lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/10fg-sh_red_f10t70lst.png'

