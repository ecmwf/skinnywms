"""
Snow density
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 33  
     * - **shortName**
       - rsn  


 

Default style: 
--------------
**Contour shade (Level list : (100./120/140/160/180/200/220/240/260/280/300/320/340/360/480)** \[sh_blu_f100t480lst]  

.. image:: /_static/styles/rsn-sh_blu_f100t480lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Level list : (100./120/140/160/180/200/220/240/260/280/300/320/340/360/480)** \[sh_blu_f100t480lst]

.. image:: /_static/styles/rsn-sh_blu_f100t480lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "rsn")

 

data =  magics.mgrib(grib_input_file_name = "rsn.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blu_f100t480lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/rsn-sh_blu_f100t480lst.png'

