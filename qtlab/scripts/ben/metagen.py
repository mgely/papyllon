def spyview_process(data=0,len1=0,minval1=0,maxval1=0,len2=0,minval2=0,maxval2=0,len3=0,minval3=0,maxval3=0):
    metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n'
                   +str(len1)+'\n'
                   +str(minval1)+'\n'
                   +str(maxval1)+'\n'
                   +str(data.get_dimension_name(0))+'\n'
                   +'#outer loop\n'
                   +str(len2)+'\n'
                   +str(minval2)+'\n'
                   +str(maxval2)+'\n'
                   +str(data.get_dimension_name(1))+'\n'
                   +'#outer most loop\n'
                   +str(len3)+'\n'
                   +str(minval3)+'\n'
                   +str(maxval3)+'\n'
                   +str(data.get_dimension_name(2))+'\n'
                  )                       

    metafile.write('#values\n'
                   +'4\n'
                   +str(data.get_dimension_name(3)))
    metafile.write('#values\n'
                   +'5\n'
                   +str(data.get_dimension_name(4)))
    metafile.write('#values\n'
                   +'6\n'
                   +str(data.get_dimension_name(5)))
    metafile.write('#values\n'
                   +'7\n'
                   +str(data.get_dimension_name(6)))
    metafile.write('#values\n'
                   +'8\n'
                   +str(data.get_dimension_name(7)))
    metafile.close()
