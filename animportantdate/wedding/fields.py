from django.db import models
import re
import random

class PnrField(models.CharField):
    alphabet = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
    not_in_alphabet = re.compile(r'[^' + alphabet + ']')

    @staticmethod
    def clean_pnr(dirty_pnr):
        normalized_pnr = dirty_pnr.upper().replace("O", "0").replace("I", "1").replace("L", "1")
        return re.sub(PnrField.not_in_alphabet, '', normalized_pnr)

    @staticmethod
    def make_generator(length):
        return lambda: PnrField.generate(length)

    @staticmethod
    def generate(length):
        return ''.join([random.SystemRandom().choice(PnrField.alphabet) for i in range(length)])
    
    def get_prep_value(self, value):
        return PnrField.clean_pnr(value)
