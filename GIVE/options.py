import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description='parameters for GIVE')

    parser.add_argument('--config', type=str, default='./config.yaml')
    parser.add_argument('--openai_api_key', type=str)
    parser.add_argument('--input_path', type=str)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--model', type=str, default='gpt-4o-mini')
    parser.add_argument('--output_path', type=str, default='./output')
    parser.add_argument('--thread_num', type=int, default=2)

    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r') as f:
            data = yaml.safe_load(f)
        for key, value in data.items():
            setattr(args, key, value)

    return args

if __name__ == '__main__':
    args = parse_args()
    print(args)