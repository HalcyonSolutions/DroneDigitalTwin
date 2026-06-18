import argparse
import asyncio
import time
import projectairsim
from projectairsim import Drone, World
from projectairsim.types import Pose, Quaternion, Vector3

keyboard = None

# --- Drone Control Functions ---


def parse_vector3(value):
    parts = value.replace(",", " ").split()
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"Expected three coordinates, got {len(parts)} from '{value}'"
        )
    try:
        return [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Coordinates must be numeric: '{value}'"
        ) from exc


def make_pose_ned(position_ned):
    return Pose(
        {
            "translation": Vector3(
                {
                    "x": position_ned[0],
                    "y": position_ned[1],
                    "z": position_ned[2],
                }
            ),
            "rotation": Quaternion({"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0}),
            "frame_id": "DEFAULT_ID",
        }
    )


def get_pose_position_ned(drone):
    position = drone.get_ground_truth_kinematics()["pose"]["position"]
    return [float(position["x"]), float(position["y"]), float(position["z"])]


def print_live_ned(drone, last_print_at, interval_sec, force=False):
    now = time.time()
    if not force and now - last_print_at < interval_sec:
        return last_print_at

    position = get_pose_position_ned(drone)
    print(
        f"[LIVE NED] x={position[0]:8.2f}  "
        f"y={position[1]:8.2f}  z={position[2]:8.2f}",
        flush=True,
    )
    return now


async def takeoff(drone):
    """Arms the drone and takes off to a default altitude."""
    print("Arming the drone...")
    drone.arm()
    print("Taking off...")
    await drone.takeoff_async()
    time.sleep(1)


async def land(drone):
    """Lands the drone."""
    print("Landing...")
    await drone.land_async()
    print("Disarming the drone...")
    drone.disarm()

# --- Main Control Loop ---

async def run_keyboard_control(drone, live_ned_interval_sec, show_live_ned=True):
    """
    Controls the drone using keyboard inputs.

    Args:
        drone: The Drone object.
    """

    global keyboard
    if keyboard is None:
        try:
            import keyboard as keyboard_module
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "The keyboard_control.py script needs the 'keyboard' Python "
                "package. Install it in DroneSimDev_ENV with: pip install keyboard"
            ) from exc
        keyboard = keyboard_module

    # Enable API control
    drone.enable_api_control()

    # Takeoff
    await takeoff(drone)

    # Speed settings
    speed = 5  # m/s
    yaw_speed = 20  # degrees/s
    duration = 0.1  # seconds

    print("\n--- Keyboard Control ---")
    print("W/S: Pitch (Forward/Backward)")
    print("A/D: Roll (Left/Right)")
    print("Up/Down Arrows: Throttle (Altitude)")
    print("Left/Right Arrows: Yaw (Rotation)")
    print("L: Land")
    print("Q: Quit")
    if show_live_ned:
        print(f"Live NED: printing every {live_ned_interval_sec:g}s")
    print("--------------------")

    keep_running = True
    last_live_ned_at = 0.0

    while keep_running:
        if show_live_ned:
            last_live_ned_at = print_live_ned(
                drone,
                last_live_ned_at,
                live_ned_interval_sec,
            )

        # Reset velocity components
        vx, vy, vz, yaw_rate = 0, 0, 0, 0

        # Pitch
        if keyboard.is_pressed('w'):
            vx = speed

        elif keyboard.is_pressed('s'):
            vx = -speed

        # Roll
        if keyboard.is_pressed('a'):
            vy = -speed

        elif keyboard.is_pressed('d'):
            vy = speed

        # Throttle
        if keyboard.is_pressed('up'):
            vz = -speed  # Negative Z is up

        elif keyboard.is_pressed('down'):
            vz = speed

        # Yaw
        if keyboard.is_pressed('left'):
            yaw_rate = -yaw_speed

        elif keyboard.is_pressed('right'):
            yaw_rate = yaw_speed

        # Land and exit
        if keyboard.is_pressed('l'):
            await land(drone)
            if show_live_ned:
                last_live_ned_at = print_live_ned(
                    drone,
                    last_live_ned_at,
                    live_ned_interval_sec,
                    force=True,
                )
            keep_running = False

        # Quit
        if keyboard.is_pressed('q'):
            if show_live_ned:
                last_live_ned_at = print_live_ned(
                    drone,
                    last_live_ned_at,
                    live_ned_interval_sec,
                    force=True,
                )
            keep_running = False

        # Move the drone in its body frame
        # vx, vy, vz are now interpreted as forward/backward, right/left, up/down relative to the drone
        if vx != 0 or vy != 0 or vz != 0:
            await drone.move_by_velocity_body_frame_async(vx, vy, vz, duration)
        if yaw_rate != 0:
            await drone.rotate_by_yaw_rate_async(yaw_rate, duration)
        await asyncio.sleep(0.01)

# --- Main Execution ---

async def main():
    parser = argparse.ArgumentParser(
        description="Example of using keyboard to control a drone in Project AirSim."
    )

    # ... (parser arguments remain the same) ...
    parser.add_argument(
        "--address",
        help=("the IP address of the host running Project AirSim"),
        type=str,
        default="127.0.0.1",
    )

    parser.add_argument(
        "--sceneconfigfile",
        help=(
            'the Project AirSim scene config file to load, defaults to "scene_basic_drone.jsonc"'
        ),

        type=str,
        default="scene_basic_drone.jsonc",
    )

    parser.add_argument(
        "--simconfigpath",
        help=(
            'the directory containing Project AirSim config files, defaults to "sim_config"'
        ),
        type=str,
        default="sim_config/",
    )

    parser.add_argument(
        "--topicsport",
        help=(
            "the TCP/IP port of Project AirSim's topic pub-sub client connection "
            '(see the Project AirSim command line switch "-topicsport")'
        ),
        type=int,
        default=8989,
    )

    parser.add_argument(
        "--servicesport",
        help=(
            "the TCP/IP port of Project AirSim's services client connection "
            '(see the Project AirSim command line switch "-servicessport")'
        ),
        type=int,
        default=8990,
    )
    parser.add_argument(
        "--live-ned-interval-sec",
        help="How often to print live NED position while manually flying.",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--no-live-ned",
        help="Disable live NED position printing.",
        action="store_true",
    )
    parser.add_argument(
        "--start",
        type=parse_vector3,
        help="Optional NED x,y,z position to teleport Drone1 to before takeoff.",
    )

    args = parser.parse_args()
    client = projectairsim.ProjectAirSimClient(
        address=args.address,
        port_topics=args.topicsport,
        port_services=args.servicesport,
    )

    drone = None
    try:
        client.connect()
        world = projectairsim.World(
            client=client,
            scene_config_name=args.sceneconfigfile,
            sim_config_path=args.simconfigpath,
        )
        drone = Drone(client, world, "Drone1")

        if args.start:
            print(f"Teleporting Drone1 to NED {args.start}...")
            drone.set_pose(make_pose_ned(args.start), reset_kinematics=True)
            time.sleep(1)
            if not args.no_live_ned:
                print_live_ned(
                    drone,
                    last_print_at=0.0,
                    interval_sec=args.live_ned_interval_sec,
                    force=True,
                )

        await run_keyboard_control(
            drone,
            args.live_ned_interval_sec,
            not args.no_live_ned,
        )

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if drone:
            drone.disarm()
            drone.disable_api_control()
        client.disconnect()

        print("Cleaned up and disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
