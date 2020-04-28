import sys

#using an algorithm written by the sweetest ever wife to be, wei

#usage python pixels_to_map oa_xm oa_ym oa_xi oa_yi ob_xm ob_ym ob_xi ob_yi
#m is map coords, i is pixels relative to map center

oa_xm=int(sys.argv[1])
oa_ym=int(sys.argv[2])
oa_xi=int(sys.argv[3])
oa_yi=int(sys.argv[4])
ob_xm=int(sys.argv[5])
ob_ym=int(sys.argv[6])
ob_xi=int(sys.argv[7])
ob_yi=int(sys.argv[8])

l_10 = 1/(oa_xm - (ob_xm*oa_ym)/ob_ym)
m_10 = 1/(ob_xm - (oa_xm*ob_ym)/oa_ym)

l_01 = 1/(oa_ym - (ob_ym*oa_xm)/ob_xm)
m_01 = 1/(ob_ym - (oa_ym*ob_xm)/oa_xm)

x_10 = l_10 * oa_xi + m_10 * ob_xi
y_10 = l_10 * oa_yi + m_10 * ob_yi

x_01 = l_01 * oa_xi + m_01 * ob_xi
y_01 = l_01 * oa_yi + m_01 * ob_yi

print("pixels per map")
print(x_10, y_10, x_01, y_01)

#now the same thin in reverse
oa_xi=int(sys.argv[1])
oa_yi=int(sys.argv[2])
oa_xm=int(sys.argv[3])
oa_ym=int(sys.argv[4])
ob_xi=int(sys.argv[5])
ob_yi=int(sys.argv[6])
ob_xm=int(sys.argv[7])
ob_ym=int(sys.argv[8])

l_10 = 1/(oa_xm - (ob_xm*oa_ym)/ob_ym)
m_10 = 1/(ob_xm - (oa_xm*ob_ym)/oa_ym)

l_01 = 1/(oa_ym - (ob_ym*oa_xm)/ob_xm)
m_01 = 1/(ob_ym - (oa_ym*ob_xm)/oa_xm)

x_10 = l_10 * oa_xi + m_10 * ob_xi
y_10 = l_10 * oa_yi + m_10 * ob_yi

x_01 = l_01 * oa_xi + m_01 * ob_xi
y_01 = l_01 * oa_yi + m_01 * ob_yi

print("maps per pixel")
print(x_10, y_10, x_01, y_01)
