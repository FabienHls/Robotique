import math

def leg_dk(theta1,theta2,theta3,l1=51,l2=63.7,l3=93):
	alpha = math.radians(20.69)
	beta = math.radians(5.06)
	x1 = l1 * math.cos(theta1)
	y1 = l1 * math.sin(theta1)
	z1 = 0
	
	x2 = x1 + math.cos(theta1) * l2 * math.cos(theta2)
	y2 = y1 + math.sin(theta1) * l2 * math.cos(theta2)
	z2 = z1 + l2 * math.sin(theta2)
	
	d12 = l2 * math.cos(theta2)
	d23 = l3 * math.cos(theta2 + theta3)
	
	planContribution = l1 + d12 + d23
	
	x3 = planContribution * math.cos(theta1) - (l2 * (1 - math.cos(alpha))) * math.cos(theta1) - (l3 * (1 - math.sin(beta))) * math.cos(theta1)
	y3 = planContribution * math.sin(theta1 - (l2 * (1 - math.cos(alpha))) * math.sin(theta1) - (l3 * (1 - math.sin(beta))) * math.sin(theta1))
	z3 = l2 * math.sin(theta2) + l3 * math.sin(theta2 + theta3) - (l2 * math.sin(alpha)) - (l3 * math.cos(beta))
	
	print("x3 %d" % x3)
	print("y3 %d" % y3)
	print("z3 %d" % z3)

leg_dk(180,-30.501,-67.819)