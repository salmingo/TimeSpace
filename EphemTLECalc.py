#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
调用库SkyField, 计算TLE根数对应的位置
功能:
1. 配置文件: 
   默认配置文件: EphemTLECalc.cfg
2. TLE文件:
   双行或三行格式. 三行格式时, 第一行是通用名称
3. 命令行参数:
   可选参数: 配置文件路径
4. 输出项:
   (1) 大地测量坐标
   (2) 地心坐标
   (3) 测站地平坐标
   (4) 测站赤道坐标
   (5) 可视性(V: 可见; S: 地影; D: 低于水平面)
'''

from math import pi;
import sys;

R2D     = 180.0 / pi;
D2R     = pi / 180.0;

pathCfg = "EphemTLECalc.cfg";  # 默认配置文件
siteLon = 120.0 * D2R;  # 站心经度
siteLat = 40.0 * D2R;   # 站心纬度
siteAlt = 900.0;        # 站心海拔
pathTLE = "";           # TLE文件路径
dirDst  = "";           # 结果文件目录

def LoadConfig():
    '''
    加载配置参数文件
    '''
    return True;
    
#-----------------------------------------------------------------------------#
# 主函数
if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) == 2:
        pathCfg = sys.argv[1];
    if LoadConfig() == False:
        sys.exit(1);
        