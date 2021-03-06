'''
Created on Aug 28, 2016

@author: Wajih-PC
'''
from CNN import Layers
import numpy as np
from scipy.signal import fftconvolve
from util import sigm

def cnnff(net,x):
    n = len(net.layers)
    net.layers[0].A[0] = x.copy();
    inputMaps = 1
    for l in range(1,n):
        if isinstance(net.layers[l],Layers.ConvolutionalLayer):
            for j in range(0,net.layers[l].OutputMaps):
                # Create a temp output map
                # map shape 
                t = np.asarray([net.layers[l].KernelSize - 1 ,net.layers[l].KernelSize - 1, 0])
                s = np.asarray(net.layers[l - 1].A[0].shape)
                z = np.zeros(shape = s-t,dtype = np.float64)
                for i in range(0,inputMaps):    
                    kernel = net.layers[l].K[i,j].copy()
                    # add a dimension to kernel as the data is in MxMxN                    
                    kernel = np.expand_dims(kernel,axis=2)
                    convolutionResult = fftconvolve(net.layers[l-1].A[i],kernel,mode = 'valid')
                    # Zero out very small values, this helps in avoiding overflow error in sigm function in util module                    
                    z = np.add(z,convolutionResult)
                # add bias, pass through nonlinearity
                net.layers[l].A[j] = sigm.sigm(np.add(z,net.layers[l].B[j]))                              
                
            # set number of input maps tp this layers number of output maps
            inputMaps = net.layers[l].OutputMaps        
        elif isinstance(net.layers[l],Layers.ScaleLayer):
            # Downsample
            for j in range(0,inputMaps):
                kernel = np.true_divide(np.ones(shape = (net.layers[l].Scale,net.layers[l].Scale)),net.layers[l].Scale*net.layers[l].Scale)
                kernel = np.expand_dims(kernel,axis=2)                
                v = fftconvolve(net.layers[l-1].A[j],kernel,mode = 'valid')                
                net.layers[l].A[j] = v[:: net.layers[l].Scale, :: net.layers[l].Scale,:];

    # Concatenate all end layer feature maps into vector
    net.fV = None
    for j in range(0,len(net.layers[n-1].A)):
        sa = net.layers[n-1].A[j].shape    
        if net.fV is None:
            net.fV = np.reshape(net.layers[n-1].A[j], newshape =(sa[0]*sa[1], sa[2]),order="F")[:]
        else:          
            net.fV = np.append(net.fV,np.reshape(net.layers[n-1].A[j], newshape =(sa[0]*sa[1], sa[2]),order="F"),axis = 0)[:]   
    # Feedforward into output perceptrons
    net.O = sigm.sigm(np.dot(net.ffW,net.fV)+np.tile(net.ffB,(1,net.fV.shape[1])))
       
    return net 