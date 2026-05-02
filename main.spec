# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

spec_root = SPECPATH

datas = []
binaries = []
hiddenimports = ['onnxruntime', 'onnxruntime.capi', 'onnxruntime.capi.onnxruntime_pybind11_state']

# customtkinter — resolve path dynamically instead of hardcoding
import customtkinter
datas.append((os.path.dirname(customtkinter.__file__), 'customtkinter'))

# Project JS files (executed at runtime via execjs)
datas.append((os.path.join(spec_root, 'course.js'), '.'))
datas.append((os.path.join(spec_root, 'app.js'), '.'))

# node_modules (crypto-js required by course.js and app.js)
datas.append((os.path.join(spec_root, 'node_modules'), 'node_modules'))

# ffprobe.exe (used by video_helper.py to get MP4 durations)
binaries.append((os.path.join(spec_root, 'ffmpeg', 'bin', 'ffprobe.exe'), 'ffmpeg/bin/'))

# collect onnxruntime — also copy DLLs to _internal root so Windows can find them
import onnxruntime
onnx_capi_dir = os.path.join(os.path.dirname(onnxruntime.__file__), 'capi')
binaries.append((os.path.join(onnx_capi_dir, 'onnxruntime.dll'), '.'))
binaries.append((os.path.join(onnx_capi_dir, 'onnxruntime_providers_shared.dll'), '.'))
tmp_ret = collect_all('onnxruntime')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# collect ddddocr
tmp_ret = collect_all('ddddocr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(spec_root, 'rthook_onnxruntime.py')],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='rsjapp-mianyang',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='rsjapp-mianyang',
)
