import os, os.path
import sys
from array import *
import string


#-- Find and parse .evo limits file  ----------------------------------------------
#----------------------------------------------------------------------------------
dir_list = [d for d in os.listdir('.') if (os.path.isdir(d) and not d.startswith('.'))]

if dir_list.__len__() > 1:
    print("Multiple test programs found. Please select which one to parse:")
    i = 1;
    for d in dir_list:
        print('['+str(i)+'] '+d)
        i = i + 1
    while True:
        try:
            user_sel = int(input("Enter index (1 to " + str(dir_list.__len__()) + "): "))
            if user_sel > dir_list.__len__() or user_sel < 1:
                raise ValueError
        except ValueError:
            print("Nope")
            continue
        else:
            break
    tp_dir = dir_list[user_sel - 1]

elif dir_list.__len__() == 1:
    print("Found " + dir_list[0])
    tp_dir = dir_list[0]

elif dir_list.__len__() == 0:
    print("No tp found. Exiting code")
    sys.exit()

print('\n')

evo_list = [e for e in os.listdir('./'+tp_dir+'/Extrefs') if (e.find('Limit')!=-1 or e.find('limit')!=-1) or e.find('setup')!=-1]
if evo_list.__len__() > 1:
  print("Multiple limits files found. Please select which one to parse:")
  i = 1;
  for e in evo_list:
    print('['+str(i)+'] '+e)
    i = i+1
  while True:
    try:
      user_sel = int(input("Enter index (1 to " + str(evo_list.__len__()) + "): "))
      if user_sel > dir_list.__len__() or user_sel < 1:
        raise ValueError
    except ValueError:
      print("Nope")
      continue
    else:
      break
    
  evo_select = evo_list[user_sel - 1]
  with open('./' + tp_dir + '/Extrefs/'+evo_select, "r") as theFile:
    contents_of_theFile = theFile.read().splitlines()  

elif evo_list.__len__() == 1:
  with open('./' + tp_dir + '/Extrefs/limits.evo', "r") as theFile: #default file if no other limits file
    contents_of_theFile = theFile.read().splitlines()

elif evo_list.__len__() == 0:
  print("No limit file found. Exiting code")
  sys.exit()
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

print('\n')
while True:
    try:
        numDevices = int(input("How many devices are declared in your VRAD?\n"))
        if numDevices < 0:
            raise ValueError
    except:
        print('Nope')
        continue
    else:
        break



#-- Extract parameters ------------------------------------------------------------
#----------------------------------------------------------------------------------
Limits_Spec_Categories = []
Limits_Spec_startIndices = []
Limits_Spec_stopIndices = []

RawMatrix = []
NumberOfParamsPerOption = []

#-- Determine slice indices of each test option / spec category
for n, line in enumerate(contents_of_theFile):
    if "Category" in line:
        Limits_Spec_Categories.append(line[line.find("Category")+9:-2])
        Limits_Spec_startIndices.append(n + 1)
        for m, ln in enumerate(contents_of_theFile[n+1:]):
            if "}" in ln:
                Limits_Spec_stopIndices.append(m + n + 1)
                break

#-- Slice those motherfuckers
for specIdx in range(0, Limits_Spec_Categories.__len__()):
    RawMatrix.append(contents_of_theFile[Limits_Spec_startIndices[specIdx]:Limits_Spec_stopIndices[specIdx]])
     
for spec in RawMatrix:
    NumberOfParamsPerOption.append(spec.__len__())

ParamsMatrix = []
Units = ['ns','us','ms','s','nS','uS','mS','S','nA','uA','mA','A','nV','uV','mV','V','mOhms','Ohms','Ohm','kOhm','MOhm','Cel','Hz','kHz','MHz']
UnitsWithScale = ['ns','us','ms','nS','uS','mS','nA','uA','mA','nV','uV','mV','kOhm','MOhm','kHz','MHz']
for spec in RawMatrix:
    Params = []
    for param in spec:
        param = param.translate({ord(c): None for c in string.whitespace}) # remove all whitespaces
        Properties = [] # 4-element list containing name, value, unit of parameter, scale of unit

        parname_idx = 0
        parname_stopidx = param.find('=')

        parval_idx = param.find('"') + 1
        unit_present = False
        unit_has_scale = False
        for unit in Units:
            unitindex = param.find(unit[-1])
            paramend = param[-3]
            parval_stopidx = -2
            if unit in param and param[-3]==unit[-1]: # if unit is present in the string AND appears at the end of the string before ' "; '
                parval_stopidx = param.find(unit)
                parunit_idx = param.find(unit)
                parunit_stopidx = -2
                unit_present = True
                if unit in UnitsWithScale:
                    unit_has_scale = True
                break

        parname = param[parname_idx:parname_stopidx].replace('.','_')
        if unit_present:
            if unit_has_scale:
                Properties = [parname, param[parval_idx:parval_stopidx], param[parunit_idx:parunit_stopidx-1], param[parunit_idx+1:parunit_stopidx]]
            else:
                Properties = [parname, param[parval_idx:parval_stopidx], '', param[parunit_idx:parunit_stopidx]]
        else:   # param has no unit
            Properties = [parname, param[parval_idx:parval_stopidx], '', '']

        Params.append(Properties)
    ParamsMatrix.append(Params)
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------



#-- Assign binary representation to each category ---------------------------------
#----------------------------------------------------------------------------------
Limits_Spec_Codes = []
for i in range(numDevices, 0, -1):
    Limits_Spec_Codes.append(2**(i-1))
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------



#-- Format the parameters ---------------------------------------------------------
#----------------------------------------------------------------------------------
# compile aggregate uniqe parameters
unique_params = []
for n, category in enumerate(ParamsMatrix):
    for name, val, scale, unit in category:
        if name not in unique_params:
            unique_params.append(name)

# convert parameter matrix to parameter tree. This is needed to collapse parameter values that are the same for two or more categories (NOTE: for now it only collapses equal consecutive values)
param_tree = []
paridx = 0
for par in unique_params:
    param_branch = []
    param_branch.append(par)
    
    value_list = [ [0,0,0,0] ]* numDevices
    val_idx = 0
    for n, category_section in enumerate(ParamsMatrix):
        category_name = Limits_Spec_Categories[n]
        for name, val, scale, unit in category_section:
            entry = []
            if par == name:
                val2 = value_list[val_idx][1]
                if n == 0:
                    entry.append(Limits_Spec_Codes[n])
                    entry.append(val)
                    entry.append(scale)
                    entry.append(unit)
                    value_list[0] = entry
                elif n > 0 and val == value_list[val_idx][1]:   # if val is equal to previous val, do not append another value to the list, but increment the param code
                    value_list[val_idx][0] = value_list[val_idx][0] | Limits_Spec_Codes[n]
                else:
                    entry.append(Limits_Spec_Codes[n])
                    entry.append(val)
                    entry.append(scale)
                    entry.append(unit)
                    value_list[val_idx + 1] = entry
                    val_idx = val_idx + 1
                break
    param_branch.append(value_list)
    param_tree.append(param_branch)
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------



#-- Build the file "Params.txt" ---------------------------------------------------
#----------------------------------------------------------------------------------
VRAD_PARAMS = []
param_count = 0
for name, properties in param_tree:
    for row in properties:
        if int(row[0]):
            
            value = row[1]
            value = value.replace('E', 'e') # for sci notation

            if not row[2]:
                scale = ' ' # append whitespace if unit is V, A, Ohm (i.e. no scale)
            else:
                scale = row[2]

            if not row[3]:
                unit = ' ' # append whitespace if unit is V, A, Ohm (i.e. no scale)
            else:
                unit = row[3]

            enablecode = format(row[0],'0'+str(numDevices)+'b') # converts code to binary string with leading zeroes

            VRAD_PARAMS.append(name+';;'+value+';'+value+';'+scale+unit+';'+enablecode+';')

            param_count = param_count + 1

VRAD_PARAMS.insert(0, '1.00;'+str(param_count)+';')

VRAD_PARAMS_TXT = "\n".join(VRAD_PARAMS)

f = open("Params.txt", 'w')
f.write(VRAD_PARAMS_TXT)
f.close
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

print("DONE.\n")
yes = input("Do you wish to generate Bins.txt from the same test program? Type anything if yes.")
if not yes:
  sys.exit()
#-- Generate Bins.txt


print('\n')

#-- Parse bins .evo file  -------------------------------------------------------
evo_list = [e for e in os.listdir('./'+tp_dir+'/Extrefs') if (e.find('bin')!=-1 or e.find('Bin')!=-1)]
if evo_list.__len__() > 1:
  print("Multiple bin files found. Please select which one to parse:")
  i = 1;
  for e in evo_list:
    print('['+str(i)+'] '+e)
    i = i+1
  while True:
    try:
      user_sel = int(input("Enter index (1 to " + str(evo_list.__len__()) + "): "))
      if user_sel > dir_list.__len__() or user_sel < 1:
        raise ValueError
    except ValueError:
      print("Nope")
      continue
    else:
      break

  evo_select = evo_list[user_sel - 1]
  with open('./' + tp_dir + '/Extrefs/'+evo_select, "r") as theFile:
    contents_of_theFile = theFile.read().splitlines()  

elif evo_list.__len__() == 1:
  with open('./' + tp_dir + '/Extrefs/bins.evo', "r") as theFile: #default file if no other limits file
    contents_of_theFile = theFile.read().splitlines()

elif evo_list.__len__() == 0:
  print("No limit file found. Exiting code")
  sys.exit()
#--------------

Bin_Names = []
SW_Bin_Nums = []
PF_Results = []
BinMap = []
bin_vrad = []

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
VRAD_BINS.append("System Error;0;0;Error;;;;"+("1"*numDevices)+";")
VRAD_BINS.append("Fail;2;2;Fail;;;;"+("1"*numDevices)+";")

for idx in range(0, len(Bin_Names)-1):
    VRAD_BINS.append(Bin_Names[idx]+";"+SW_Bin_Nums[idx]+";"+HW_Bin_Nums[idx]+";"+PF_Results[idx]+";;;;"+("1"*numDevices)+";")

VRAD_BINS_TXT = "\n".join(VRAD_BINS)

f = open("Bins.txt", 'w')
f.write(VRAD_BINS_TXT)
f.close()