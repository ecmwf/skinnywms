"""
Low vegetation cover
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 27  
     * - **shortName**
       - cvl  


 

Default style: 
--------------
**Contour shade (Level list : (0./0.1/0.2/0.3/0.4/0.5/0.6/0.7/0.8/0.9/1)** \[sh_grn_f0t1lst]  

.. image:: /_static/styles/cvl-sh_grn_f0t1lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Level list : (0./0.1/0.2/0.3/0.4/0.5/0.6/0.7/0.8/0.9/1)** \[sh_grn_f0t1lst]

.. image:: /_static/styles/cvl-sh_grn_f0t1lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "cvl")

 

data =  magics.mgrib(grib_input_file_name = "cvl.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_grn_f0t1lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/cvl-sh_grn_f0t1lst.png'

