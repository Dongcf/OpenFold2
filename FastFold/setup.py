#######################################
#https://github.com/hpcaitech/FastFold#
#######################################

import os
import subprocess

import torch
from setuptools import setup, find_packages
from torch.utils.cpp_extension import BuildExtension, CUDAExtension, CUDA_HOME
import xml.etree.ElementTree as ET

# ninja build does not work unless include_dirs are abs path
this_dir = os.path.dirname(os.path.abspath(__file__))

def get_gpu_info():
    raw_output = subprocess.check_output(["nvidia-smi", "-q", "-x"], universal_newlines=True)
    xml = ET.fromstring(raw_output)
    datas = []
    driver_version = xml.findall("driver_version")[0].text
    cuda_version = xml.findall("cuda_version")[0].text

    for gpu_id, gpu in enumerate(xml.iter("gpu")):
        gpu_data = {}
        name = [x for x in gpu.iter("product_name")][0].text
        memory_usage = gpu.findall("fb_memory_usage")[0]
        total_memory = memory_usage.findall("total")[0].text

        gpu_data["name"] = name
        gpu_data["total_memory"] = total_memory
        gpu_data["driver_version"] = driver_version
        gpu_data["cuda_version"] = cuda_version
        datas.append(gpu_data)
    return datas


def get_cuda_bare_metal_version(cuda_dir):
    raw_output = subprocess.check_output([cuda_dir + "/bin/nvcc", "-V"], universal_newlines=True)
    output = raw_output.split()
    release_idx = output.index("release") + 1
    release = output[release_idx].split(".")
    bare_metal_major = release[0]
    bare_metal_minor = release[1][0]

    return raw_output, bare_metal_major, bare_metal_minor


def check_cuda_torch_binary_vs_bare_metal(cuda_dir):
    raw_output, bare_metal_major, bare_metal_minor = get_cuda_bare_metal_version(cuda_dir)
    torch_binary_major = torch.version.cuda.split(".")[0]
    torch_binary_minor = torch.version.cuda.split(".")[1]

    print("\nCompiling cuda extensions with")
    print(raw_output + "from " + cuda_dir + "/bin\n")

    if (bare_metal_major != torch_binary_major) or (bare_metal_minor != torch_binary_minor):
        raise RuntimeError(
            "Cuda extensions are being compiled with a version of Cuda that does " +
            "not match the version used to compile Pytorch binaries.  " +
            "Pytorch binaries were compiled with Cuda {}.\n".format(torch.version.cuda) +
            "In some cases, a minor-version mismatch will not cause later errors:  " +
            "https://github.com/NVIDIA/apex/pull/323#discussion_r287021798.  "
            "You can try commenting out this check (at your own risk).")


def append_nvcc_threads(nvcc_extra_args):
    _, bare_metal_major, bare_metal_minor = get_cuda_bare_metal_version(CUDA_HOME)
    if int(bare_metal_major) >= 11 and int(bare_metal_minor) >= 2:
        return nvcc_extra_args + ["--threads", "4"]
    return nvcc_extra_args


if not torch.cuda.is_available():
    # https://github.com/NVIDIA/apex/issues/486
    # Extension builds after https://github.com/pytorch/pytorch/pull/23408 attempt to query torch.cuda.get_device_capability(),
    # which will fail if you are compiling in an environment without visible GPUs (e.g. during an nvidia-docker build command).
    print(
        '\nWarning: Torch did not find available GPUs on this system.\n',
        'If your intention is to cross-compile, this is not an error.\n'
        'By default, FastFold will cross-compile for Pascal (compute capabilities 6.0, 6.1, 6.2),\n'
        'Volta (compute capability 7.0), Turing (compute capability 7.5),\n'
        'and, if the CUDA version is >= 11.0, Ampere (compute capability 8.0).\n'
        'If you wish to cross-compile for a single specific architecture,\n'
        'export TORCH_CUDA_ARCH_LIST="compute capability" before running setup.py.\n')
    if os.environ.get("TORCH_CUDA_ARCH_LIST", None) is None:
        _, bare_metal_major, _ = get_cuda_bare_metal_version(CUDA_HOME)
        if int(bare_metal_major) == 11:
            os.environ["TORCH_CUDA_ARCH_LIST"] = "6.0;6.1;6.2;7.0;7.5;8.0"
        else:
            os.environ["TORCH_CUDA_ARCH_LIST"] = "6.0;6.1;6.2;7.0;7.5"

print("\n\ntorch.__version__  = {}\n\n".format(torch.__version__))
TORCH_MAJOR = int(torch.__version__.split('.')[0])
TORCH_MINOR = int(torch.__version__.split('.')[1])

if TORCH_MAJOR < 1 or (TORCH_MAJOR == 1 and TORCH_MINOR < 10):
    raise RuntimeError("FastFold requires Pytorch 1.10 or newer.\n" +
                       "The latest stable release can be obtained from https://pytorch.org/")

cmdclass = {}
ext_modules = []

# Set up macros for forward/backward compatibility hack around
# https://github.com/pytorch/pytorch/commit/4404762d7dd955383acee92e6f06b48144a0742e
# and
# https://github.com/NVIDIA/apex/issues/456
# https://github.com/pytorch/pytorch/commit/eb7b39e02f7d75c26d8a795ea8c7fd911334da7e#diff-4632522f237f1e4e728cb824300403ac
version_dependent_macros = ['-DVERSION_GE_1_1', '-DVERSION_GE_1_3', '-DVERSION_GE_1_5']

if CUDA_HOME is None:
    raise RuntimeError(
        "Are you sure your environment has nvcc available?  If you're installing within a container from https://hub.docker.com/r/pytorch/pytorch, only images whose names contain 'devel' will provide nvcc."
    )
else:
    check_cuda_torch_binary_vs_bare_metal(CUDA_HOME)

    def cuda_ext_helper(name, sources, extra_cuda_flags):
        return CUDAExtension(
            name=name,
            sources=[
                os.path.join('Kernel/cuda_native/csrc', path) for path in sources
            ],
            include_dirs=[
                os.path.join(this_dir, 'Kernel/cuda_native/csrc/include')
            ],
            extra_compile_args={
                'cxx': ['-O3'] + version_dependent_macros,
                'nvcc':
                    append_nvcc_threads(['-O3', '--use_fast_math'] + version_dependent_macros +
                                        extra_cuda_flags)
            })

    gpu_info = get_gpu_info()
    gen_61 = False
    for gpu in gpu_info:
        if gpu['name'] == 'NVIDIA GeForce GTX 1080':
           gen_61 = True
    if gen_61:
        print('Generating code for 1080\'s')
        cc_flag = ['-gencode', 'arch=compute_61,code=sm_61']
    else:
        print('Generating code for V100\'s')
        cc_flag = ['-gencode', 'arch=compute_70,code=sm_70']

    _, bare_metal_major, _ = get_cuda_bare_metal_version(CUDA_HOME)
    if int(bare_metal_major) >= 11:
        cc_flag.append('-gencode')
        cc_flag.append('arch=compute_72,code=sm_72')
        # cc_flag.append('-gencode')
        # cc_flag.append('arch=compute_80,code=sm_80')
		

    extra_cuda_flags = [
        '-std=c++14', '-maxrregcount=50', '-U__CUDA_NO_HALF_OPERATORS__',
        '-U__CUDA_NO_HALF_CONVERSIONS__', '--expt-relaxed-constexpr', '--expt-extended-lambda'
    ]

    ext_modules.append(
        cuda_ext_helper('fastfold_layer_norm_cuda',
                        ['layer_norm_cuda.cpp', 'layer_norm_cuda_kernel.cu'],
                        extra_cuda_flags + cc_flag))

    ext_modules.append(
        cuda_ext_helper('fastfold_softmax_cuda', ['softmax_cuda.cpp', 'softmax_cuda_kernel.cu'],
                        extra_cuda_flags + cc_flag))

setup(
    name='fastfold',
    version='0.1.0-custom',
    packages=find_packages(exclude=(
        'assets',
        'benchmark',
        '*.egg-info',
    )),
    description= 'Optimizing Protein Structure Prediction Model Training and Inference on GPU Clusters',
    ext_modules=ext_modules,
    package_data={'fastfold': ['Kernel/cuda_native/csrc/*']},
    cmdclass={'build_ext': BuildExtension} if ext_modules else {},
	install_requires=['einops']
)