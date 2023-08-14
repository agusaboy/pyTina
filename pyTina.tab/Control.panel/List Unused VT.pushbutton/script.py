"""List Unused View Templates

Author Agustina Aboy @ https://twitter.com/agusaboy """
__author__ = 'Agustina Aboy'


from telnetlib import PRAGMA_HEARTBEAT
from pyrevit import forms
from pyrevit import revit, DB


viewlist = DB.FilteredElementCollector(revit.doc)\
             .OfClass(DB.View)\
             .WhereElementIsNotElementType()\
             .ToElements()


vtemp = set()
usedvtemp = set()
views = []

for v in viewlist:
    if v.IsTemplate and 'master' not in revit.query.get_name(v).lower():
        vtemp.add(v.Id.IntegerValue)
    else:
        views.append(v)

for v in views:
    vtid = v.ViewTemplateId.IntegerValue
    if vtid > 0:
        usedvtemp.add(vtid)

unusedvtemp = vtemp - usedvtemp

if not unusedvtemp:
    forms.alert("All View Templates are in use.")
else:
    # ask user for wipe actions
    print("UNUSED VIEW TEMPALTES")
    print("\n ")
    for x in unusedvtemp:
        vt_list = revit.doc.GetElement(DB.ElementId(x)).Name
        print(vt_list)