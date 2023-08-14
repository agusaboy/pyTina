"""Select multiple Views/Sheets on Project Browser and Open all at once

Author Agustina Aboy @ https://twitter.com/agusaboy """
__author__ = 'Agustina Aboy'


#IMPORTS ---------------------------------------------------------------------------------------------
from pyrevit import forms, revit

# these commands get executed in the current scope
# of each new shell (but not for canned commands)
import clr
# clr.AddReferenceByPartialName('PresentationCore')
# clr.AddReferenceByPartialName('AdWindows')
# clr.AddReferenceByPartialName("PresentationFramework")
# clr.AddReferenceByPartialName('System')
# clr.AddReferenceByPartialName('System.Windows.Forms')

from Autodesk.Revit import DB



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




#INPUTS ---------------------------------------------------------------------------------------------


selected_views =  [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
count = 0

# # Opens views
if len(selected_views) > 0 and isinstance(selected_views[0], DB.View):
    print("OPENED VIEWS\n")
    for v in selected_views:
         count += 1
         v_name = v.Name
         v_id = v.Id
         view = revit.doc.GetElement(v_id)
         revit.uidoc.ActiveView = view
         print(v_name)
    print("Total views opened: {}".format(count))

else:
    forms.alert('Select a Views first')
