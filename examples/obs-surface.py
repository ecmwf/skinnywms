from Magics import macro as magics
import json


	


output = magics.output(output_formats= ['png'],
                output_name_first_page_number= "off",
                output_name= "obs-surface")


area = magics.mmap(subpage_lower_left_latitude = 35. ,
                    subpage_lower_left_longitude = -30.,
                    subpage_upper_right_longitude = -25,
                    subpage_upper_right_latitude = 40
                     )


coastlines = magics.mcoast()

data = magics.mgeojson(geojson_input_filename = "../skinnywms/testdata/small.geojson")

symbol = magics.msymb(symbol_type = "marker",
	symbol_marker_index = 15,
	legend = "off",
	symbol_colour = "red",
	symbol_height = 1.00)

magics.plot(output, area, data, symbol, coastlines)
