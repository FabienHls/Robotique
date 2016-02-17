from math import *


def leg_ik(x, y, z, l1=51, l2=63.7, l3=93):
    # Alpha is a negative angle
    alpha = -20.69
    beta = 5.06

    # Correction of the 2 angles theta 2 and theta3 with alpha and beta
    correction_theta2 = alpha
    correction_theta3 = - 90 + correction_theta2 - beta

    theta1 = atan2(y, x)

    d13 = sqrt(y ** 2 + x ** 2) - l1
    d = sqrt(z ** 2 + d13 ** 2)

    a = atan2(z, d13)
    b = al_kashi(l2, d, l3)
    theta2 = - a - b

    theta3 = al_kashi(l2, l3, d)

    theta1 = degrees(theta1)
    theta2 = degrees(theta2) + correction_theta2
    theta3 = degrees(theta3) + correction_theta3

    print("[", theta1, ",", theta2 ,",", theta3, "]")

#Al-kashi theorem
def al_kashi(a, b, c):
    return acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))


# Test
leg_ik(118.79, 0, -115.14)
