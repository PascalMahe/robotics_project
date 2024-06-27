import sys

from client import fetch_msg_from_other_host
from compute_position import compute_final_coordinates, go_to_dest


if __name__ == '__main__':
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    else:
        print("Please specify address to connect to (169.254.XXX.XXX).")
        sys.exit()

    port = 8890
    msg = fetch_msg_from_other_host(addr, port)
    position, orientation = compute_final_coordinates(msg)
    go_to_dest(position, orientation)