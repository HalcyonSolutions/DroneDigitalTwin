"""
Copyright (C) Microsoft Corporation. 
Copyright (C) 2025 IAMAI CONSULTING CORP
MIT License.

List the names of assets that can be spawned by `world.spawn_object()` in ProjectAirSim.
"""

import argparse
import os

from projectairsim import ProjectAirSimClient, World
from projectairsim.utils import projectairsim_log


def main(scene: str, sim_config_path: str, asset_regex: str):
    client = ProjectAirSimClient()

    try:
        projectairsim_log().info("Connecting to Project AirSim server...")
        client.connect()
        projectairsim_log().info("Connected to sim server.")

        world = World(client, scene, delay_after_load_sec=0, sim_config_path=sim_config_path)
        projectairsim_log().info(f"Loaded scene '{scene}' from '{sim_config_path}'.")

        projectairsim_log().info(f"Listing assets matching regex: '{asset_regex}'")
        asset_ids = world.list_assets(asset_regex)

        print("\nAvailable spawnable assets:")
        if not asset_ids:
            print("  (no asset names found)")
        else:
            for asset_id in sorted(asset_ids):
                print(f"  {asset_id}")

    except Exception as err:
        projectairsim_log().error(f"Exception occurred: {err}", exc_info=True)
        raise

    finally:
        client.disconnect()
        projectairsim_log().info("Disconnected from sim server.")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_sim_config_path = os.path.join(script_dir, "sim_config")

    parser = argparse.ArgumentParser(
        description="List spawnable ProjectAirSim assets available to world.spawn_object()."
    )
    parser.add_argument(
        "--scene",
        default="scene_hello_gis.jsonc",
        help="Scene config to load before listing assets.",
    )
    parser.add_argument(
        "--sim-config-path",
        default=default_sim_config_path,
        help="Path to the sim config directory containing scene files.",
    )
    parser.add_argument(
        "--asset-regex",
        default=".*",
        help="Regex to filter asset names returned by the sim server.",
    )
    args = parser.parse_args()

    main(args.scene, args.sim_config_path, args.asset_regex)
