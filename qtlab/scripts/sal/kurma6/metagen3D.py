def spyview_process(data=0,minval=0,maxval=0,minblockval=0,maxblockval=0,outermostblockval=0,reset=False,_outermostblockvals=[],newoutermostblockval=False):
    '''
    Substitute for "data.new_block"
    Creates spyview meta.txt file after every block is completed

    REQUIRED Arguments:
        data -- the data object
        minval -- minval of inner loop
        maxval -- maxval of inner loop
        blockval -- value of outer loop
        
    optional argument:
        reset -- use to clear before measurement:

    _blockvals is internal and should not be touched!
    '''

    #print 'debug metagen'
    
    if reset==True:

        #print 'reset is true'
        while len(_outermostblockvals)>0:
            _outermostblockvals.pop()
    else:

        if(newoutermostblockval):
            _outermostblockvals.append(outermostblockval)

        #print 'reset is false'
        #print _outermostblockvals

        metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
        metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (data.get_npoints_max_block(), minval, maxval,
             data.get_dimension_name(0)))
        metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (data.get_nblocks_complete()/(len(_outermostblockvals)), minblockval, maxblockval,
             data.get_dimension_name(1)))
        metafile.write('#outer most loop\n%s\n%s\n%s\n%s\n'%(len(_outermostblockvals), _outermostblockvals[0], _outermostblockvals[-1],data.get_dimension_name(2)))
        metafile.write('#values\n4\n%s'%data.get_dimension_name(3))
        metafile.close()

#There should be something that converts a datafile back into a data object...

##def spyview_post_process(filename):
##    '''
##    Substitue for "data.new_block"
##    Creates spyview meta.txt file after every block is completed
##
##    Arguments:
##        filename -- data file to use 
##    '''
##    datafile=open(filename,'r')
##    data=[]
##    for line in datafile:
##        if (len(line)>2) and (line[0]!='#')
##        data.append(line.split())
##
##    innervals=[]
##    blockvals=[]
##    for i in data:
##        innervals.append(i[0])
##        outervals.append(i[1])
##       
##    
##    metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
##    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
##        (data.get_npoints_max_block(), min(innervals), max(innervals),
##         data.get_dimension_name(0)))
##    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
##        (len(_blockvals), min(_blockvals), max(_blockvals),
##         data.get_dimension_name(1)))#len(_blockvals) = data.get_nblocks()
##    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')
##    metafile.write('#values\n3\n%s'%data.get_dimension_name(2))
##    metafile.close()
