import os
import sys


if getattr(sys, 'frozen', False):
    # Add onnxruntime/capi to DLL search path so onnxruntime_pybind11_state.pyd can find onnxruntime.dll
    onnx_dir = os.path.join(sys._MEIPASS, 'onnxruntime', 'capi')
    if os.path.isdir(onnx_dir):
        os.add_dll_directory(onnx_dir)
