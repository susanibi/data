import numpy as np

class GravyHelper:
    # Kyte & Doolittle hydropathy index
    hydropathy_index = {
        'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2,
        'U': 0.0
    }

    def __init__(self, name):
        self.name = name  # instance variable

    @staticmethod
    def replace_modification(sequence):
        # Convert C(UniMod:4) to U
        return sequence.replace("C(UniMod:4)", "U")

    @staticmethod
    def calculate_gravy(sequence):
        sequence = GravyHelper.replace_modification(sequence)
        values = [GravyHelper.hydropathy_index.get(aa, 0) for aa in sequence]

        return round(sum(values) / len(values), 2)
