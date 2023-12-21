"""Calculates total Plumb Fixtures requiered per Occupancy Type and Area, according to California Plumbing Code.
INSTITUTIONAL AND RESIDENTIAL OCCUPANCY TYPES ARE NOT INCLUDED

Author Agustina Aboy @ https://twitter.com/agusaboy """
__author__ = 'Agustina Aboy'
__helpurl__ = "https://github.com/agusaboy/BIMstash"


#IMPORTS ---------------------------------------------------------------------------------------------

# these commands get executed in the current scope
# of each new shell (but not for canned commands)
import clr
clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('AdWindows')
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName('System')
clr.AddReferenceByPartialName('System.Windows.Forms')

from Autodesk.Revit import DB
from Autodesk.Revit import UI
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms
from pyrevit import revit

import math
import os


# creates variables for selected elements in global scope
# e1, e2, ...
max_elements = 1
gdict = globals()
uiapp = __revit__
uidoc = uiapp.ActiveUIDocument
if uidoc:
    doc = uiapp.ActiveUIDocument.Document
    selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
    for idx, el in enumerate(selection):
        if idx < max_elements:
            gdict['e{}'.format(idx+1)] = el
        else:
            break

def alert_exit(msg):
	forms.alert(msg,exitscript=True)

	
#USER INPUT DIALOGS---------------------------------------------------------------------------------------------


#select Annotfamily
sel_annot = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
if sel_annot==[]:
	alert_exit('You must select the Table Family first')

#Set occupancy types window
occtypes = [ "A-1","A-2","A-3","A-4","A-5","B","E","F1","F2","M","S-1","S-2"]
sel_occtype = forms.SelectFromList.show(occtypes, button_name='Select Occupancy Type')

#area
area = forms.ask_for_string(
    default='1000',
    prompt='Enter area for selected occupancy type:',
    title='Input Area'
)
sel_area = int(area)


#row number
row_numbers = [1,2,3,4]
sel_row_num = forms.CommandSwitchWindow.show(
    row_numbers,
     message='Select Row:',)



#selecting Code year and tables to be applied
OLF = None

code_year = forms.CommandSwitchWindow.show(
    ['2019', '2022'],
     message='Select CPC year:',)
if code_year == '2019':
    code_OLFtable_options = ['CBC Egress', 'CPC 422.1 TABLE A','CPC 422.1 TABLE 4-1']
elif code_year == '2022':
	code_OLFtable_options = ['User Manual Input']
code_OLtable = forms.CommandSwitchWindow.show(
	code_OLFtable_options,
     message='Select what table to be used for Occupancy Load per Type:',)

#''' #OVERRIDE FOR TESTING PURPOSES !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

print ("Inputs:",sel_occtype, sel_area,sel_row_num)
print ('California code selected',code_year, code_OLtable)


#PLUMBING CODE DATA ---------------------------------------------------------------------------------------------

script_path = os.path.realpath(__file__) 

#CODES 2019
cpc_2019 = script_path.replace('script.py', 'PFcalcs - CPC2019_table 422.1_formated.csv')
CBCegress19_path =  script_path.replace('script.py','.csv')
CPC19_4221_tableA_path =  script_path.replace('script.py','PFcalcs - CPC2019_OLFperOccType_422.1 TABLE A.csv')
CPC19_4221_table41_path =  script_path.replace('script.py','.csv')

#CODES 2022
cpc_2022 = script_path.replace('script.py', 'PFcalcs - CPC2022_table 422.1_formated.csv')


#Codes pick per user input
if code_year=='2019':
	cpc_filepath = cpc_2019
	if code_OLtable == 'CBC Egress':
		OLFpertype_filepath = CBCegress19_path
	elif code_OLtable == 'CPC 422.1 TABLE A':
		OLFpertype_filepath = CPC19_4221_tableA_path
	elif code_OLtable == 'CPC 422.1 TABLE 4-1':
		OLFpertype_filepath = CPC19_4221_table41_path
	else:
		alert_exit('Code not correctly Selected')
elif code_year=='2022':
	cpc_filepath = cpc_2022
	code_OLtable == 'User Manual Input'
	OLFpertype_filepath = 'empty'
	user_olf = forms.ask_for_string(
		default='00',
		prompt='Enter OLF for selected occupancy type:',
		title='USER INPUT_Occ. Load Factor per Occ. Type'
	)
	OLF = int(user_olf)

if OLFpertype_filepath != 'empty':
	OLFpertype_db = open(OLFpertype_filepath, "r")
	OLFpertype_db_to_string = OLFpertype_db.read()
	OLFpertype_list = OLFpertype_db_to_string.splitlines(False)
	OLFpertype_list.pop(0) #REMOVES HEADERS
else:
	pass

#CODE TABLE FOR PF QUANTITIES PER OCC. TYPE
cpc_db = open(cpc_filepath, "r")
cpc_to_string = cpc_db.read()
cpc_list = cpc_to_string.splitlines(False)
cpc_list.pop(0)

#OCCUPANCY CALCS ------------------------------------------------------------------------------------------------------------------------------

#Calculate OLF per Occ. Type CPC 422.1 TABLE A [DSA-SS & DSA-SS/CC]
if OLF==None:
	for o in OLFpertype_list:
		OLF_split = o.split(",")
		occ = OLF_split[0]
		OLFpertype = OLF_split[1]
		if occ == sel_occtype:
			OLF = int(OLFpertype)
else:
	pass
print ('OLF',OLF)

#OCCUPANCY LOAD
OL = round((sel_area)/float(OLF),2)
if OL < 1:
	alert_exit('Ocuppancy Load is lower than 1 person')
OLf = round(OL/2,2)
OLm = round(OL/2,2)
print ("OL",OL,"OLf",OLf,"OLm",OLm)


#USER INPUT on FAMILY ------------------------------------------------------------------------------------------------------------------------------

def	occup_on_rows (sel_row):
	row_occup = "R"+str(sel_row)+"_OccType"
	return row_occup

def	olf_on_rows (sel_row):
	row_olf = "R"+str(sel_row)+"_OLF"
	return row_olf

def	area_on_rows (sel_row):
	row_area = "R"+str(sel_row)+"_AREA"
	return row_area

#TRANSACTIONS (set user inputs on family parameters)

t = Transaction(doc,"Fill Rows with Input")
t.Start()
for annot in sel_annot:
		input_occtype = annot.LookupParameter(occup_on_rows(sel_row_num)).Set(sel_occtype)
		input_olf = annot.LookupParameter(olf_on_rows(sel_row_num)).Set(OLF)
		input_area = annot.LookupParameter(area_on_rows(sel_row_num)).Set(sel_area)
t.Commit()

#--------------------------------------------------------------------------------------------
#DEFINITION PF CODE CALC FORMULA PER CPC
def code_calc (totalOL,belowFx,aboveFx,belowOL,aboveOL):
	calc = float(belowFx +(totalOL-belowOL)*(aboveFx-belowFx)/(aboveOL-belowOL))
	return round(calc,2)

#last_merged_dict = {}
#pf_range = []
#pf_dict = {}	

#DEFINITION CPC CALC PER PF

def code_to_dict(occtype,PF_selected):
	merged_dict = {}
	for l in cpc_list:
		split_commas = l.split(",")
		occ = split_commas[0]
		pf = split_commas[1]
		pf_qty = int(split_commas[2])
		range_lower = int(split_commas[3])
		range_upper = int(split_commas[4])
		if occ == occtype and pf==PF_selected and pf!='ss':
			pf_dict = {pf_qty:(range_lower, range_upper)}
			merged_dict.update(pf_dict)
		sorted_dict = dict(sorted(merged_dict.items()))
		last_merged_dict = merged_dict.copy()
	return sorted_dict


def pf_ranges(PF_selected, olgender):
	pf_dictionary = code_to_dict(sel_occtype, PF_selected)
	print("pf_dictionary",PF_selected,pf_dictionary)
	keys = pf_dictionary.keys()
	values = pf_dictionary.values()
	max_index = len(keys) - 1
	# print('max_index',max_index)
	for v in values:
		i = values.index(v)
		b_ol = v[0]
		# b_ol = v[0]-1
		a_ol = v[1]
		above_fx = keys[i]
		below_fx = keys[i-1]
		if b_ol <= olgender <= a_ol:
			if i==0:
				calc = code_calc(olgender,0,above_fx,0,a_ol)
				print ("calc result",PF_selected,'bottom range',olgender,0,above_fx,0,a_ol)
				return calc
			elif 0<i<max_index:
				calc = code_calc(olgender,below_fx,above_fx,b_ol,a_ol)
				print ("calc result",PF_selected,'middle range',olgender,below_fx,above_fx,b_ol,a_ol)
				return calc
			elif i==max_index:
				calc = below_fx +(olgender-b_ol)/a_ol
				print ("calc result",PF_selected,'above range',olgender,below_fx,b_ol,a_ol)
				return calc
		elif i==max_index and i!=0:
			calc = below_fx +(olgender-b_ol)/a_ol
			print ("calc result",PF_selected,'above range',olgender,below_fx,b_ol,a_ol)
			return calc
		elif max_index==0: #elif i==max_index and i==0:
			calc = olgender/a_ol
			print ("calc result",PF_selected,'single value',olgender,0,0,0,a_ol)
			return calc
	return "error"

#PF CALCS INPUT TO FAMILY--------------------------------------------------------------------------------------------

# SET CALC ON FAMILY
def	pf_on_rows (sel_row,PF_selected):
	pfs = {"wcm":"_M WC","wcf":"_F WC","ur":"_URINAL","lvm":"_M LAV.","lvf":"_F LAV.","df":"_DF","ss":"_SS"}
	keys = pfs.keys()
	#print("keys",keys)
	values = pfs.values()
	#print("values",values)
	for k in keys:
		i = keys.index(k)
		if k==PF_selected:
			descriptor = values[i]
			row = "R"+str(sel_row)+ descriptor
	return row


#CALC OUPUTS & TRANSACTIONS
print('------------------')
wcm = pf_ranges('wcm',OLm)
print('wcm value',wcm)
print('------------------')
wcf = pf_ranges('wcf',OLf)
print('wcf value',wcf)
print('------------------')
urinal = pf_ranges('ur',OLm)
print('ur value',urinal)
print('------------------')
lvm = pf_ranges('lvm',OLm)
print('lvm value',lvm)
print('------------------')
lvf = pf_ranges('lvf',OLf)
print('lvf value',lvf)
print('------------------')
df = pf_ranges('df',OL)
print('df value',df)
print('------------------')

#TRANSACTION
t = Transaction(doc,"Fill row values")
t.Start()
for annot in sel_annot:
		input_wcm = annot.LookupParameter(pf_on_rows(sel_row_num,'wcm')).Set(wcm)
		input_wcf = annot.LookupParameter(pf_on_rows(sel_row_num,"wcf")).Set(wcf)
		input_ur = annot.LookupParameter(pf_on_rows(sel_row_num,"ur")).Set(urinal)
		input_lvm = annot.LookupParameter(pf_on_rows(sel_row_num,"lvm")).Set(lvm)
		input_lvf = annot.LookupParameter(pf_on_rows(sel_row_num,"lvf")).Set(lvf)
		input_df = annot.LookupParameter(pf_on_rows(sel_row_num,"df")).Set(df)
		input_ss = annot.LookupParameter(pf_on_rows(sel_row_num,"ss")).Set(1.00)
t.Commit()

#TA-DAAA! ALL DONE ;) --------------------------------------------------------------------------------------------


