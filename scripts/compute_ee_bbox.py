import numpy as np
from pyproj import Transformer

t = Transformer.from_crs("EPSG:4326", "EPSG:1078", always_xy=True)

# Sample the whole globe densely to capture the true projected extent.
lons = np.linspace(-180, 180, 7201)
lats = np.linspace(-90, 90, 3601)
L, P = np.meshgrid(lons, lats)
X, Y = t.transform(L, P)

print("min_x (w_lon):", round(float(X.min()), 2))
print("min_y (s_lat):", round(float(Y.min()), 2))
print("max_x (e_lon):", round(float(X.max()), 2))
print("max_y (n_lat):", round(float(Y.max()), 2))
PY