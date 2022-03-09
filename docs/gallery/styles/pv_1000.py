"""
Potential vorticity
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 60  
     * - **shortName**
       - pv  


 

Default style: 
--------------
**Contour (interval 2, thickness 3)** \[ct_magenta_i2_t3]  

.. image:: /_static/styles/pv-ct_magenta_i2_t3.png  
    :width: 400

Other available styles:
-----------------------

**Contour (interval 2, thickness 3)** \[ct_magenta_i2_t3]

.. image:: /_static/styles/pv-ct_magenta_i2_t3.png  
    :width: 400
    
**Contour shade (Range: 2 / 30)** \[sh_blu_f02t30]

.. image:: /_static/styles/pv-sh_blu_f02t30.png  
    :width: 400
    
**Contour shade (Range: 0.0 / 1.0 & 1.5 / 20)** \[sh_gry_f0t20lst]

.. image:: /_static/styles/pv-sh_gry_f0t20lst.png  
    :width: 400
    
**Contour (interval 1, thickness 1, violet)** \[ct_vio_i1_t1]

.. image:: /_static/styles/pv-ct_vio_i1_t1.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "pv")

 

data =  magics.mgrib(grib_input_file_name = "pv.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "ct_magenta_i2_t3",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/pv-ct_magenta_i2_t3.png'

