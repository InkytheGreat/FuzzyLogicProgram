
from fuzzylogic.classes import Domain, Set, Rule
from fuzzylogic.functions import R, S, alpha
from fuzzylogic.defuzz import bisector

from matplotlib import pyplot as plt






angle = Domain("Angle", -180, 180)
distance = Domain("Distance", 0, 100)
obstacle = Domain("Obstacle", 0, 100)
obstacle_left = Domain("ObstacleLeft", 0, 100)  # Distance to obstacle on the left
obstacle_right = Domain("ObstacleRight", 0, 100)  # Distance to obstacle on the right
exploration = Domain("Exploration", 0, 1)
direction = Domain("Direction", 0, 2)
space_advantage = Domain("SpaceAdvantage", -1, 1)

# Angle plot
plt.figure(1)
angle.left = S(-40, -2)
angle.left.plot()
angle.leftCenter = R(-15, 0)
angle.rightCenter = S(0, 15)
angle.center = angle.leftCenter & angle.rightCenter
angle.center.plot()
angle.right = R(2, 40)
angle.right.plot()
plt.title('Angle')

# Distance plot
plt.figure(2)
distance.close = S(0, 40)
distance.close.plot()
distance.leftMedium = R(10, 50)
distance.rightMedium = S(50, 90)
distance.medium = distance.leftMedium & distance.rightMedium
distance.medium.plot()
distance.far = R(15, 100)
distance.far.plot()
plt.title('Distance')


# Obstacle plot
plt.figure(3)
obstacle.near = S(0, 25)
obstacle.near.plot()
obstacle.leftMedium = R(10, 50)
obstacle.rightMedium = S(50, 90)
obstacle.medium = obstacle.leftMedium & obstacle.rightMedium
obstacle.medium.plot()
obstacle.far = R(15, 100)
obstacle.far.plot()
plt.title('Obstacle')

# Obstacle left plot
plt.figure(4)
obstacle_left.near = S(0, 25)
obstacle_left.near.plot()
obstacle_left.leftMedium = R(10, 50)
obstacle_left.rightMedium = S(50, 90)
obstacle_left.medium = obstacle.leftMedium & obstacle.rightMedium
obstacle_left.medium.plot()
obstacle_left.far = R(15, 100)
obstacle_left.far.plot()
plt.title('Obstacle')

# Obstacle right plot
plt.figure(5)
obstacle_right.near = S(0, 25)
obstacle_right.near.plot()
obstacle_right.leftMedium = R(10, 50)
obstacle_right.rightMedium = S(50, 90)
obstacle_right.medium = obstacle.leftMedium & obstacle.rightMedium
obstacle_right.medium.plot()
obstacle_right.far = R(15, 100)
obstacle_right.far.plot()
plt.title('Obstacle')

# Direction plot
plt.figure(6)
direction.left = S(0, 0.8)
direction.left.plot()
direction.leftStraight = R(0.2, 0.8)
direction.rightStraight = S(1.2, 1.8)
direction.straight = direction.leftStraight & direction.rightStraight
direction.straight.plot()
direction.right = R(1.2, 2)
direction.right.plot()
plt.title('Direction')

plt.figure(7)
exploration.high = R(0.5, 1)
exploration.low = S(0, 0.5)
exploration.high.plot()
exploration.low.plot()
plt.title('Exploration')

plt.figure(8)
space_advantage.left_open = S(-1, -0.2)
space_advantage.left_open.plot()
space_advantage.left_balanced = R(-0.5, 0)
space_advantage.right_balanced = S(0, 0.5)
space_advantage.balanced = space_advantage.left_balanced & space_advantage.right_balanced
space_advantage.balanced.plot()
space_advantage.right_open = R(0.2, 1)
space_advantage.right_open.plot()
plt.title('Space Advantage')

# Define fuzzy rules
# Food-seeking with progress
R1 = Rule({(angle.left, obstacle_left.far, ~space_advantage.right_open): direction.left})
R2 = Rule({(angle.right, obstacle_right.far, ~space_advantage.left_open): direction.right})
R3 = Rule({(angle.center, obstacle.far, space_advantage.balanced): direction.straight})

# Collision avoidance
'''R4 = Rule({(obstacle.near, obstacle_left.far, obstacle_right.near): direction.left})
R5 = Rule({(obstacle.near, obstacle_left.near, obstacle_right.far): direction.right})
R6 = Rule({(obstacle.near, obstacle_left.medium, obstacle_right.near): direction.left})
R7 = Rule({(obstacle.near, obstacle_left.near, obstacle_right.medium): direction.right})
R8 = Rule({(obstacle.near, obstacle_left.medium, obstacle_right.medium): direction.right})
R9 = Rule({(obstacle.near, obstacle_left.far, obstacle_right.medium): direction.left})
R10 = Rule({(obstacle.near, obstacle_left.medium, obstacle_right.far): direction.right})
R11 = Rule({(obstacle.near, obstacle_left.far, obstacle_right.far): direction.left})'''
R_panic_L = Rule({(obstacle_left.near): direction.right})
R_panic_R = Rule({(obstacle_right.near): direction.left})

# 2. HEAD-ON COLLISION HANDLING (The Decision Tree)
# We only care about Front Obstacles if sides are NOT near (handled above).

# Case A: Front blocked, but Angle says "Go Left" -> We Obey Angle
R_headon_L = Rule({
    (obstacle.near, obstacle_left.far, angle.left): direction.left
})
# Also cover LeftCenter to be safe
R_headon_LC = Rule({
    (obstacle.near, obstacle_left.far, angle.leftCenter): direction.left
})

# Case B: Front blocked, but Angle says "Go Right" -> We Obey Angle
R_headon_R = Rule({
    (obstacle.near, obstacle_right.far, angle.right): direction.right
})
R_headon_RC = Rule({
    (obstacle.near, obstacle_right.far, angle.rightCenter): direction.right
})

R_deflect_L = Rule({
    (obstacle.near , obstacle_left.far , angle.leftCenter):
    direction.left}
)

R_deflect_R = Rule({
    (obstacle.near , obstacle_right.far , angle.rightCenter):
    direction.right}
)

# Case C: THE TRUE STALEMATE (The Tie-Breaker)
# Front is blocked, sides are safe, AND Angle is Dead Center (or unknown).
# ONLY NOW do we force an arbitrary Right turn.
R_stalemate = Rule({
    (obstacle.near, obstacle_left.far, obstacle_right.far, angle.center): 
    direction.right
})

# Default
#R_default = Rule({(): direction.straight})

# Exploration (random movement)
R_random1 = Rule({(exploration.high, obstacle_right.far): direction.right})
R_random2 = Rule({(exploration.high, obstacle_left.far): direction.left})
#R_random3 = Rule({(exploration.high, obstacle.far): direction.straight})
R_explore_safe = Rule({(exploration.high, obstacle_left.far, obstacle_right.far, obstacle.far): direction.right})




rules = [
    R1, R2, R3, R_random1, R_random2,  R_explore_safe, R_panic_L, R_panic_R,
    R_headon_L, R_headon_LC, R_headon_R, R_headon_RC, R_stalemate, R_deflect_L, R_deflect_R
]

# sample inputs (angle degrees, distance units, obstacle front distance
samples = [
    {angle: -90, distance: 50, obstacle: 50, space_advantage: 0},
    {angle: -20, distance: 10, obstacle: 2, space_advantage: 0},
    {angle: 0, distance: 5, obstacle: 1, space_advantage: 0},
    {angle: 15, distance: 30, obstacle: 20, space_advantage: 0},
    {angle: 90, distance: 100, obstacle: 100, space_advantage: 0}
]
totalRule = sum(rules)
    
def direction_output(result): 
    if result is None:
        return "F"
    elif result < 0.95:
        return "L"
    elif result < 1.05:
        return "F"
    else:
        return "R"

# for i, sample in enumerate(samples):
#     print(f"Sample {i+1}: Angle={sample[angle]}, Distance={sample[distance]}, Obstacle={sample[obstacle]}")
    
#     # Evaluate rules
#     result = totalRule(sample, bisector)
#     print(f"  Resulting Direction Memberships: {result} Direction Value: {direction_output(result)}")

#plt.show()