import sys

from app.final_tester.main import main

if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])
