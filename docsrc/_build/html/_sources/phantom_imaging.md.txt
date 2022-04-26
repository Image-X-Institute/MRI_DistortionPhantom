# Phantom Imaging

Below are some things to think about when imaging the phantom. \

All our development work has been on a siemens scanner running VB ADD VERSION. Therefore, although the principles outlined below are scanner independent, the specific instructions are siemens specific. If you can update these instructions for other vendors, please do so! 


## Fat-Water chemical shift
If you use oil capsules as the markers in your phantom, there is an important effect you must be aware of: [Fat-Water chemical shift](https://mriquestions.com/f-w-chemical-shift.html). This means if your scanner has a center frequency calibrated for water (which it almost certainly does), the oil based capsules will be offset in the readout direction. There are a number of things you can do to avoid this:

1. **Set the scanner center frequency to oil instead of wate**r. Most scanners should have some method to reset the central frequency based on a given load. Specific instructions are scanner specific; ADD SIEMENS INSTRUCTIONS.  The phantom itself may not provide sufficient load to carry out this procedure; in this case you could simply use a bottle of oil. If you successfully reset the central frequency, you will remove any offsets due to fat-water shift. The central frequency is encoded in the dicom header, so you can always retrospectively check what was used.
2. **Use a large bandwidth**: Since fundamentally this is a B0 distortion, the same mitigation used for B0 can be used. If you use a large enough bandwidth, the fat-water shift will be almost eliminated.  
3. **Correct in software**: the fat-water shift is a known effect; its magnitude at a given field strength can easily be calculated. Therefore, it is in principle possible to correct for it in software. PUT LINK TO OUR SOFTWARE HERE.
4. **Use water based markers:** In many ways this is the ideal solution, except for one thing: we haven't been able to find any water based markers yet!

## Separation of B0/ Gradient distortion effects

There are two 'system based' sources of distortion in MRI: the gradient coils, and B0 inhomogeneity (there are also patient specific effects, which we ignore here.)

- Gradient distortion appears in every direction, and is essentially independent of imaging sequence.
- B0 distortion appears only in the **readout** direction, and is highly sequence dependent. 

For a given sequence, these effects can be separated as follows: 

1. Take the first phantom image
2. Reverse the phase encoding direction. See image below 
3. The gradient distortion is the same in both images, while the direction of B0 distortion is reversed. Therefore, the gradient distortion is the average position of each marker between the two images.

To put this into a very simple example: consider just one marker and one dimension. This marker has a ground truth position (for instance measured with CT) of x_gt; gradient non-linearity causes it instead to appear at x_gnl. If we take two scans with opposite encoding directions x_forward and x_backward, we observe this marker at x_scan1 and x_scan2. We can separate the gradient and B0 effects as follows:
$$
x\_gnl = mean(x\_scan1, x\_scan2) = (x\_scan1, x\_scan2)/2\\
x\_b0 = x\_gt - x\_gnl
$$
At this point, we have a good estimate of the perturbation caused by gradient non-linearity in x which will be sequence independent, and a good estimate of the perturbation caused by B0, which will be sequence dependent. We would then have to repeat this process for encoding directions y and z to get a good estimate of each gradient field.

If this all makes your head hurt as much as it does mine, you have two options:

1. If you don't care about B0 (e.g. you are sure it is small enough that you don't need to worry about it), then use a large imaging bandwidth in conjunction with a spin echo sequence. Both of these will minimize your sensitivity to B0 inhomogeneity such that you can ignore B0 effects.
2. We have provide analysis software (**coming soon**!) ADD LINK that automates these steps for you. 

## Gradient Echo sequences

The gradient echo sequence family will exhibit increased more sensitivity to B0 inhomogeneity than Spin Echo sequences. Therefore, if you are trying to separate B0/ Gradient effects this can be a good sequence to utilize. It is also normally faster than spin echo. On the other hand, it will tend to have lower SNR. 

## Spin Echo sequences

The spin echo sequence family are not as sensitive to B0 as gradient echo. They are slower to run, but often exhibit better SNR, especially if your B0 homogeneity is not great. If you are not interested in quantifying B0, then using this sequence with a  high bandwidth is a good choice. 

## Bandwidth







