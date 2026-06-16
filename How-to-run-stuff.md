# How to run stuff

## How to run the simulation with autonavigation using PX4 SITL over Blocks environment

This example uses airsim provided Blocks.uproject

1. Open the Blocks.uproject in Unreal Engine Editor and press play button
2. Launch PX4 by running `make px4_sitl_default none_iris`
3. Run `python ./DroneSimDev/client/python/example_user_scripts/px4_astar_autopilot.py` and watch the drone fly a mission

```python
python px4_astar_autopilot.py `
  --start "30,0,-6" `
  --goal "30,-48,-10" `
  --velocity-mps 2 `
  --land-at-goal `
  --print-waypoints `
  --px4-ready-timeout-sec 300
```

## How to run the simulation with rgb, depth, and lidar cameras

This example uses airsim provided Blocks.uproject

1. Open the Blocks.uproject in Unreal Engine Editor and press play button
2. Run `python ./DroneSimDev/client/python/example_user_scripts/check_all_cameras.py --camera [rgb|depth|lidar]`

```python
python check_all_cameras.py --camera all --fly-pattern
```

```python
python check_all_cameras.py --camera depth --depth-min-m 0.1 --depth-max-m 80
```

Units of distance are provided in meters for the depth camera. I found out the 30-80 meters works fine with Blocs.uproject environment.

## How to run the simulation over River-side forest environment

This example uses Free Fab provided River-side ForestDomeEnv.uproject

### How to scan the map

1. Open the River-side ForestDomeEnv.uproject in Unreal Engine Editor and press play button
2. Run
```python
   python px4_map_viewer.py `
   --start "50,0,-6" `
   --goal "50,20,-6" `
   --slice-z-ned -8 `
   --resolution-m 1 `
   --grid-step-m 10 `
   --label-step-m 20 `
   --output riverside_forest.png `
   --output-3d riverside_forest_3d.png `
   --map-size "500,500,10"
```

It saves both, 2D and 3D plots of the map.

### How to fly a mission with PX4
1. Open the River-side ForestDomeEnv.uproject in Unreal Engine Editor and press play button
2. Launch PX4 by running `make px4_sitl_default none_iris`
3. Run the command below, the drone will cross the river
```python
python px4_astar_autopilot.py `
  --start "60,-20,-6" `
  --goal "50,20,-6" `
  --velocity-mps 2 `
  --land-at-goal `
  --print-waypoints `
  --px4-ready-timeout-sec 300 `
  --teleport-start
```
