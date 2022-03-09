"""
Lake total layer temperature
=============================

The metadata used to detect the styles are :

**paramId:** 228011
**shortName:** ltlt



Styles available:


Contour shade (Range: 0 / 36)
-------------------------------------------------
.. image:: ../_static/style/ltlt-sh_red_f0t36_i4.png
    :width: 400



"""


from Magics import macro as magics

output = magics.output(output_formats = ['png'],
                output_name_first_page_number = "off",
                output_name = "ltlt")

 

data =  magics.mgrib(grib_input_file_name = "ltlt.grib"
        
contour = magics.mcont(contour_automatic_setting="style_name",
                        contour_style_name= "",)
        
coastlines = magics.mcoast()
        
magics.plot(output, data, contour, coastlines)

# sphinx_gallery_thumbnail_path = '_static/styles/ltlt-.png'

