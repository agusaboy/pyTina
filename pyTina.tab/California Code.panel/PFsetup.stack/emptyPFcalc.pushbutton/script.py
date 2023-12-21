"""Empty Annotation Family for Plumb Fixtures

Author Agustina Aboy @ https://twitter.com/agusaboy """
__author__ = 'Agustina Aboy'
__helpurl__ = "https://github.com/archsourcing/plumbing-fixture-calcs"


#IMPORTS ---------------------------------------------------------------------------------------------
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


def alert_exit(msg):
	forms.alert(msg,exitscript=True)


#INPUTS ---------------------------------------------------------------------------------------------

#select Annotfamily
sel_annot = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
if sel_annot==[]:
	alert_exit('You must select the Table Family first')


#row number
row_numbers = [1,2,3,4,"ALL"]
#sel_row_num = forms.SelectFromList.show(row_numbers, button_name='Select Row')
INPUT_row_num = forms.CommandSwitchWindow.show(
    row_numbers,
     message='Select Row:',)

if INPUT_row_num == "ALL":
	sel_row_num = [1,2,3,4]
else:
	sel_row_num = INPUT_row_num

#CALCS ------------------------------------------------------------------------------------------------------------------------------

#Calculate OLF per Occ. Type CPC 422.1 TABLE A [DSA-SS & DSA-SS/CC]
OLF = None


#INPUT on FAMILY ------------------------------------------------------------------------------------------------------------------------------

def	occup_on_rows (sel_row):
	row_occup = "R"+str(sel_row)+"_OccType"
	print(row_occup)
	return row_occup

def	olf_on_rows (sel_row):
	row_olf = "R"+str(sel_row)+"_OLF"
	print(row_olf)
	return row_olf

def	area_on_rows (sel_row):
	row_area = "R"+str(sel_row)+"_AREA"
	print(row_area)
	return row_area


def	pf_on_rows (sel_row,PF_selected):
	pfs = {"wcm":"_M WC","wcf":"_F WC","ur":"_URINAL","lvm":"_M LAV.","lvf":"_F LAV.","df":"_DF","ss":"_SS"}
	keys = pfs.keys()
	values = pfs.values()
	for k in keys:
		i = keys.index(k)
		if k==PF_selected:
			descriptor = values[i]
			row = "R"+str(sel_row)+ descriptor
	return row

t = Transaction(doc,"Fill Rows with Input")
t.Start()

for r in sel_row_num:
	for annot in sel_annot:
			input_occtype = annot.LookupParameter(occup_on_rows(r)).Set(" ")
			input_olf = annot.LookupParameter(olf_on_rows(r)).Set(0)
			input_area = annot.LookupParameter(area_on_rows(r)).Set(0)
			input_wcm = annot.LookupParameter(pf_on_rows(r,'wcm')).Set(0)
			input_wcf = annot.LookupParameter(pf_on_rows(r,"wcf")).Set(0)
			input_ur = annot.LookupParameter(pf_on_rows(r,"ur")).Set(0)
			input_lvm = annot.LookupParameter(pf_on_rows(r,"lvm")).Set(0)
			input_lvf = annot.LookupParameter(pf_on_rows(r,"lvf")).Set(0)
			input_df = annot.LookupParameter(pf_on_rows(r,"df")).Set(0)
			input_ss = annot.LookupParameter(pf_on_rows(r,"ss")).Set(0)
t.Commit()
