import sys
import argparse

def main():
    print('Arguments:')
    print(sys.argv)

    parser = argparse.ArgumentParser(description='Sample')

    parser.add_argument('--hello', action='store_true', help='Say hello')

    args = parser.parse_args()

    if args.hello:
        print('Hello world')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

