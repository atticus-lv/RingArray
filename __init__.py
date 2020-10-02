# -*- coding =utf-8 -*-
# 灵感来源 卯月的小插件 url: https://space.bilibili.com/29298335


bl_info = {
    "name": "Ring Array",
    "author": "Atticus",
    "description": "允许阵列任意物体的插件",
    "blender": (2, 83, 2),
    "version": (0, 0, 6),
    "location": "Side Menu -> Edit",
    "warning": "",
    "wiki_url": "https://github.com/atticus-lv/RingArray",
    "category": "Object"
}

import importlib
import base64
import sys


def license():
    """UGFuZWwgT3BlcmF0b3Jz"""
    __dict__ = {}
    modules = base64.b64decode(license.__doc__).decode("utf-8").split()

    for module in modules:
        __dict__[module] = (f'{module}') if 'DEBUG_MODE' in sys.argv else (f'{__name__}.{module}')
    # 动态加载
    for name in __dict__.values():
        if name in sys.modules:
            importlib.reload(sys.modules[name])
        else:
            globals()[name] = importlib.import_module(name)
            setattr(globals()[name], 'SSM_modules', __dict__)
    return __dict__


module_name = license()


def register():
    for name in module_name.values():
        if name in sys.modules:
            if hasattr(sys.modules[name], 'register'):
                sys.modules[name].register()


def unregister():
    for name in module_name.values():
        if name in sys.modules:
            if hasattr(sys.modules[name], 'unregister'):
                sys.modules[name].unregister()


if __name__ == '__main__':
    register()
