#import qt
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

from numpy import genfromtxt

import pylab
from scipy import *
from scipy import optimize


def loadcsv(filename):
    try:
        data=np.genfromtxt(filename,dtype=float,delimiter=';',names=True)
        return data

    except ValueError:
        print 'let us try Sonnet format'
        
        data=np.genfromtxt(filename,skip_header=True, dtype=float,delimiter=',', names=True)
        return data
        #except ValueError:
        #    print 'bullshit'

            
def loadcsv_sonnet(filename):
    
    data=np.genfromtxt(filename,delimiter=',', names=True)

def peak_S21(filename):
    data=loadcsv(filename)
    

    f_list=[]
    tr2=[]
    for i in data:
        f_list.append(i[0])
        tr2.append(i[1])

    a=array(tr2)
    return a.max()


class Resonance:

    def __init__(self):

        self.f_res=[]
        self.q_i=[]
        self.q_c=[]


        self.shunt_length=[]
        self.thickness=[]
    

def proc_data(s,S21=True):
    if(S21):
        f_res=[]
        t0=[]
        ql=[]
        for i in s:
            f_res.append(i[1][0])
            t0.append(i[1][1])
            ql.append(i[1][2])
        return f_res,t0,ql
    else:
        f_res=[]
        qi=[]
        qc=[]
        for i in s:
            f_res.append(i[1][0])
            qi.append(i[1][1])
            qc.append(i[1][2])
        return f_res,qi,qc
                         

    

def process_sonnet_csv(filename,save_batch=True,S21=True):
    f=open(filename,'r')

    batch=[]
    names=[]
    results=[]
    lines=[]

    #chop parametrizations into batches
    for i in f:
        lines.append(i)
        if i == '\n':
            batch.append(lines)
            lines=[]
    if(save_batch):
        for i in batch:
            print i[0][:-1]+'.csv'
            names.append(i[0][:-1]+'.csv')
            f=open(i[0][:-1]+'.csv','w')
            for j in i:
                f.write(j)
            f.close()
    for i in names:
        print i

        if(S21):
            result=fit_S21_sal(i)
        else:
            result = fit_S11(i)
        
        results.append([i,result])


    
    
    
    return results


def lorentzian(w,w0,k_in,k_out):
    return 20*np.log10(np.abs(2*np.sqrt(k_in*k_out)/(k_in+k_out)/(1-2j*(w-w0)/(k_in+k_out))))#(k_in*p[1]/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))




def fit_S21_schuster(f_list=None, trace=None,filename=None,plotsave=True,k_in=0.001,k_out=0.0224):

    if filename is not None:
        print 'load csv file'
        data=loadcsv(filename)

        f_list=[]
        tr2=[]

        for i in data:
            f_list.append(i[0])
            tr2.append(i[1])

        a=array(tr2)
    else:
        if f_list is None:
            print 'error no data supplied'
            return
        if trace is None:
            print 'error no data supplied'
            return
    a=array(trace)
        
        

    f_index = np.where(a==a.max())[0][0]
    print f_index

    f_estimate=f_list[f_index]
    print 'fest ', f_estimate

    #transmission cavity formula in Schuster's thesis p.51/52
    #format p: p[0]=w0, p[1]=k_out, k_in has to be supplied by hand...

    
    
    #fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(np.sqrt((k_in*p[1])/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))
    fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(2*np.sqrt(k_in*p[1])/(k_in+p[1])/(1-2j*(x-p[0])/(k_in+p[1]))))#(k_in*p[1]/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))
    
    errfunc = lambda p,x,y: fitfunc_S21(p,x)-y
    p0=[f_estimate,k_out]
    p1, success = optimize.leastsq(errfunc,p0[:],args=(array(f_list),array(tr2)))
    
    for z in p1:
        print z

    if(plotsave):
        pylab.plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,array(f_list)),"r-")


        # Legend the plot
        pylab.title("Transmission response")
        pylab.xlabel("frequency [Hz]")
        pylab.ylabel("S21 transmission [dB]")
        pylab.legend(('data', 'fit'))
 
        ax = pylab.axes()
 
        pylab.text(0.8, 0.07,'f_res :  %.4f GHz \n k_ext :  %u \n' % (p1[0],p1[1]),
                    fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform=ax.transAxes)

        pylab.savefig(filename +'.png')
        pylab.show()


    return f_list,tr2


def lorentzian_sal(w,w0,Ql,T0):
    return 20*np.log10(np.abs(T0/(1+2j*Ql*(w-w0)/(w0))))

def fit_S21_sal(filename,plotsave=True,max_dB=-40, k_out=0.0224):

    data=loadcsv(filename)

    f_list=[]
    tr2=[]

    for i in data:
        f_list.append(i[0])
        tr2.append(i[1])

    a=array(tr2)

    f_index = np.where(a==a.max())[0][0]
    print f_index

    f_estimate=f_list[f_index]
    print 'fest ', f_estimate

    T0 =a[f_index]

    print 'peak max: ', max_dB, T0

    #transmission cavity formula in Schuster's thesis p.51/52, modified to Rami's type
    #format p: p[0]=w0, p[1]=T0, p[2]=Ql, k_in has to be supplied by hand...

    
    fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(p[1]/(1+2j*p[2]*(x-p[0])/(p[0]))))
    #fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(np.sqrt((k_in*p[1])/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))
    #fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(2*np.sqrt(k_in*p[1])/(k_in+p[1])/(1-2j*(x-p[0])/(k_in+p[1]))))#(k_in*p[1]/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))
    
    errfunc = lambda p,x,y: fitfunc_S21(p,x)-y
    p0=[f_estimate,T0,400]
    p1, success = optimize.leastsq(errfunc,p0[:],args=(array(f_list),array(tr2)))
    
    for z in p1:
        print z

    if(plotsave):
        pylab.plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,array(f_list)),"r-")


        # Legend the plot
        pylab.title("Transmission response")
        pylab.xlabel("frequency [Hz]")
        pylab.ylabel("S21 transmission [dB]")
        pylab.legend(('data', 'fit'))
 
        ax = pylab.axes()
 
        pylab.text(1.1, .1,'f_res :  %.4f GHz \n T0 :  %.4f \n Ql %.4f' % (p1[0],20*np.log10(p1[1]),p1[2]),
                    fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='top',
                    transform=ax.transAxes)

        pylab.savefig(filename +'.png')
        pylab.show()


    return p1


                                   
def fit_S11(filename,plotsave=True):

    data=loadcsv(filename)
    

    f_list=[]
    tr2=[]
    for i in data:
        f_list.append(i[0])
        tr2.append(i[1])

    a=array(tr2)
    f_index = np.where(a==a.min())[0][0]
    print f_index

    f_estimate = f_list[f_index]

    print f_estimate

    #usage of ramy barends formula
    #format p: p[0]=w0, p[1]=Qi, p[2]=Qc, p[3]=unity transmission, p[4]=slope unity transmission
    #fitfunc_S21 = lambda p, x: p[3] + 20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))))
    fitfunc_S21 = lambda p, x: p[3] + x*p[4] +20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(x-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(x-p[0])/float(p[0]))))
    errfunc = lambda p,x, y: fitfunc_S21(p,x)-y
    p0= [f_estimate,10000,10000,0,-0.01]
    p1, success = optimize.leastsq(errfunc,p0[:],args=(array(f_list),array(tr2)))

    p1[1]=abs(p1[1])
    p1[2]=abs(p1[2])

    for z in p1:
        print z

    
    if(plotsave):
        pylab.plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,array(f_list)),"r-")


        # Legend the plot
        pylab.title("Transmission response")
        pylab.xlabel("frequency [Hz]")
        pylab.ylabel("S21 transmission [dB]")
        pylab.legend(('data', 'fit'))
 
        ax = pylab.axes()
 
        pylab.text(0.8, 0.07,'f_res :  %.4f GHz \n Qi :  %u \n Qc : %u \n unity: %.1f dBm' % (p1[0],p1[1],p1[2],p1[3]),
                    fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform=ax.transAxes)

        pylab.savefig(filename +'.png')
        pylab.show()

    return p1
    
        
