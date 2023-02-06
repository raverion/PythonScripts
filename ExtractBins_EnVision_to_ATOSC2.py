import os, os.path

Bin_Names = []
SW_Bin_Nums = []
PF_Results = []
BinMap = []
bin_vrad = []




#-- Parse bins .evo file  -------------------------------------------------------
evo_files = [f for f in os.listdir('.') if f.endswith('.evo')]
if len(evo_files) > 1:
    raise ValueError('There are multiple .evo files!')
elif len(evo_files) < 1:
	raise ValueError('No .evo file found!')

with open(evo_files[0], "r") as theFile:
    contents_of_theFile = theFile.read().splitlines()  
#--------------------------------------------------------------------------------



#-- Get number of devices from user ---------------------------------------------
while True:
    try:
        num_devices = int(input("Enter number of devices in VRAD Device Map (1-99): "))
        if num_devices < 1 or num_devices > 99:
            raise ValueError
    except ValueError:  # do not accept input if string or not within limits
        print("Nope")
        continue
    else:
        break
#--------------------------------------------------------------------------------



#-- Extract bin names, software bin numbers, and bin result (pass/fail) ---------
for strline_in_theFile in contents_of_theFile:

    Bin_Block = [] # list of strings in the individual Bin definition

    if "Bin_" in strline_in_theFile:
        bin_name = strline_in_theFile[5:-2]
        Bin_Names.append(bin_name)

        # extract bin definition
        block_begin_idx = contents_of_theFile.index(strline_in_theFile)
        block_end_idx = block_begin_idx + 5
        Bin_Block = contents_of_theFile[block_begin_idx:block_end_idx]
        Bin_Block_str = ''.join(Bin_Block)

        # extract sw bin number to populate list of sw bins with
        sw_bin_num = '0' # If bin is not an actual bin, i.e. 'Number' is not defined, pad '0' to sw bins list
        pf = "Fail"
        for bin_property in Bin_Block:
            if "Number" in bin_property:
                sw_bin_num = bin_property[13:-1] # slice from 13th character to 2nd-to-the-last character
            if "Result" in bin_property:
                pf_result = bin_property[13:-1] # slice from 13th character to 2nd-to-the-last character
                if pf_result == 'False':
                    pf = "Fail"
                elif pf_result == 'True':
                    pf = "Pass"
                break
        SW_Bin_Nums.append(sw_bin_num)
        PF_Results.append(pf)
# -------------------------------------------------------------------------------



#-- Extract HW bin numbers from BinMap definition -------------------------------
hwbin_def_begin_idx = contents_of_theFile.index("BinMap Bins_Nominal {") + 1 # Plus 1, to exclude the definition header
hwbin_def_end_idx = hwbin_def_begin_idx + len(Bin_Names)
HW_Bin_Definition = contents_of_theFile[hwbin_def_begin_idx:hwbin_def_end_idx]
#--------------------------------------------------------------------------------



#-- Populate HW bin number list according to matching Bin Name ------------------
HW_Bin_Nums = [0]*len(Bin_Names) # Create empty list
for hw_bin_str in HW_Bin_Definition:
   hw_bin_name = hw_bin_str[8:-5] # slice from 8th character (indention + 'Bin ') to 6th-to-the-last character
   hw_bin_num = hw_bin_str[-2] # slice the 2nd-to-the-last character, which is the hw bin number
   bin_index = Bin_Names.index(hw_bin_name)
   HW_Bin_Nums[bin_index] = hw_bin_num
#--------------------------------------------------------------------------------



#-- Do some verifications first -------------------------------------------------
if len(Bin_Names)!=len(SW_Bin_Nums)!=len(HW_Bin_Nums)!=len(PF_Results):
    raise ValueError("Parsing problem. Please check bin file formatting")


#-- Build VRAD bins.txt file ----------------------------------------------------


VRAD_BINS = []
VRAD_BINS.append("1.00;"+str(len(Bin_Names))+";") # header
VRAD_BINS.append("System Error;0;0;Error;;;;"+("1"*num_devices)+";")
VRAD_BINS.append("Fail;2;2;Fail;;;;"+("1"*num_devices)+";")

for idx in range(0, len(Bin_Names)-1):
    VRAD_BINS.append(Bin_Names[idx]+";"+SW_Bin_Nums[idx]+";"+HW_Bin_Nums[idx]+";"+PF_Results[idx]+";;;;"+("1"*num_devices)+";")

VRAD_BINS_TXT = "\n".join(VRAD_BINS)

f = open("Bins.txt", 'w')
f.write(VRAD_BINS_TXT)
f.close()
