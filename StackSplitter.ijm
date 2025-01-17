/*
 * StackSplitter.ijm
 * Author: Johann Brenner
 * 
 * ImageJ macro to split a multi-series LIF file into individual TIFF files.
 * Processes series that match a specified pattern and saves them to a target folder.
 */

// Configuration variables
folder = "20221011_Pre2_Day1/" // Target folder (must end with slash)
path = "/Volumes/msdata/flwilfli/Lab/users/Jeremy/Stellaris/FRAP_Pre2/"
file = path + "20221011_Pre2_Day1.lif";

// Set up ImageJ options
setBatchMode(true); // Process without displaying images
setOption("ExpandableArrays", true);

/* Commented out interactive dialog - using hardcoded values instead
Dialog.create("Open series by name");
Dialog.addFile("File", "");
Dialog.addString("Series name", "");
Dialog.addChoice("Matching", newArray("contains", "equals"), "contains");
Dialog.show();

file = Dialog.getString();
seriesName = Dialog.getString();
matchMode = Dialog.getChoice(); */

// Search parameters
matchMode = "contains";
seriesName = "001";

// Initialize Bio-Formats
run("Bio-Formats Macro Extensions");
Ext.setId(file);

// Get total number of series in file
Ext.getSeriesCount(nSeries);

// Process each series
for(j = 0; j < 1; j++) {
	// Generate padded series name (e.g. 001, 002, etc)
	seriesName = String.pad(j,3);
	IJ.log(seriesName);
	seriesToOpen = "";
	sIdx = 0;
	
	// Search through all series for matches
	for(i = 0; i < nSeries; i++) {
		Ext.setSeries(i);
		Ext.getSeriesName(name);
		
		// Check if series name matches our criteria
		if((matchMode == "equals" && name == seriesName) || 
		   (matchMode == "contains" && indexOf(name, seriesName) >= 0)) {
			if (sIdx == 0){
				finalName = name;
				seriesToOpen = seriesToOpen + (i+1);
				sIdx++;
			} else {
				seriesToOpen = seriesToOpen + ", " + (i+1);
				if(sIdx == 1) {break;} // Stop after finding second match
			}
		}
	}
	
	// If matches were found, process and save the series
	if (sIdx != 0){
		IJ.log(seriesToOpen);
		// Import matched series
		run("Bio-Formats Importer", "open=[" + file + 
		    "] autoscale color_mode=Composite rois_import=[ROI manager] " +
		    "concatenate_series view=Hyperstack stack_order=XYCZT " +
		    "series_list=["+seriesToOpen+"]");

		// Create output directory and save as TIFF
		finalNameArray = split(finalName,'/');
		File.makeDirectory(path+folder);
		saveAs("tiff",path+folder+finalNameArray[0]);
		close();
	}
}

/* Alternative approach using array of series (currently disabled)
Array.print(seriesToOpen)
IJ.log(seriesToOpen);
for(s = 0; s < seriesToOpen.length; s++)
	run("Bio-Formats Importer", "open=[" + file + 
	    "] autoscale color_mode=Composite rois_import=[ROI manager] " +
	    "view=Hyperstack stack_order=XYCZT series_list=" + seriesToOpen[s]); */
