from info_extraction_final_grouped import GIVE
from attr_dict import my_attr_dict
from openai import OpenAI
import os
from options import parse_args

def main():
    args = parse_args()
    chat_client = OpenAI(api_key=args.openai_api_key)
    extractor = GIVE(client=chat_client, attr_dict=my_attr_dict, temperature = args.temperature, max_retry=args.max_try)
    extractor.extract_info_from_directory(args.input_path, args.model, args.thread_num, args.output_path)
if __name__ == '__main__':
    main()