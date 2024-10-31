import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description='parameters for Text2SQL')

    parser.add_argument('--config', type=str, default='config.yaml')
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--parser_model', type=str)
    parser.add_argument('--agent_model', type=str)
    parser.add_argument('--summary_model', type=str)
    parser.add_argument('--work_dir', type=str)
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--mysql_address',type=str)
    parser.add_argument('--mysql_port', type=int)
    parser.add_argument('--mysql_username',type=str)
    parser.add_argument('--mysql_password',type=str)
    parser.add_argument('--mysql_db_name', type=str)
    parser.add_argument('--collection_name', type=str)
    parser.add_argument('--vectorDB_path', type=str, default='vectorDB')
    parser.add_argument('--vectorDB_collection_name', type=str)
    parser.add_argument('--vectorDB_path_url', type=str)
    parser.add_argument('--thread_num', type=int, default=2)
    parser.add_argument('--port', type=int, default=9012)
    parser.add_argument('--openai_api_key', type=str)

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