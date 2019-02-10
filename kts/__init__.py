import sys

if not sys.argv[0]:
    from .cli.file_system import check_file_system
    check_file_system()
    from .feature.decorators import preview, register, deregister, dropper, selector
    from .feature.stl import *
    from .feature import stl
    from .feature.storage import feature_list as features
    from .validation.experiment import experiment_list as experiments
