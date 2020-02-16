import inspect
from pathlib import Path

from kts.core import ui
from kts.settings import cfg
from kts.core.runtime import ray, create_address_manager, get_address_manager

def find_scope():
    frame = inspect.currentframe()
    while frame is not None and 'get_ipython' not in frame.f_globals:
        frame = frame.f_back
    if frame is not None:
        return frame.f_globals
    else:
        return None

def find_config():
    p = Path('.').cwd()
    while p != p.parent and not (p / 'kts_config.toml').exists():
        p = p.parent
    config_path = (p / 'kts_config.toml')
    if config_path.exists():
        return config_path
    else:
        return None

def init():
    global address_manager
    cfg.scope = find_scope()
    config_path = find_config()
    if config_path is not None:
        cfg.load(config_path)
    ui.init()
    ray.init(ignore_reinit_error=True)
    try:
        address_manager = get_address_manager()
    except:
        address_manager = create_address_manager()
