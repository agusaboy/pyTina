#pylint: disable=E0401,C0103
from pyrevit import revit
from pyrevit import forms
from pyrevit import script
from Autodesk.Revit.DB import ElementCategoryFilter, ElementClassFilter, LogicalAndFilter, FilteredElementCollector, ElementCategoryFilter, BuiltInCategory, ElementId


logger = script.get_logger()

class SubCategoryOption(forms.TemplateListItem):
    def __init__(self, subcategory):
        super(SubCategoryOption, self).__init__(subcategory)

    @property
    def name(self):
        return '{} --> {}'.format(self.item.Parent.Name, self.item.Name)
    

# DEFINITIONS -------------------------------------------------------------------------------------

def get_elements_by_subcategory(subcategory_name):
    # Get the category of the desired subcategory
    category = None
    categories = revit.doc.Settings.Categories
    for cat in categories:
        if cat.SubCategories.Size > 0:
            for subcat in cat.SubCategories:
                if subcat.Name == subcategory_name:
                    category = subcat
    if category:
        # Filter elements by category
        collector = FilteredElementCollector(revit.doc)
        filter = ElementCategoryFilter(category.Id)
        elements = collector.WherePasses(filter).ToElements()
        return elements
    else:
        print("Subcategory '{}' not found.".format(subcategory_name))

def get_detail_item_subcategories():
    detail_item_subcategories = []
    categories = revit.doc.Settings.Categories
    for cat in categories:
        if cat.SubCategories.Size > 0 and cat.Name == "Detail Items":
            for subcat in cat.SubCategories:
                detail_item_subcategories.append(subcat)
    return detail_item_subcategories

def replace_subcategory(elements, new_subcategory_name):
    new_subcategory = None
    detail_item_subcategories = get_detail_item_subcategories()
    for subcategory in detail_item_subcategories:
        if subcategory.Name == new_subcategory_name:
            new_subcategory = subcategory
            break

    if new_subcategory:
        with revit.Transaction('Replace Subcategories'):
            for element in elements:
                element.Category = new_subcategory.Parent
    else:
        print("New subcategory '{}' not found in 'Detail Items' category.".format(new_subcategory_name))

# USER INTERFACE -------------------------------------------------------------------------------------
if forms.alert('This tool is very destructive. It resets all '
               'the element subcategories (what is shown in Object Styles '
               'panel) inside this model, effectively resetting all line '
               'styles and all other subcategories of any families imported '
               'in the model. Proceed only if you know what you are doing!\n\n'
               'Are you sure you want to proceed?', yes=True, no=True):

    detail_item_subcategories = get_detail_item_subcategories()
  
    subcats_to_delete = forms.SelectFromList.show(
        [SubCategoryOption(x) for x in detail_item_subcategories],
        title='Select SubCategories to Purge',
        button_name='Purge',
        multiselect=True,
        checked_only=True
    )
    
    subcat_to_replace = forms.SelectFromList.show(
        [SubCategoryOption(x) for x in detail_item_subcategories if x not in subcats_to_delete],
        title='Select SubCategory to Replace purged Subcategories',
        button_name='Replace',
        multiselect=False,
        checked_only=True
    )

    if subcats_to_delete and subcat_to_replace:
        for subcategory in subcats_to_delete:
            with revit.Transaction('Merge/Replace SubCategories'):
                elements_to_replace = get_elements_by_subcategory(subcategory.Name)
                replace_subcategory(elements_to_replace, subcat_to_replace.Name)
                
                # Delete the original subcategory
                revit.delete.delete_elements(subcategory)
        
        forms.alert('Subcategories merged/replaced successfully!')
