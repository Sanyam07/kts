import os
from typing import Dict

import pandas as pd
import ray
import ray.experimental.signal as rs

from kts.core.backend.progress import ProgressSignal
from kts.core.backend.signals import RunPID
from kts.core.backend.stats import Stats
from kts.core.frame import KTSFrame


@ray.remote(num_return_vals=3, max_retries=0)
def worker(self, *args, df: pd.DataFrame, meta: Dict):
    assert 'run_manager' not in meta
    assert 'report' not in meta
    kf = KTSFrame(df, meta=meta)
    kf.__meta__['remote'] = True
    had_state = bool(kf.state)

    rs.send(ProgressSignal(0, 1, None, None, None))
    rs.send(RunPID(os.getpid()))

    stats = Stats(df)
    with stats, self.remote_io(), self.suppress_stderr():
        res_kf = self.compute(*args, kf)

    if had_state:
        res_state = None
    else:
        res_state = kf._state

    rs.send(ProgressSignal(1, 1, None, None, None))
    return res_kf, res_state, stats.data