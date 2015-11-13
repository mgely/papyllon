#test for fitting function + Plotting from
# http://wiki.scipy.org/Cookbook/FittingData

from pylab import *
from scipy import *
from scipy import optimize
 
# if you experience problem "optimize not found", try to uncomment the following line. The problem is present at least at Ubuntu Lucid python scipy package
# from scipy import optimize
 
# Generate data points with noise
num_points = 150
Tx = linspace(-.1, .1, num_points)
Ty = Tx

tX = 11.86*cos(2*pi/0.81*Tx-1.32) + 0.64*Tx+4*((0.5-rand(num_points))*exp(2*rand(num_points)**2))
tY = -32.14*cos(2*pi/0.8*Ty-1.94) + 0.15*Ty+7*((0.5-rand(num_points))*exp(2*rand(num_points)**2))

Qc=100
Qi=100
w0=-0.05

Ql=float(Qi*Qc)/float(Qi+Qc)

S21= 20*np.log10(np.abs((float(Qc)/float(Qc+Qi)+2j*float(Qi*Qc)/float(Qi+Qc)*(Tx-w0)/float(w0))/(1+2j*float(Qi*Qc)/float(Qi+Qc)*(Tx-w0)/float(w0))))

#format p: p[0]=w0, p[1]=Qi, p[2]=Qc, p[3]=unity transmission
fitfunc_S21 = lambda p, x: p[3] + 20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(flist-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(flist-p[0])/float(p[0]))))
errfunc = lambda p,x, y: fitfunc_S21(p,x)-y
p0= [4.28e9,800,3000,-20]
p1, success = optimize.leastsq(errfunc,p0[:],args=(flist,b))

p1[1]=abs(p1[1])
p1[2]=abs(p1[2])

plot(flist,b,"ro", flist,fitfunc_S21(p1,flist),"r-")

# Fit the first set
#fitfunc = lambda p, x: p[0]*cos(2*pi/p[1]*x+p[2]) + p[3]*x # Target function
#errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
#p0 = [-15., 0.8, 0., -1.] # Initial guess for the parameters
#p1, success = optimize.leastsq(errfunc, p0[:], args=(Tx, tX))

#time = linspace(Tx.min(), Tx.max(), 100)
#plot(Tx, tX, "ro", time, fitfunc(p1, time), "r-") # Plot of the data and the fit
 
# Fit the second set
#p0 = [-15., 0.8, 0., -1.]
#p2,success = optimize.leastsq(errfunc, p0[:], args=(Ty, tY))
 
#time = linspace(Ty.min(), Ty.max(), 100)
#plot(Ty, tY, "b^", time, fitfunc(p2, time), "b-")

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
