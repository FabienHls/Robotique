import math


def leg_dk(theta1, theta2, theta3, l1=51, l2=63.7, l3=93):

    correction_theta2 = -20.69
    correction_theta3 = 90 + correction_theta2 - 5.06

    theta1 = math.radians(theta1)
    theta2 = math.radians(theta2-correction_theta2)
    theta3 = math.radians(-(theta3-correction_theta3))


    d12 = l2 * math.cos(theta2)
    d23 = l3 * math.cos(theta2 + theta3)

    plan_contribution = l1 + d12 + d23


    x = math.cos(theta1) * plan_contribution
    y = math.sin(theta1) * plan_contribution
    z = - (l2 * math.sin(theta2) +l3 * math.sin(theta2 + theta3))

    print(x)
    print(y)
    print(z)


leg_dk(180,-30.501,-67.819)
