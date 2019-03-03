#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
大地测量坐标(WGS84):
O: 地球质心
λ: 经度
ψ: 纬度
h: 高度
引力等势面

地心系(Geocentric):
O: 地球质心
X:   O至赤道与本初子午线的交点
Y:   O至赤道与经度90度子午线的交点
Z:   O至北极

站心系(Topocentric):
O: 测站中心
XYZ: ENU

'''
from math import pi, cos, sin, tan, sqrt, asin, atan2;

PI360  = pi * 2;
D2R = pi / 180.0;  # 系数: 角度=>弧度
R2D = 180.0 / pi;  # 系数: 弧度=>角度

a  = 6378137;    # WGS84参考椭圆半长轴, 量纲: 米. 赤道半径
f  = 1.0 / 298.257223563;  # 椭圆扁平率
b  = a * (1.0 - f); # 半短轴
e2 = f * (2.0 - f); # 离心率平方

def CurveRadius(lat):
    '''
    计算WGS84下在纬度lat的曲率半径
    lat: 纬度, 量纲: 弧度
    R  : 曲率半径, 量纲: 米
    '''
    t = sin(lat);
    R = a / sqrt(1.0 - e2 * t * t);
    return R;

def Geodetic2Geocentric(lon, lat, h):
    '''
    计算WGS84下球坐标对应的直角坐标
    lon: 经度, 量纲: 弧度
    lat: 纬度, 量纲: 弧度
    h  : 高度, 量纲: 米
    (x, y, z): 对应的直角坐标
    '''
    R = CurveRadius(lat);
    R1 = (R + h) * cos(lat);
    x = R1 * cos(lon);
    y = R1 * sin(lon);
    z = ((1.0 - e2) * R + h) * sin(lat);
    return [x, y, z];

def Geograph2Geodetic(lat, h):
    '''
    地理测量系转换为WGS84系, ψ变化
    '''
    t  = tan(lat);
    hr = h / a;
    factor = 1.0 / sqrt(1 + (1.0 - e2) * t * t);
    x  = factor + hr * cos(lat);
    y  = (1.0 - e2) * tan(lat) * factor + hr * sin(lat);
    lat1 = atan2(y, x);
    
    return lat1;
    
def Geocentric2Topocentric(dX, dY, dZ, lon, lat):
    '''
    地心系转换为站心系
    (dX, dY, dZ)=(X-X0, Y-Y0, Z-Z0)
    (X, Y, Z): 目标的地心系坐标
    (X0, Y0, Z0): 站心的地心系坐标
    lon: 站心经度, 量纲: 弧度
    lat: 站心纬度, 量纲: 弧度
    (x, y, z): 目标的站心系坐标
    '''
    x = -sin(lon) * dX + cos(lon) * dY;
    y = -sin(lat) * cos(lon) * dX - sin(lat) * sin(lon) * dY + cos(lat) * dZ;
    z = cos(lat) * cos(lon) * dX + cos(lat) * sin(lon) * dY + sin(lat) * dZ;
    return [x, y, z];

def Topocentric2Gencentric(x, y, z, lon, lat):
    '''
    站心系转换为地心系
    (x, y, z): 目标的站心系坐标
    lon: 站心经度, 量纲: 弧度
    lat: 站心纬度, 量纲: 弧度
    (dX, dY, dZ)=(X-X0, Y-Y0, Z-Z0)
    (X, Y, Z): 目标的地心系坐标
    (X0, Y0, Z0): 站心的地心系坐标
    '''
    dX = -sin(lon) * x - sin(lat) * cos(lon) * y + cos(lat) * cos(lon) * z;
    dY = cos(lon) * x - sin(lat) * sin(lon) * y + cos(lat) * sin(lon) * z;
    dZ = cos(lat) * y + sin(lat) * z;
    return [dX, dY, dZ];

def CartTopocentric2Horizontal(x, y, z):
    '''
    WGS系直角坐标转换为地平系球坐标
    lon: 经度, 南零点
    lat: 纬度
    h  : 高度
    '''
    x2y2 = x * x + y * y;
    h = sqrt(x2y2 + z * z);
    lon = asin(y / sqrt(x2y2));
    lon = -1.0 * (lon + pi * 0.5);
    if (lon < -pi):
        lon = lon + PI360;
    elif (lon > pi):
        lon = lon - PI360;
        
    lat = asin(z / h);
    return [lon, lat, h];

def Horizontal():
    '''
    '''

lon_site = (117 + (34 + 28.35 / 60.0) / 60.0) * D2R;
lat_site = (40 + (23 + 45.36 / 60.0) / 60.0) * D2R;
h_site   = 900.0;
# lon_obj  = 110.41 * D2R;
# lat_obj  = -0.23 * D2R;
# h_obj    = 35770000.0;
lon_obj  = lon_site + 10 * D2R;
lat_obj  = lat_site;
h_obj    = h_site;

# lat_site_1 = Geograph2Geodetic(lat_site, h_site);
# print "Site Latitude: %f (Geographic), %f (Geocentric)" % (lat_site * R2D, lat_site_1 * R2D);

[X0, Y0, Z0] = Geodetic2Geocentric(lon_site, lat_site, h_site);
[X, Y, Z] = Geodetic2Geocentric(lon_obj, lat_obj, h_obj);
dX = X - X0;
dY = Y - Y0;
dZ = Z - Z0;
print "Cartesian Site   : %f, %f, %f" % (X0, Y0, Z0);
print "Cartesian Object : %f, %f, %f" % (X, Y, Z);

[x, y, z] = Geocentric2Topocentric(dX, dY, dZ, lon_site, lat_site);
[lon, lat, h] = CartTopocentric2Horizontal(x, y, z);
print "Horzontal Coordinates: %f, %f, %f [km]" % (lon * R2D, lat * R2D, h * 1E-3);

# 
# [Xo, Yo, Zo] = Geodetic2Geocentric(lo, bo, ho);
# [X, Y, Z]    = Geodetic2Geocentric(l, b, h);
# dX  = X - Xo;
# dY  = Y - Yo;
# dZ  = Z - Zo;
# [x, y, z]    = Geocentric2Topocentric(l, b, dX, dY, dZ);
# [lt, bt, ht] = Cart2Sphere(x, y, z);
# 
# print "l = %f, b = %f, h = %f km" % (lt * R2D, bt * R2D, ht * 1E-3);
