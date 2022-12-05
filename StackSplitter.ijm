folder="20221011_Pre2_Day1/" // has to have a slash in the end
path = "/Volumes/msdata/flwilfli/Lab/users/Jeremy/Stellaris/FRAP_Pre2/"
file = path + "20221011_Pre2_Day1.lif";



setBatchMode(true);
setOption("ExpandableArrays", true);
/*
Dialog.create("Open series by name");
Dialog.addFile("File", "");
Dialog.addString("Series name", "");
Dialog.addChoice("Matching", newArray("contains", "equals"), "contains");
Dialog.show();

file = Dialog.getString();
seriesName = Dialog.getString();
matchMode = Dialog.getChoice(); */
matchMode = "contains"
seriesName = "001";
run("Bio-Formats Macro Extensions");
Ext.setId(file);

Ext.getSeriesCount(nSeries);
//IJ.log(seriesName);
for(j = 0; j < 1; j++){
	seriesName = String.pad(j,3);
	IJ.log(seriesName);
	seriesToOpen = "";
	sIdx = 0;
	for(i = 0; i < nSeries; i++) {
		Ext.setSeries(i);
		Ext.getSeriesName(name);
		//IJ.log(name);
		if((matchMode == "equals" && name == seriesName) || (matchMode == "contains" && indexOf(name, seriesName) >= 0)) {
			if (sIdx == 0){
				finalName = name;
				seriesToOpen = seriesToOpen + (i+1);
				sIdx++;
			} else {
				seriesToOpen = seriesToOpen + ", " + (i+1);
				if(sIdx == 1) {break;}
			}
		}
	}
	if (sIdx != 0){
	IJ.log(seriesToOpen);
	run("Bio-Formats Importer", "open=[" + file + "] autoscale color_mode=Composite rois_import=[ROI manager] concatenate_series view=Hyperstack stack_order=XYCZT series_list=["+seriesToOpen+"]");

	finalNameArray = split(finalName,'/');
	File.makeDirectory(path+folder);
	saveAs("tiff",path+folder+finalNameArray[0]);
	close();
	}
}


//Array.print(seriesToOpen)
//IJ.log(seriesToOpen);
//for(s = 0; s < seriesToOpen.length; s++)
//	run("Bio-Formats Importer", "open=[" + file + "] autoscale color_mode=Composite rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT series_list=" + seriesToOpen[s]);
