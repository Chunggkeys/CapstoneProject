# CommunicationSystem

## Measurement Module

The Measurement Module contains the code for reading the ADC values and returning the resistances, and temperature values to the manager module. The configurations of the ADC's can be changed in the initialisation1 function and can be referenced by section 8.6.1 of the [ADS1220 data sheet](https://www.ti.com/lit/ds/symlink/ads1220.pdf?ts=1620014551609&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FADS1220). read_R uses the Read_Data function to read ADC's 1-4 corresponding to the ADC's used for the sample fibres, and read_T reads ADC5 used for reading the thermocouples. 
