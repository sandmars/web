#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')
import pylab
from fabric.api import local

class pylab_pesq:
    def __init__(self, filename='pesq_results.txt'):
        self.filename = filename

    def __pylab_result(self, mos, mos_lqo, picture):
        '''pylab 生成折线图'''
        length = len(mos)
        pylab.figure(figsize=(20.0, 5.0), frameon=False)
        pylab.grid(True)

        num = [num for num in range(length)]
        pylab.plot(num, mos, color='blue', linewidth=1.0, linestyle='-', label='MOS')
        pylab.plot(num, mos_lqo, color='green', linewidth=1.0, linestyle='-', label='MOS_LQO')

        from matplotlib.font_manager import FontProperties
        font = FontProperties(fname=r"/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc", size=14) 
        pylab.title(u'网关语音质量MOS值分析', fontproperties=font)
        pylab.legend(loc='lower right')
        pylab.xlabel(u'第N次', fontproperties=font)
        pylab.ylabel(u'MOS/MOS_LQO值', fontproperties=font)
        pylab.xlim(0.0, length)
        pylab.ylim(0, 5)
        mos_tick = [i * 0.5 for i in range(11)]
        pylab.yticks(mos_tick, mos_tick)
        
        x_tick = []
        for i in num:
            if i % (len(num)/10) == 0:
                x_tick.append(i)
        pylab.xticks(x_tick, x_tick)

        pylab.savefig(picture, dpi=256)
        #使用 pylab.show()，需要禁用 import matplotlib，matplotlib.use('Agg')
	
    def __mos_result(self):
        '''分析 PESQ 软件生成的文件，返回 MOS、MOS_LQO 列表'''
        mos = []
        mos_lqo = []
        fp = file(self.filename, 'rb')
        fp.readline()
        while True:
            line = fp.readline()
            if len(line) == 0:
                break
            line = line.split('\t')
            mos.append(float(line[2].split(' ')[1]))
            mos_lqo.append(float(line[3].split(' ')[1]))
        fp.close()
        return(mos,mos_lqo)
    
    def run_pesq(self, audio_dir, audio_prefix):
        out_list = local('ls -v %s/%s*out.wav' % (audio_dir, audio_prefix), capture=True).split('\n')
        in_list = local('ls -v %s/%s*in.wav' % (audio_dir, audio_prefix), capture=True).split('\n')
        local('cat /dev/null > pesq_results.txt')
        for audio in zip(in_list, out_list):
            local('/usr/local/bin/pesq +8000 %s %s' % audio, capture=True)
            #try:
                #local('/usr/local/bin/pesq +8000 %s %s' % audio, capture=True)
            #except:
                #pass

    def result(self, offset, picture_prefix):
        '''每 offset 个数据生成一个折线图'''
        mos,mos_lqo = self.__mos_result()
        length = len(mos)
        start,end = 0,offset
        while True:
            self.__pylab_result(mos[start:end:1], mos_lqo[start:end:1], '%s-%d-%d.png' % (picture_prefix, start, end))
            start,end = end,end+offset
            if start > length:
                break
        print('平均 MOS 值：%s' % (sum(mos)/len(mos)))
        print('最优 MOS 值：%s' % max(mos))
        print('最差 MOS 值：%s' % min(mos))
        print('平均 MOS_LQO 值：%s' % (sum(mos_lqo)/len(mos_lqo)))
        print('最优 MOS_LQO 值：%s' % max(mos_lqo))
        print('最差 MOS_LQO 值：%s' % min(mos_lqo))

if __name__ == '__main__':
    result = pylab_pesq('pesq_results.txt')
    #result.run_pesq('/nfs_share', '10000')
    result.result(500, '/tmp/mos-10000')

