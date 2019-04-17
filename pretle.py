#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
generate satellite ephemeris from tle file
- 读取tle文件中根数
- 为每一组根数生成星历并存储为txt文件
'''
import sys;
import ephem;
from math import pi
from ephem import degrees, hours

R2D = 180.0 / pi
D2R = pi / 180.0

class TLECal:
    '''
    依据TLE根数生成星历
    文件名格式:
        name_yyyymmdd_xxxx.txt
        
    高度角阈值: 20度
    文件分割: 每个可观测弧段保存为一个文件
    
    输出项:
        UTC时间（时分秒）
        赤经[arcdeg]/J2000
        赤纬[arcdeg]/J2000
        方位角[arcdeg]
        高度角[arcdeg]
    '''
    def __init__(self):
        '''
        设置测站位置(地理经度/地理纬度/海拔高度)
        '''
        self.obs = ephem.Observer()
        # 默认位置: 兴隆观测基地
        self.obs.lon = '117.5745417' # 实数量纲: 弧度; 字符串格式: ddd:mm:ss
        self.obs.lat = '40.395933'
        self.obs.elevation = 960.0   # 实数, 量纲: 米
        self.obs.horizon = '20.0'    # 默认最小仰角: 20度
        self.cycle = 10              # 数据周期, 量纲: 秒

    def SetDate(self, year, month, day):
        self.year  = year
        self.month = month
        self.day   = day
    
    def SetTLE(self, name, line1, line2):
        self.sat = ephem.readtle(name, line1, line2)
        self.objid = line2[2:7]
        self.obs.date = "{}/{}/{} 00:00".format(self.year, self.month, self.day)
        print "ObjID : ", self.objid

    def OutputFile(self, t0, tn, no):
        '''
        输出星历文件
        '''
        print "Sequence No. : ", no
        filename = "%s_%d%02d%02d_%d.txt"%(self.objid, self.year, self.month, self.day, no)
        fd = open(filename, "w")
        while t0 <= tn:
            self.obs.date = t0
            self.sat.compute(self.obs)
#             print "%s %8.4f %8.4f" % (self.obs.date, self.sat.ra * R2D, self.sat.dec * R2D)
            fd.write("%s %8.4f %8.4f\n"%(self.obs.date, self.sat.ra * R2D, self.sat.dec * R2D))
            t0 += ephem.second * self.cycle
        fd.close()
        
    def Compute(self):
        '''
        计算根数在对应日期内的
        '''
        end_time = ephem.Date("{}/{}/{} 23:59:59".format(self.year, self.month, self.day))
        i = 1
        while True:
            self.sat.compute(self.obs)
            if (self.sat.set_time < self.sat.rise_time) or (self.sat.rise_time > end_time):
                break
            else:
#                 print "%d: %s,  %s,  %s" % (i, self.sat.rise_time, self.sat.transit_time, self.sat.set_time)
                set_time = self.sat.set_time
                # 开始: 输出星历文件
                self.OutputFile(self.sat.rise_time, set_time, i)
                i = i + 1
                # 结束: 输出星历文件
                self.obs.date = set_time + ephem.minute * 1
        
#-----------------------------------------------------------------------------#
# 主函数
# 命令行参数:
# 参数1: TLE file
# 参数2: 起始时间(UTC) 年
# 参数3: 起始时间(UTC) 月
# 参数4: 起始时间(UTC) 日
# 参数无效时直接退出
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "Usage: pretle TLE-File Year Month Day"
        sys.exit(1)

    year  = int(sys.argv[2])
    month = int(sys.argv[3])
    day   = int(sys.argv[4])

    tle = TLECal() # 测站位置
    tle.SetDate(year, month, day) # 日期

    complete = False # 已读取完备目标根数
    name = "unknown"
    # 遍历读取TLE文件, 提取TLE根数
    fd = open(sys.argv[1], "r")
    for line in fd:
        line = line.strip('\n')
        if line[1] == ' ':
            if line[0] == '1':   # 第一行
                line1 = line
            elif line[0] == '2': # 第二行
                line2 = line
                complete = True
        else:
            name = line

        if complete:
            tle.SetTLE(name, line1, line2)
            tle.Compute()
            complete = False
        
    fd.close()
