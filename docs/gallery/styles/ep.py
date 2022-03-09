"""
2m temperature anomaly of at least +2K
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 131001  
     * - **shortName**
       - 2tag2  
     * - **type**
       - ep  


 

Default style: 
--------------
**Contour shade (0-100%, blue-purple)** \[sh_blup_f0t100lst]  

.. image:: /_static/styles/2tag2-sh_blup_f0t100lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (0-100%, blue-purple)** \[sh_blup_f0t100lst]

.. image:: /_static/styles/2tag2-sh_blup_f0t100lst.png  
    :width: 400
    
**Contour shade (0-100%, light blue-purple)** \[sh_blup_f0t100lst_light]

.. image:: /_static/styles/2tag2-sh_blup_f0t100lst_light.png  
    :width: 400
    
**Contour shade (5-100%, more levels)** \[sh_rgb_f5t100]

.. image:: /_static/styles/2tag2-sh_rgb_f5t100.png  
    :width: 400
    
**Contour shade (5-100%, transparent, more levels)** \[sh_rgb_transparent_f5t100]

.. image:: /_static/styles/2tag2-sh_rgb_transparent_f5t100.png  
    :width: 400
    
**Contour shade (5-100%, More transparent, more levels)** \[sh_rgb_transparent25_f5t100]

.. image:: /_static/styles/2tag2-sh_rgb_transparent25_f5t100.png  
    :width: 400
    
**Contour shade (0-100%, green)** \[sh_grn_f0t100lst]

.. image:: /_static/styles/2tag2-sh_grn_f0t100lst.png  
    :width: 400
    
**Contour shade (0-100%, light green)** \[sh_grn_f0t100lst_light]

.. image:: /_static/styles/2tag2-sh_grn_f0t100lst_light.png  
    :width: 400
    
**Contour shade (0-100%, red)** \[sh_red_f0t100lst]

.. image:: /_static/styles/2tag2-sh_red_f0t100lst.png  
    :width: 400
    
**Contour shade (0-100%, light red)** \[sh_red_f0t100lst_light]

.. image:: /_static/styles/2tag2-sh_red_f0t100lst_light.png  
    :width: 400
    
**Contour shade (0-100%, every 10%)** \[genesis_prob]

.. image:: /_static/styles/2tag2-genesis_prob.png  
    :width: 400
    
**Contour shade (0-100%, every 10%)** \[genesis_prob_light]

.. image:: /_static/styles/2tag2-genesis_prob_light.png  
    :width: 400
    
**Black contours for probabilities (thickness 2)** \[ct_prob_black_f5t100t2]

.. image:: /_static/styles/2tag2-ct_prob_black_f5t100t2.png  
    :width: 400
    
**Blue contours for probabilities (thickness 2)** \[ct_prob_blue_f5t100t2]

.. image:: /_static/styles/2tag2-ct_prob_blue_f5t100t2.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "2tag2")

 

data =  magics.mgrib(grib_input_file_name = "2tag2.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blup_f0t100lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/2tag2-sh_blup_f0t100lst.png'

