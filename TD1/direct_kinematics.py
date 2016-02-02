import math


def leg_dk(theta1, theta2, theta3, l1=51, l2=63.7, l3=93):
    alpha = math.radians(20.69)
    beta = math.radians(5.06)

    theta1 = math.radians(theta1)
    theta2 = math.radians(theta2)
    theta3 = math.radians(theta3)

    x1 = l1 * math.cos(theta1)
    y1 = l1 * math.sin(theta1)
    z1 = 0

    l2_1 = l2 * math.cos(alpha)

    x2_1 = (l1+l2_1 * math.cos(theta2)) * math.cos(theta1)
    y2_1 = (l1 + l2_1 * math.cos(theta2)) * math.sin(theta1)
    z2_1 = l2_1 * math.sin(theta2)

    x2 = x2_1 + math.sin(theta2) * math.sin(alpha) * l2
    y2 = y1 + math.sin(theta1) * l2 * math.cos(theta2)
    z2 = z1 + l2 * math.sin(theta2)

    d12 = l2 * math.cos(theta2)
    d23 = l3 * math.cos(theta2 + theta3)

    plan_contribution = l1 + d12 + d23

    x3 = (l1 + math.cos(alpha) * l2 * math.cos(theta2) +
          math.sin(theta2) * math.sin(alpha) *l2 +
          math.sin(theta3) * math.cos(beta) * l3 +
          math.cos(theta2) * math.sin(beta) * l3 * math.cos(theta1))
    y3 = (l1 + math.cos(alpha) * l2 * math.cos(theta2) +
          math.sin(theta2) * math.sin(alpha) *l2 +
          math.sin(theta2) * math.cos(beta) * l3 +
          math.cos(theta2) * math.sin(beta) * l3 * math.cos(theta1))
    z3 = math.cos(alpha) * l2 * math.sin(theta2) \
         - math.cos(theta2) * math.sin(alpha) * l2 \
         - math.cos(theta2) * math.cos(beta) * l3 \
         + math.sin(theta2) * math.sin(beta)* l3

    '''x3 = plan_contribution * math.cos(theta1)
    y3 = plan_contribution * math.sin(theta1)
    z3 = l2 * math.sin(theta2) + l3 * math.sin(theta2+theta3)'''


    print(x3.__round__(2))
    print(y3.__round__(2))
    print(z3.__round__(2))


leg_dk(180,-30.501,-67.819)
