import argparse
import json
import os
import subprocess
import sys

import torch

import transformerlab.plugin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', type=str)
    parser.add_argument('--adaptor-path', type=str)
    parser.add_argument('--parameters', type=str, default="{}")

    args, unknown = parser.parse_known_args()

    print("Starting Extended FastChat Tools Worker", file=sys.stderr)

    model = args.model_path
    adaptor = args.adaptor_path

    if adaptor != "":
        model = adaptor

    parameters = args.parameters
    parameters = json.loads(parameters)

    if (parameters.get("eight_bit") == 'on'):
        eight_bit = True
    else:
        eight_bit = False

    # Used only if memory on multiple cards is needed. Do not include if this is not not set.
    num_gpus = parameters.get("num_gpus", None)

    # Auto detect backend if device not specified
    device = parameters.get("device", None)
    if device is None or device == "":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
            num_gpus = 0

    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    print("Plugin dir:", plugin_dir)

    popen_args = [
        sys.executable, 
        f"{plugin_dir}/run_server.py",
        '--model-path', model, 
        "--device", device
        ]
    if (num_gpus):
        popen_args.extend(["--num-gpus", num_gpus])
    if (eight_bit):
        popen_args.append("--load-8bit")


    print(popen_args)
    proc = subprocess.Popen(popen_args, stderr=subprocess.PIPE, stdout=None)

    # save worker process id to file
    # this will allow transformer lab to kill it later
    WORKSPACE_DIR = transformerlab.plugin.WORKSPACE_DIR
    with open(f"{WORKSPACE_DIR}/worker.pid", "w") as f:
        f.write(str(proc.pid))

    # read output:
    for line in proc.stderr:
        # if line contains "Ready to serve" then we can break
        if "torch.cuda.OutOfMemoryError" in line.decode("utf-8"):
            print("CUDA Out of memory error", file=sys.stderr)
            sys.exit(99)  # 99 is our code for CUDA OOM
        print(line.decode('utf-8'), file=sys.stderr)

    print("FastChat Worker exited", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

