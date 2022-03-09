"""
Convective precipitation
=============================

The metadata used to detect the styles are :  

.. list-table::  
     :widths: 25 25 

     * - **paramId**
       - 143  
     * - **shortName**
       - cp  


 

Default style: 
--------------
**Contour shade (Range: 0.5 / 250, with isolines)** \[sh_blured_f05t300lst]  

.. image:: /_static/styles/cp-sh_blured_f05t300lst.png  
    :width: 400

Other available styles:
-----------------------

**Contour shade (Range: 0.5 / 250, with isolines)** \[sh_blured_f05t300lst]

.. image:: /_static/styles/cp-sh_blured_f05t300lst.png  
    :width: 400
    
**Contour shade (Range: 1.0 / 250, no isolines)** \[sh_blured_f1t100lst]

.. image:: /_static/styles/cp-sh_blured_f1t100lst.png  
    :width: 400
    
**Contour shade (Range: 1.0 / 250, no isolines)** \[sh_blured_f1t100lst_dark]

.. image:: /_static/styles/cp-sh_blured_f1t100lst_dark.png  
    :width: 400
    
**Contour shade (Range: 1.0 / 250, no isolines)** \[sh_grnvio_f1t100lst]

.. image:: /_static/styles/cp-sh_grnvio_f1t100lst.png  
    :width: 400
    
**Contour shade (Range: 0.5 / 300, no isolines)** \[sh_all_f05t300lst]

.. image:: /_static/styles/cp-sh_all_f05t300lst.png  
    :width: 400
    
**Contour shade (Range: 0.1 / 500)** \[sh_blured_f01t500lst]

.. image:: /_static/styles/cp-sh_blured_f01t500lst.png  
    :width: 400
    
**Contour shade (Range: 0/300, with isolines)** \[sh_blured_f0t300]

.. image:: /_static/styles/cp-sh_blured_f0t300.png  
    :width: 400
    
**Contour (Range: 1 / 250, thickness 2, blue)** \[ct_blumag_lst]

.. image:: /_static/styles/cp-ct_blumag_lst.png  
    :width: 400
    
 

"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "cp")

 

data =  magics.mgrib(grib_input_file_name = "cp.grib")
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "sh_blured_f05t300lst",)
        
coastlines = magics.mcoast(map_grid = "off" )
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/cp-sh_blured_f05t300lst.png'

