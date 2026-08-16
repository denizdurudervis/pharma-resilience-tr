"""
Interface only. The validated TÜİK A64 core must remain frozen.

Rules:
- domestic Leontief inverse remains L_D = (I - A_D)^(-1)
- import-use constraints are not folded into A_D before inversion
- macro shocks are scenario analyses unless an external probability law exists
- this module must not infer product-level component availability from sector totals
  without an explicit allocation/mapping assumption.
"""


def assert_macro_inputs(ad_shape, am_shape=None):
    if ad_shape[0] != ad_shape[1]:
        raise ValueError("A_D must be square")
    if am_shape is not None and am_shape[1] != ad_shape[1]:
        raise ValueError("A_M must align with domestic production sectors")
    return True
