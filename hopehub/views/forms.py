from django import forms
from ..models import JournalEntry

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        # Including all fields from your model, plus the new image field!
        fields = ['text', 'emotion', 'mood_rating', 'tags', 'categories', 'image']
        
        widgets = {
            # Modern textarea configuration
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Start typing your entry here...'
            }),
            
            # Converts the text field into a clean dropdown menu using your Model's choices
            'emotion': forms.Select(attrs={
                'class': 'form-control custom-select'
            }),
            
            # Converts the number field into a clean dropdown menu using your Model's choices
            'mood_rating': forms.Select(attrs={
                'class': 'form-control custom-select'
            }),
            
            # Multi-select dropdown windows for relations
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            
            # File picker for your image upload field
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            })
        }
