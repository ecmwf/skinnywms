"""
Snow evaporation
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 44  
     * - **shortName**
       - es  


 

Default style: 
--------------
**Contour shade (Level list : 0./0.001/0.002/0.003/0.004/0.005/0.01/1) Used for Snow evaporation** \[sh_blugrn_f0t1lst]  

.. image:: /_static/styles/es-sh_blugrn_f0t1lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Level list : 0./0.001/0.002/0.003/0.004/0.005/0.01/1) Used for Snow evaporation** \[sh_blugrn_f0t1lst]

.. image:: /_static/styles/es-sh_blugrn_f0t1lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "es")

 

data =  magics.mgrib(grib_input_file_name = "es.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blugrn_f0t1lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/es-sh_blugrn_f0t1lst.png'

