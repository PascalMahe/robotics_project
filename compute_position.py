import math
import logging


test_logger = logging.getLogger("test_logger")

def parse_command(command):
    """Parse a single command and return the command type and its parameters."""
    parts = command.split()
    cmd_type = parts[0]
    params = parts[1:]
    return cmd_type, params

def update_position(position, orientation, cmd_type, params):
    """Update the drone's position and orientation based on the command type and its parameters."""
    x, y, z = position
    yaw = orientation  # Current orientation in degrees
    
    param0 = int(params[0])

    if cmd_type == "up":
        z += param0
    elif cmd_type == "down":
        z -= param0
    elif cmd_type == "left":
        test_logger.debug(f"-= Left =-")
        # yaw - 90 -> account for direction (left)
        dx = param0 * math.cos(math.radians(yaw - 90))
        dy = param0 * math.sin(math.radians(yaw - 90))
        x += dx
        y += dy
    elif cmd_type == "right":
        test_logger.debug(f"-= Right =-")
        # yaw + 90 -> account for direction (right)
        dx = param0 * math.cos(math.radians(yaw + 90))
        dy = param0 * math.sin(math.radians(yaw + 90))
        x += dx 
        y += dy
    elif cmd_type == "forward":
        test_logger.debug(f"-= Forward =-")
        dx = param0 * math.cos(math.radians(yaw))
        dy = param0 * math.sin(math.radians(yaw))

        x += dx
        y += dy
    elif cmd_type == "back":
        # compute dx and dy, same as forward
        dx = param0 * math.cos(math.radians(yaw))
        dy = param0 * math.sin(math.radians(yaw))
        # apply dx and dy: reverse from forward
        x -= dx
        y -= dy
    elif cmd_type == "cw":
        yaw += param0
        yaw = yaw % 360  # Normalize yaw within 0-359 degrees
    elif cmd_type == "ccw":
        yaw -= param0
        yaw = yaw % 360  # Normalize yaw within 0-359 degrees
    elif cmd_type == "go":
        x = param0
        y = int(params[1])
        z = int(params[2])
    elif cmd_type == "curve":
        # For simplicity, assume the drone stops at the second curve point
        x = int(params[3])
        y = int(params[4])
        z = int(params[5])
    elif cmd_type == "stop":
        pass  # Do nothing, just hover in place
    
    return (x, y, z), yaw

def compute_final_coordinates(commands_str):
    """Compute the final coordinates based on the list of commands."""
    position = (0, 0, 0)
    orientation = 0  # Starting orientation (yaw) in degrees
    
    commands = commands_str.split(';')
    
    for command in commands:
        command = command.strip()
        if not command:
            continue
        cmd_type, params = parse_command(command)
        position, orientation = update_position(position, orientation, cmd_type, params)
    
    return position, orientation

def go_to_dest(position, orientation):
    # cmd_str = ""
    # # X
    # x = position[1]
    # x_dist = int(abs(x))
    # x_cmd = "forward"
    # if x < 0:
    #     x_cmd = "back"

    # if x != 0:
    #     cmd_str += f"{x_cmd} {x_dist}"
    
    # # Y
    # y = position[1]
    # y_dist = int(abs(y))
    # y_cmd = "left"
    # if y < 0:
    #     y_cmd = "right"

    # if y != 0:
    #     if len(cmd_str) > 0:
    #         cmd_str += "; "
    #     cmd_str += f"{y_cmd} {y_dist}"

    # #Z
    # z = position[2]
    # z_dist = int(abs(z))
    # z_cmd = "up"
    # if z < 0:
    #     z_cmd = "down"

    # if z != 0:
    #     if len(cmd_str) > 0:
    #         cmd_str += "; "
    #     cmd_str += f"{z_cmd} {z_dist}"

    # # finally orientation
    # if orientation != 0:
    #     cmd_str += f"; cw {orientation}"
    cmd_str = f"go {int(position[0])} {int(position[1])} {int(position[2])} 90"

    return cmd_str