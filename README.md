# FRAP-Processing

This script should be running out-of-the-box from the [conda environment](#install-conda-environment) described below. Open the [main notebook](main-notebook.ipynb) in a code editor of your choice or by opening a terminal and running ```jupyter notebook```. In case you have any remaining questions, please don't hesitate to contact jbrenner@biochem.mpg.de or the Wilfling Group at the Max-Planck-Institute of Biophysics. 
Please consider also citing the script with the paper soon to be published by Licheva*, Pflaum*, Babic*, Manchilla* et al.

## The processing workflow
In order to process your FRAP-experiments in batch, we need a folder with single TIFF-stacks (tyx) per position. The notebook will loop through every of these positions and let you semi-automatedly process each stack. If you acquired your data on a Leica microscope and therefore have data in the LIF-format, you can use the ImageJ macro [StackSplitter.ijm](StackSplitter.ijm) to extract single TIF-stacks.

### 1. Zooming the extents of the bleached area
In the first window, you are prompted to zoom the ROI into the viewer by [left mouse] and dragging. To detect the ROI, you can loop through the timeseries with the [mouse wheel] or by dragging the slider under the window. Resetting the ROI works with [shift]+[alt], while the ROI is accepted by pressing [enter].
| Before Bleach|  After Bleach |
| :---: | :---: |
| ![](doc/img/1.png)  | ![](doc/img/2.png) |

| Before selection of punctum | After selection of punctum |
| :---: | :---: |
| ![](doc/img/3.png)  | ![](doc/img/4.png) |

### 2. Segmenting the bleached and unbleached area
Next, the program will automatically detect the punctum and segment it into _bleached_ and _unbleached_ area. This can be adjusted by dragging the vertices of the ROIs to the desired location. Holding the [shift] and dragging an edge moves all of the vertices. The ROI can be reset by clicking __ROI Method 1__ again.
| Segmentation |  Adjusted segmentation |
| :---: | :---: |
| ![](doc/img/5.png)  | ![](doc/img/6.png) |

### 3. Export and continue
 Once __EXPORT__ is pressed, an excel file with the same name as the stack is created. The format looks like this:

| Timepoints | Area(all) |	Mean_intensity(all)	| Area(bleached) |	Mean_intensity(bleached) |	Area(unbleached) |	Mean_intensity(unbleached) | Single Normalization | Double Normalization|
|---|---|---|---|---|---|---|---|---|
|0||||||||
|...||||||||
|End||||||||

To continue stack processing, click __Next Stack__. It will also remind you if you forgot to export your latest ROIs. In case you would like to abort processing, just close the window as usual.


## Install conda environment
In case, you havent installed "conda", download the latest miniconda version: https://docs.anaconda.com/free/miniconda/

After installing, open a terminal, move to a desired installation location, download the repository and create an environment. Before every use, make sure to activate the enviroment accordingly.
```sh
## To clone this repository:
git clone https://github.com/CraignRush/FRAP-Processing.git YOURFOLDERNAME

## Create a new environment for the processing
conda env create --name frap-processing --file=environment.yml

# To activate this environment, use
conda activate frap-processing

## To deactivate an active environment, use
conda deactivate
```

