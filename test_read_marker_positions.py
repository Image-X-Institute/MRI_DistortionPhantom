from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
import numpy as np

data_loc = 'marker_positions.txt'
data = np.loadtxt(data_loc)

test_vol = MarkerVolume(data.T)
