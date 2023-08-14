"""List and place detail groups in view

The purpose of this script is to: collect all detail groups on a model filtered by name and place them in an orderly fashion in a drafting view.

Author Agustina Aboy @ https://twitter.com/agusaboy """
__author__ = 'Agustina Aboy'

from pyrevit import forms
from pyrevit import revit, DB
from System.Collections.Generic import List
import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *


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

# DEFINITIONS
def alert_exit(msg):
	forms.alert(msg,exitscript=True)


def group_placer_placegroup(point,gtype):

    # Copy the group to the desired location
    placed_groups = doc.Create.PlaceGroup(point,gtype)
    return placed_groups, point


# USER INPUT

name_filter = forms.ask_for_string(
    default='Group',
    prompt='Filter Groups by Name. (Case sensitive)',
    title='Filter Groups by Name'
)

distance = forms.ask_for_string(
    default= '0.5',
    prompt='Distance between groups in feet',
    title='Group Graphic Offset'
)
dist_offset = float(distance)

#VIEW PLACEMENT
active_view = revit.active_view
location = revit.uidoc.Selection.PickPoint()
offset = DB.XYZ(0, -dist_offset, 0)

# LOOK FOR GROUPS
groups = DB.FilteredElementCollector(doc).OfClass(DB.Group).ToElements()
g_count = 0
g_filtered_count = 0

placed_group_names = set()

with revit.Transaction("Place Detail Groups in Active View"):
    for g in groups:
        groups_names = g.Name
        group_type = g.GroupType
        g_count += 1
        # if name_filter in groups_names:
        # if name_filter in groups_names and group_type not in placed_group_types:
        if name_filter in groups_names and groups_names not in placed_group_names:
            g_filtered_count += 1
            print("{}".format(groups_names))
            with revit.Transaction("Place Detail Groups in Active View"):
                location_offset = offset  # Initialize the location_offset
                location_with_offset = location.Add(location_offset)  # Apply the current offset
                placed_groups, location = group_placer_placegroup(location_with_offset,group_type)
                location_offset = location_offset.Add(offset)
                placed_group_names.add(groups_names)  # Add the placed group name to the set
        else:
            pass
    print(" TOTAL FITLER GROUPS:.........{}".format(g_filtered_count))
    print(" TOTAL COUNT OF PLACED GROUPS:.........{}".format(g_count))
     
