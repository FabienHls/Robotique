import math


def leg_ik(x, y, z, l1=51, l2=63.7, l3=93):

    #Alpha is a negative angle
    alpha = -20.69
    beta = 5.06
    
    #Correction of the 2 angles theta 2 and theta3 whith alpha and beta
    correction_theta2 = alpha
    correction_theta3 = 90 + correction_theta2 - beta

    theta1 = math.atan2(y,x)

    d13 = math.sqrt(y**2 + x**2) - l1
    d = math.sqrt(z**2 + d13**2)

    a = math.atan2(z,d13)
    b = math.acos(( - (l3**2) + l2**2 + d**2) / (2 * l2 * d))
    theta2 = a + b

    x = math.acos( ( - (d**2) + l3**2 + l2**2) / (2 * l2 * l3))
    theta3 = 180 - x

    theta1 = math.degrees(theta1)
    theta2 = math.degrees(theta2) - correction_theta2
    theta3 = math.degrees(theta3) #+ correction_theta3

    print("[",theta1.__round__(3),",",theta2.__round__(3),","
        ,theta3.__round__(3),"]")

#Test
leg_ik(118.79, 0, -115.14)
leg_ik(0, 118.79, -115.14)
leg_ik(-64.14, 0, -67.79)
leg_ik(203.23, 0, -14.30)
