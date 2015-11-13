#test for fitting function + Plotting from
# http://wiki.scipy.org/Cookbook/FittingData

from pylab import *
from scipy import *
from scipy import optimize
 
# if you experience problem "optimize not found", try to uncomment the following line. The problem is present at least at Ubuntu Lucid python scipy package
# from scipy import optimize
 
# Generate data points with noise


#usage of ramy barends formula
#format p: p[0]=w0, p[1]=Qi, p[2]=Qc, p[3]=unity transmission
fitfunc_S21 = lambda p, x: p[3] + 20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(flist-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(flist-p[0])/float(p[0]))))
errfunc = lambda p,x, y: fitfunc_S21(p,x)-y
p0= [4.28e9,800,3000,-20]
p1, success = optimize.leastsq(errfunc,p0[:],args=(flist,b))

p1[1]=abs(p1[1])
p1[2]=abs(p1[2])

plot(flist,b,"ro", flist,fitfunc_S21(p1,flist),"r-")


# Legend the plot
title("Transmission response of hanger")
xlabel("frequency [Hz]")
ylabel("S21 transmission [dB]")
legend(('data', 'fit'))
 
ax = axes()
 
text(0.8, 0.07,'f_res :  %.2f GHz \n Qi :  %u \n Qc : %u \n unity: %.1f dBm' % (p1[0]*1e-9,p1[1],p1[2],p1[3]),
        fontsize=10,
        horizontalalignment='left',
        verticalalignment='center',
        transform=ax.transAxes)
    
show()
