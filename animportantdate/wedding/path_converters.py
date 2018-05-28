from .fields import PnrField

class PnrConverter:
    regex = '[A-Za-z0-9]{6}'
    
    def to_python(self, value):
        return PnrField.clean_pnr(value)
    
    def to_url(self, value):
        return value
