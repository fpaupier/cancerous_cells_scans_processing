 run("32-bit");
run("Invert LUT");
///run("Reverse");
print("Patient name: ",getInfo("0010,0010"));
print("Patient's sex: ",getInfo("0010,0040"));
print("Patient's weight: ",getInfo("0010,1030"));
print("Manufacturer: ",getInfo("0008,0070"));
print("Model: ",getInfo("0008,1090"));
print("Reconstruction: ",getInfo("0054,1103"));
print("Institution name: ",getInfo("0008,0080"));
print("Birth date: ",getInfo("0010,0030"));
print("Series date: ",getInfo("0008,0021"));
print("Convolution kernel: ",getInfo("0018,1210"));
print("Pixel spacing (mm): ",getInfo("0028,0030"));
print("Slice (mm): ",getInfo("0018,0050"));
print("Frame duration (s): ",getInfo("0018,1242"));
print("###########################################################");
// Check the delay between injetion and acquisition
startHour = parseInt(substring(getInfo("0008,0031"),1,3));
startMinute = parseInt(substring(getInfo("0008,0031"),3,5));
injHour = parseInt(substring(getInfo("0018,1072"),1,3));
injMinute = parseInt(substring(getInfo("0018,1072"),3,5));

deltaHour = startHour-injHour;
deltaMinute = startMinute-injMinute;
if(deltaMinute<0)
{
deltaMinute = 60 + deltaMinute;
deltaHour = deltaHour -1;
}
delay = (deltaHour*60)+deltaMinute;
print("Delay (min)",delay);
if((delay<55) || (delay>75))
{
print("*****************************************************");
print("WARNING!!!! Delay not in the range of EANM guidelines");
print("*****************************************************");
}
// End


if( (substring(getInfo("0008,0070"),1,3) == "Ph") && (substring(getInfo("0054,1001"),1,5) != "BQML"))
{
        suvFactor = parseFloat(getInfo("7053,1000"));
        // Intermediate computation for patient 1 -> 33
        //suvFactor = suvFactor/parseFloat(getInfo("0028,1053"));
        // End intermediate computation for patient 1 -> 33
}
else
{
 for (n=1; n<=nSlices; n++) {
 setSlice(n);
rescaleSlope = getInfo("0028,1053");
run("Multiply...", "value=rescaleSlope slice");
//print(rescaleSlope);
 }

startHour = parseInt(substring(getInfo("0008,0031"),1,3));
startMinute = parseInt(substring(getInfo("0008,0031"),3,5));
injHour = parseInt(substring(getInfo("0018,1072"),1,3));
injMinute = parseInt(substring(getInfo("0018,1072"),3,5));

deltaHour = startHour-injHour;
deltaMinute = startMinute-injMinute;
if(deltaMinute<0)
{
deltaMinute = 60 + deltaMinute;
deltaHour = deltaHour -1;
}
//18F
decayFactor = exp(-log(2)*(60*deltaHour+deltaMinute)/109.8);
//68Ga
//decayFactor = exp(-log(2)*(60*deltaHour+deltaMinute)/67.71);
correctedActivity = decayFactor*getInfo("0018,1074");

if(getInfo("0010,1030")== "" || parseInt(getInfo("0010,1030"))==0)
{
        Dialog.create("Enter the patient mass");
        Dialog.addNumber("Mass (kg):", 75);
        Dialog.show();
        mass = Dialog.getNumber();
        suvFactor = (mass*1000)/(correctedActivity);
        }
        else
        {
suvFactor = (parseFloat(getInfo("0010,1030"))*1000)/correctedActivity;
        }
}
Dialog.create("Radio Buttons");
  items = newArray("Calculate the SUV scale factor only", "Calculate the SUV scale factor and modify the image");
  Dialog.addRadioButtonGroup("Your choice?", items, 1, 2, "Calculate the SUV scale factor only");
Dialog.show;
if(Dialog.getRadioButton=="Calculate the SUV scale factor only")
{

print("SUV factor:\n",suvFactor);

}
else
{
        for (n=1; n<=nSlices; n++) {
 setSlice(n);
run("Multiply...", "value=suvFactor slice");
}
