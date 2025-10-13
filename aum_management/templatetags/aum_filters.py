from django import template
from django.template.defaultfilters import register

@register.filter(name='get_dict_value')
def get_dict_value(dictionary, key):
    """
    Looks up a value in a dictionary using a variable key.
    Useful for accessing dict values inside template loops.
    """
    if not isinstance(dictionary, dict):
        # Handle case where the value passed is not a dictionary (e.g., Decimal object)
        # This prevents crashes and allows default logic to execute if needed.
        return None
        
    return dictionary.get(key)