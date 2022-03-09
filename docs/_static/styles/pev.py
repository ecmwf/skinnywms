"""
Potential evaporation
=============================

The metadata used to detect the styles are :

**paramId:** 228251
**shortName:** pev



Styles available:


Contour shade (Range: 0 / 1), used for Evaporation
-------------------------------------------------
.. image:: ../_static/style/pev-sh_blugrn_f0t1_i01.png
    :width: 400



"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "pev")

 

data =  magics.mgrib(grib_input_file_name = "pev.grib"
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "",)
        
coastlines = magics.mcoast()
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/pev-.png'

