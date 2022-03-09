"""
Low cloud cover
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 186  
     * - **shortName**
       - lcc  


 

Default style: 
--------------
**Transparency grey (rgbA)** \[transparency_grey]  

.. image:: /_static/styles/lcc-transparency_grey.png  
    :width: 400

Other available styles:
-----------------------

**Transparency grey (rgbA)** \[transparency_grey]

.. image:: /_static/styles/lcc-transparency_grey.png  
    :width: 400
    
**Contour shade (0-1, intervals in octas)** \[sh_gry_f0t1lst]

.. image:: /_static/styles/lcc-sh_gry_f0t1lst.png  
    :width: 400
    
**Contour shade (0-1, intervals in octas)** \[sh_redgry_f0t1lst]

.. image:: /_static/styles/lcc-sh_redgry_f0t1lst.png  
    :width: 400
    
**Transparency grey for sct and bkn (or ovc) clouds** \[tran_gry_f03t1lst]

.. image:: /_static/styles/lcc-tran_gry_f03t1lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lcc")

 

data =  magics.mgrib(grib_input_file_name = "lcc.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "transparency_grey",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lcc-transparency_grey.png'

