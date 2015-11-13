#some extra functions


def fit_func(data,f_estimate):
#usage of ramy barends formula
        #format p: p[0]=w0, p[1]=Qi, p[2]=Qc, p[3]=unity transmission
        fitfunc_S21 = lambda p, x: p[3] + 20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))))
        errfunc = lambda p,x, y: fitfunc_S21(p,x)-y
        p0= [f_estimate,350,500,-66]
        p1, success = optimize.leastsq(errfunc,p0[:],args=(f_list,tr2))

        p1[1]=abs(p1[1])
        p1[2]=abs(p1[2])

        for z in p1:
            print z
            
        plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,f_list),"r-")


        # Legend the plot
        title("Transmission response of " + device_name + " timestap: " + date_path)
        xlabel("frequency [Hz]")
        ylabel("S21 transmission [dB]")
        legend(('data', 'fit'))
 
        ax = axes()
 
        text(0.8, 0.07,'f_res :  %.4f GHz \n Qi :  %u \n Qc : %u \n unity: %.1f dBm' % (p1[0]*1e-9,p1[1],p1[2],p1[3]),
                    fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform=ax.transAxes)
    
        show()


def intra_cav_photon_number(Pin, kext, kappa, w_probe, w_cav
