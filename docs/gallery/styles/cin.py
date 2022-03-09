"""
Convective inhibition
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 228001  
     * - **shortName**
       - cin  


 

Default style: 
--------------
**Contour shade (Range: 0/900)** \[sh_red_f0t900]  

.. image:: /_static/styles/cin-sh_red_f0t900.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0/900)** \[sh_red_f0t900]

.. image:: /_static/styles/cin-sh_red_f0t900.png  
    :width: 400
    
**Contour shade (Range: 0/900)** \[sh_black_f0t900]

.. image:: /_static/styles/cin-sh_black_f0t900.png  
    :width: 400
    
**Transparent contour shade (Range: 50/1100)** \[sh_grey_min50]

.. image:: /_static/styles/cin-sh_grey_min50.png  
    :width: 400
    
**Transparent contour shade (Range: 100/1100)** \[sh_grey_min100]

.. image:: /_static/styles/cin-sh_grey_min100.png  
    :width: 400
    
**Transparent contour shade (Range: 200/1100)** \[sh_grey_min200]

.. image:: /_static/styles/cin-sh_grey_min200.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "cin")

 

data =  magics.mgrib(grib_input_file_name = "cin.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_red_f0t900",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/cin-sh_red_f0t900.png'

