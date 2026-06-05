# filepath: hopehub/views/forms.py
from django import forms
from hopehub.models import JournalEntry

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        
        # Scope restricted strictly to user-facing input targets
        fields = ['text', 'emotion', 'mood_rating', 'image']
        
        widgets = {
            # Modern textarea configuration
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Start typing your entry here...'
            }),
            
            # Dropdown adapters mapping directly to model choices matrices
            'emotion': forms.Select(attrs={
                'class': 'form-control custom-select'
            }),
            
            'mood_rating': forms.Select(attrs={
                'class': 'form-control custom-select'
            }),
            
            # File picker for multi-part image asset payload integration
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            })
        }
