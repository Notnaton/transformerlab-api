import argparse
import subprocess
import sys
import os


parser = argparse.ArgumentParser(
    description='Run Eleuther AI LM Evaluation Harness.')
parser.add_argument('--model_name', default='gpt-j-6b', type=str,
                    help='Model to use for evaluation.')
parser.add_argument('--model_type', default='hf-causal',
                    type=str, help='Type of model to use for evaluation.')
parser.add_argument('--experiment_name', default='', type=str)
parser.add_argument('--eval_name', default='', type=str)
parser.add_argument('--task', default='', type=str)


args, other = parser.parse_known_args()

# print("Calling Eleuther AI LM Evaluation Harness with args:")
# print(args)

root_dir = os.environ.get("LLM_LAB_ROOT_PATH")
plugin_dir = os.path.realpath(os.path.dirname(__file__))

# example command from https://github.com/EleutherAI/lm-evaluation-harness
# python main.py \
#    --model hf-causal \
#    --model_args pretrained=EleutherAI/gpt-j-6B \
#    --tasks hellaswag \
#    --device cuda:0

# type = args.model_type

model_args = 'pretrained=' + args.model_name
task = args.task

command = ["lm-eval",
           '--model_args', model_args, '--tasks', task, '--device', 'cuda:0', '--trust_remote_code']

subprocess.Popen(
    command,
    cwd=plugin_dir,
)
