"""
Large-scale precipitation fraction
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 50  
     * - **shortName**
       - lspf  


 

Default style: 
--------------
**Contour shade (Range: 1000 / 12000)** \[sh_blu_f1kt12k]  

.. image:: /_static/styles/lspf-sh_blu_f1kt12k.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 1000 / 12000)** \[sh_blu_f1kt12k]

.. image:: /_static/styles/lspf-sh_blu_f1kt12k.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "lspf")

 

data =  magics.mgrib(grib_input_file_name = "lspf.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blu_f1kt12k",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/lspf-sh_blu_f1kt12k.png'

