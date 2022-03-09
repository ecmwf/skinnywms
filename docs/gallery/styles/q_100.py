"""
Specific humidity (100 hPa)
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **levelist**
       - 100  
     * - **paramId**
       - 133  
     * - **shortName**
       - q  


 

Default style: 
--------------
**Contour shade (Range: 0 - 28)** \[sh_spechum_option1]  

.. image:: /_static/styles/q-sh_spechum_option1.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0 - 28)** \[sh_spechum_option1]

.. image:: /_static/styles/q-sh_spechum_option1.png  
    :width: 400
    
**Contour shade (Range: 0 - 28)** \[sh_spechum_option2]

.. image:: /_static/styles/q-sh_spechum_option2.png  
    :width: 400
    
**Contour shade (Range: 0 - 28)** \[sh_spechum_option3]

.. image:: /_static/styles/q-sh_spechum_option3.png  
    :width: 400
    
**Contour (interval 2, thickness 2, black)** \[ct_blk_i2_t2]

.. image:: /_static/styles/q-ct_blk_i2_t2.png  
    :width: 400
    
**Shading (0 to 30)** \[spechum_extra1]

.. image:: /_static/styles/q-spechum_extra1.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "q")

 

data =  magics.mgrib(grib_input_file_name = "q.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_spechum_option1",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/q-sh_spechum_option1.png'

