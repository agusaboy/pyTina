"""Calculates total Plumb Fixtures needed per Occupancy Type and Area.
INSTITUTIONAL AND RESIDENTIAL OCCUPANCY TYPES NOT INCLUDED

Author Agustina Aboy @ https://twitter.com/agusaboy """
__author__ = 'Agustina Aboy'
__helpurl__ = "https://github.com/archsourcing/plumbing-fixture-calcs"


#IMPORTS ---------------------------------------------------------------------------------------------
from queue import Empty
from pyrevit import forms

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

import Autodesk.Windows as aw

# creates variables for selected elements in global scope
# e1, e2, ...
max_elements = 5
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

# alert function
def alert(msg):
    TaskDialog.Show('RPS', msg)

# quit function
def quit():
    __window__.Close()


#INPUTS ---------------------------------------------------------------------------------------------

#select Annotfamily
sel_annot = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]

'''filename = forms.ask_for_string(
    default='"C:\Users\USUARIO\Desktop\plmb.xlsx"',
    prompt='Enter file path',
    title='Code Reference File'
)

f = open(filename, "r")
print(f.readline())
f.close()
'''
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
sel_row_num = forms.SelectFromList.show(row_numbers, button_name='Select Row')

print ("Inputs:",sel_occtype, sel_area,sel_row_num)



#CALCS ------------------------------------------------------------------------------------------------------------------------------

#Calculate OLF per Occ. Type CPC 422.1 TABLE A [DSA-SS & DSA-SS/CC]
OLF = None

if sel_occtype=="A-1":
	OLF=15
elif sel_occtype=="A-2":
	OLF=30
elif sel_occtype=="A-3":
	OLF=30
elif sel_occtype=="A-4":
	OLF=30
elif sel_occtype=="A-5":
	OLF=30
elif sel_occtype=="B":
	OLF=200
elif sel_occtype=="E":
	OLF=50
elif sel_occtype=="F1":
	OLF=2000
elif sel_occtype=="F2":
	OLF=2000
elif sel_occtype=="M":
	OLF=200
elif sel_occtype=="S-1":
	OLF=5000
elif sel_occtype=="S-2":
	OLF=5000
else:
	OLF=00

#INPUT on FAMILY ------------------------------------------------------------------------------------------------------------------------------

def	occup_on_rows (sel_row):
	row_occup = "R"+str(sel_row)+"_OccType"
	return row_occup

def	olf_on_rows (sel_row):
	row_olf = "R"+str(sel_row)+"_OLF"
	return row_olf

def	area_on_rows (sel_row):
	row_area = "R"+str(sel_row)+"_AREA"
	return row_area


t = Transaction(doc,"Fill Rows with Input")
t.Start()

for annot in sel_annot:
		input_occtype = annot.LookupParameter(occup_on_rows(sel_row_num)).Set(Empty)
		input_olf = annot.LookupParameter(olf_on_rows(sel_row_num)).Set(0)
		input_area = annot.LookupParameter(area_on_rows(sel_row_num)).Set(0)
t.Commit()

wcm_dict ={"A-1":{1:(1,100),2:(101,200),3:(201,400),10000:(401,'x')}}
#print ("WC Male DICTIONARY",wcm_dict.get("A-1"))