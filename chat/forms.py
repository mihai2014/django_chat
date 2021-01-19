from django import forms


GROUPS =(
    ("1", "One"), 
    ("2", "Two"), 
    ("3", "Three"), 
    ("4", "Four"), 
    ("5", "Five"),     
)

def get_my_choices():
    return GROUPS

class SelectGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SelectGroupForm, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ChoiceField(
            choices=get_my_choices() )    
    group = forms.ChoiceField(label="Select group")
    #group = forms.ChoiceField(choices = GROUPS, label="Select group")