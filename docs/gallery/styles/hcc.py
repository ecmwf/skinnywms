"""
High cloud cover
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 188  
     * - **shortName**
       - hcc  


 

Default style: 
--------------
**Transparency white** \[transparency_white]  

.. image:: /_static/styles/hcc-transparency_white.png  
    :width: 400

Other available styles:
-----------------------

**Transparency white** \[transparency_white]

.. image:: /_static/styles/hcc-transparency_white.png  
    :width: 400
    
**Contour shade (0-1, intervals in octas)** \[sh_whi_f0t1lst]

.. image:: /_static/styles/hcc-sh_whi_f0t1lst.png  
    :width: 400
    
**Contour shade (0-1, intervals in octas)** \[sh_blugry_f0t1lst]

.. image:: /_static/styles/hcc-sh_blugry_f0t1lst.png  
    :width: 400
    
**Transparency white for sct and bkn (or ovc) clouds** \[tran_whi_f03t1lst]

.. image:: /_static/styles/hcc-tran_whi_f03t1lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "hcc")

 

data =  magics.mgrib(grib_input_file_name = "hcc.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "transparency_white",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/hcc-transparency_white.png'

