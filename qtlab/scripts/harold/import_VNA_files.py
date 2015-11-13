import numpy

foldername = 'Y:/Harold/AC/LT/lg-04/lg-04xx31/VNA measurements/new setup/n s21 source vg '

gainmatrix=[]
j=0
datalist = []

plt.clear()
plt = plot()
plt.set_xrange(3e5,3e9)
plt.set_xlog(True)
plt.set_xlabel('Frequency (Hz)')
plt.set_ylabel('S21 (dB)')

option = 2

if option == 1:
    for i in linspace(-8,8,17):

        plt.set_yrange(-60,5)
        filename = foldername + str(int(i))+ 'v.csv'
        print filename
        
        arr = numpy.genfromtxt(filename,delimiter=',')
        frequency = arr[1:20000:100,0]
        gain = arr[1:20000:100,1]
        plot(frequency,gain,title='S21 source @ Vg = '+str(int(i))+'V')
            
             
        j=j+1

    filename = 'Y:/Harold/AC/LT/lg-04/lg-04xx31/VNA measurements/new setup/n s21 gate vg 0v.csv'
    arr = numpy.genfromtxt(filename,delimiter=',')
    frequency = arr[1:20000:100,0]
    gain = arr[1:20000:100,1]
    plot(frequency,gain,title='S21 gate')

elif option ==2:
    plt.set_yrange(-60,30)
    
    filename = foldername + str(int(0))+ 'v.csv'
    print filename
    
    arr = numpy.genfromtxt(filename,delimiter=',')
    frequency = arr[1:20000:100,0]
    gain = arr[1:20000:100,1]+11.4+10
    plot(frequency,gain,title='S21 source @ Vg = '+str(int(0))+'V')
#
    RCNT = 35000.0
    CCNT = 0.16e-12
    Rreadout = 5600.0
    Creadout = 1e-12

    ZCNT = 1/(1/RCNT+(2*pi*frequency*CCNT))
    Zreadout = 1/(1/Rreadout+(2*pi*frequency*Creadout))
    
    simgainvoltpervolt = Zreadout/(ZCNT+Zreadout)
    simgaindB = 10*log10(simgainvoltpervolt**2)+20

    plot(frequency,simgaindB,title='simulated cap match res S21 source @ Vg = '+str(int(0))+'V')
#
    RCNT = 35000.0
    CCNT = 0*1e-12
    Rreadout = 5600.0
    Creadout = 1e-12

    ZCNT = 1/(1/RCNT+(2*pi*frequency*CCNT))
    Zreadout = 1/(1/Rreadout+(2*pi*frequency*Creadout))
    
    simgainvoltpervolt = Zreadout/(ZCNT+Zreadout)
    simgaindB = 10*log10(simgainvoltpervolt**2)+20

    plot(frequency,simgaindB,title='simulated CCNT = 0, S21 source @ Vg = '+str(int(0))+'V')
#
    RCNT = 35000.0
    CCNT = 0.3e-12
    Rreadout = 5600.0
    Creadout = 1e-12

    ZCNT = 1/(1/RCNT+(2*pi*frequency*CCNT))
    Zreadout = 1/(1/Rreadout+(2*pi*frequency*Creadout))
    
    simgainvoltpervolt = Zreadout/(ZCNT+Zreadout)
    simgaindB = 10*log10(simgainvoltpervolt**2)+20

    plot(frequency,simgaindB,title='simulated CCNT=0.3pF, S21 source @ Vg = '+str(int(0))+'V')
#   
    freqlist = [1e6,10e6,300e6]
    indexlist=[]
    gainlist=[]
    for i in [0,1,2]:
        print i
        indexlist.append(numpy.where(frequency>freqlist[i])[0][0])
        gainlist.append(gain[indexlist[i]])
        print str(zip(freqlist,gainlist)[i])+'\n'
