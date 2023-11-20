import sys
from app.cnc_programmer.main import main

if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])