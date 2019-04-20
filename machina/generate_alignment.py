from pathlib import Path
import re

import numpy as np
from Bio.Seq import Seq
from Bio.Alphabet import generic_protein
from Bio.SubsMat import MatrixInfo

from machina.pairwise2 import align

BLOSUM_MODE = 'off'


class _my_match(object):
    def __init__(self, matrix):
        """Initialize the class."""
        self.match = matrix

    def __call__(self, charA, charB, posA, posB):
        """Call a match function instance already created."""
        if BLOSUM_MODE == 'on':
            if (charA, charB) in MatrixInfo.blosum62:
                return self.match[posA][posB] + MatrixInfo.blosum62[(charA, charB)]
            else:
                return self.match[posA][posB] + MatrixInfo.blosum62[(charB, charA)]
        elif BLOSUM_MODE == 'only':
            if (charA, charB) in MatrixInfo.blosum62:
                return MatrixInfo.blosum62[(charA, charB)]
            else:
                return MatrixInfo.blosum62[(charB, charA)]
        else:
            return self.match[posA][posB]


def _pp(path):
    seq = []
    for line in Path(path).read_text().splitlines():
        token = line.rstrip('\r\n').split()
        if len(token) == 0:
            continue
        if re.match(r'\d+', token[0]):
            seq.append(token[1])
    return Seq(''.join(seq), generic_protein)


def alignment_local(score_matrix_path: str, domain_sid1: str, domain_sid2: str,
                    pssm_dir: str, gap_open: float, gap_extend: float):
    seq_a = str(_pp(f'{pssm_dir}/{domain_sid1[2:4]}/{domain_sid1}.mtx'))
    seq_b = str(_pp(f'{pssm_dir}/{domain_sid2[2:4]}/{domain_sid2}.mtx'))
    matrix = np.load(score_matrix_path)
    assert len(seq_a) == matrix.shape[0] and len(seq_b) == matrix.shape[1]
    ali = align.localcs(seq_a, seq_b, _my_match(matrix.tolist()), gap_open, gap_extend, force_generic=True)
    return (domain_sid1, domain_sid2), ali
