# Measurement script for Fristy by Attila Geresdi
# Based on the Measurement program Kun Zuo & Vincent Mourik
# Last updated: 18/01/2013

# We use this script for transport measurements, both DC and AC,
# as a function of 1 or 2 other variables. Its well suited to measure 
# with 1 or 2 Keithleys and/or 1 or 2 Lockins in 2 or 4 terminal geometries.
# If you are a first time user, we recommend scrolling down to the 
# 'initialization' part of the script, we put some usefull comments there.
# Comments/improvements are appreciated.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from numpy import pi, random, arange, size, array, sin, cos, linspace, sinc, sqrt,log10
from time import time, sleep
from shutil import copyfile
from os import mkdir
from os.path import exists
from lib.file_support.spyview import SpyView


import qt
import timetrack
import sys
import numpy as np
import data as d
import traces
import shutil
import os
import re #regular expression

keithley1 = qt.instruments.get('keithley1')
keithley2 = qt.instruments.get('keithley2')
keithley3 = qt.instruments.get('keithley3')
#keithley4 = qt.instruments.get('keithley4')
lockin1 = qt.instruments.get('lockin1')
#lockin2 = qt.instruments.get('lockin2')
#lockin3 = qt.instruments.get('lockin3')
ivvi = qt.instruments.get('IVVI')
triton 	= qt.instruments.get('triton')
#mw = qt.instruments.get('mw')
agilent = qt.instruments.get('mwsource')

    
class majorana():
    
    def __init__(self): 
        self.filename=filename
        self.generator=d.IncrementalGenerator(qt.config['datadir']+'\\'+self.filename,1);
    
    
    # Function generates data file, spyview file and copies the pyton script.
    def create_data(self,x_vector,x_coordinate,x_parameter,y_vector,y_coordinate,y_parameter,z_vector,z_coordinate,z_parameter):
        qt.Data.set_filename_generator(self.generator)
        data = qt.Data(name=self.filename)
        data.add_coordinate(x_parameter+' ('+x_coordinate+')',
                            size=len(x_vector),
                            start=x_vector[0],
                            end=x_vector[-1]) 
        data.add_coordinate(y_parameter+' ('+y_coordinate+')',
                            size=len(y_vector),
                            start=y_vector[0],
                            end=y_vector[-1]) 
        data.add_coordinate(z_parameter+' ('+z_coordinate+')',
                            size=len(z_vector),
                            start=z_vector[0],
                            end=z_vector[-1])
        #data.add_value('Keithley 1/Gain')                    # Processed data
        data.add_value('Keithley 1')                        # Read out of Keithley 1
        data.add_value('Keithley 2')                        # Read out of Keithley 2
        data.add_value('Keithley 3')                        # Read out of Keithley 3
        #data.add_value('Keithley 3')                        # Read out of Keithley 3
        #data.add_value('Keithley 1')                        # Read out of Keithley 2
        #data.add_value('Keithley 2')                        # Read out of Keithley 3
        data.add_value('Lockin 1_X')                          # Read out of Lockin 1 
        data.add_value('Lockin 1_Y')
        data.add_value('Lockin 2_X')                          # Read out of Lockin 2
        data.add_value('Lockin 2_Y')
        data.add_value('Lockin 3_X')                          # Read out of Lockin 3
        data.add_value('Lockin 3_Y')
        data.add_value('Mixing Chamber')                    # Fridge temperature
        data.create_file()                                  # Create data file
        SpyView(data).write_meta_file()                     # Create the spyview meta.txt file
        traces.copy_script(sys._getframe().f_code.co_filename,data._dir,self.filename+'_'+str(self.generator._counter-1))           # Copy the python script into the data folder
        return data
    
    
    # Function reads out relevant data
    def take_data(self,dacx,x):
        
        ivvi.set(dacx,x)                                                            # Set specified dac to specified value, has to be done here because of delays needed for Lockin measurements
        
        if Nkeithleys == 0:
            
            if Nlockins ==0:
                print 'Why are you using this function if you dont want to read out any Keithley or Lockin...'
                qt.msleep(3.0)
                sys.exit()
            
            elif Nlockins == 1:
                qt.msleep(delay2)                                                    # Use explained at bottom of the script
                L1 = lockin1.get_X()                                                 # Read out Lockin1
                value = (L1/GainL1)/amplitude                                        # Process the data
                datavalues = [value,0,0,L1,0]
                qt.msleep(0.01)
            
            elif Nlockins == 2:
                qt.msleep(delay2)                                                    # Use explained at bottom of the script
                L1 = lockin1.get_X()                                                 # Read out Lockin1
                L2 = lockin2.get_X()                                                 # Read out Lockin2
                value = (L1/GainL1)*(GainL2/L2)                                      # Process the data
                datavalues = [value,0,0,L1,L2]
                qt.msleep(0.01)
        
        elif Nkeithleys == 1:
            
            if Nlockins == 0:
                qt.msleep(delay2) 
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1            
                value = K1/GainK1                                                    # Process the data
                datavalues = [value,K1,0,0,0]
                qt.msleep(0.02)
            
            elif Nlockins == 1:
                qt.msleep(delay2)                                                    # Use explained at bottom of the script
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                L1 = lockin1.get_X()                                                 # Read out Lockin1
                value = (L1/GainL1)/accurrent                                        # Process the data
                datavalues = [value,K1,L1,0,0,0,0]
                qt.msleep(0.02)
            
            elif Nlockins == 2:
                qt.msleep(delay2)                                                    # Use explained at bottom of the script
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                L1_X = lockin1.get_X()                # Read out Lockin1
                L1_Y = lockin1.get_Y()
                L2_X = lockin2.get_X()                                                 # Read out Lockin2
                L2_Y = lockin2.get_Y()
                if L2_X == 0:
                    value = 1e9
                else:
                    value = (L1_X/GainL1)/L2_X                                      # Process the data
                datavalues = [value,K1,0,L1_X,L1_Y,L2_X,L2_Y]
                qt.msleep(0.02)
            
        elif Nkeithleys == 2:
            
            if Nlockins == 0:
                qt.msleep(delay2)
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                K2 = keithley2.get_readlastval()                                     # Read out Keithley2
                #K3 = keithley3.get_readlastval()                                     # Read out Keithley3
                value2 = K2/GainK2                                                   #
                value1 = K1/GainK1                                                  # Process the data
                #value = K1/GainK1/dcvoltage
                #if K1 == 0:
                #    value = 1e9
                #else:
                #value = value2/value1
                # if value == 0:
                    # Rvalue = 1e9
                # else:
                    # Rvalue = 1/value
                #t_mc = float(triton.get_MCTemp())
                datavalues = [value1,value2,K1,K2,0,0,0,0,0,0]
                #qt.msleep(0.02)
            
            elif Nlockins == 1:
                qt.msleep(delay2)                                                    # Use explained at bottom of the script
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                K2 = keithley2.get_readlastval()                                     # Read out Keithley2
                L1_X = lockin1.get_X()                                                 # Read out Lockin1
                L1_Y = lockin1.get_Y()                                                 # Read out Lockin1
                value = (L1_X/GainL1)/(amplitude*Irange/100)                                        # Process the data
                #t_mc = float(triton.get_MCTemp())
                datavalues = [value,K1,K2,L1_X,L1_Y,0,0,0,0,0,0]
                qt.msleep(0.02)
            
            elif Nlockins == 2:
                qt.msleep(delay2)                                                    # Use explained at bottom of the script
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                K2 = keithley2.get_readlastval()                                     # Read out Keithley2
                L1_X = lockin1.get_X()                                                 # Read out Lockin1_X
                L1_Y = lockin1.get_Y()
                L2_X = lockin2.get_X()                                                 # Read out Lockin2_X
                L2_Y = lockin2.get_Y()
                if L2_X == 0:
                    value = 1e9
                else:
                    value = (L1_X/GainL1)/(L2_X/GainL2)                                      # Process the data
                #t_mc = float(triton.get_MCTemp())
                datavalues = [value,K1,K2,L1_X,L1_Y,L2_X,L2_Y,0,0,0]
                qt.msleep(0.02)
                
            elif Nlockins == 3:
                qt.msleep(delay2)
                
                L1_X = lockin1.get_X()                                                 # Read out Lockin1
                L1_Y = lockin1.get_Y()
            
                L2_X = lockin2.get_X()                                                 # Read out Lockin2
                L2_Y = lockin2.get_Y()			
            
                K1 = keithley1.get_readlastval()
                K2 = keithley2.get_readlastval()
                #K3 = keithley3.get_readlastval()	
                L3_X = lockin3.get_X()                                                 # Read out Lockin3
                L3_Y = lockin3.get_Y()

                #R=L1_X/GainL1/(L3_X)
                #R2=L2_X/GainL2/(L3_X)
            
                #Rxx = (L1_X/GainL1)/self.applied_current_bias                                           # Process the data
                #Rxy = 0 #(L2_X/GainL2)/self.applied_current_bias
			
                # L3_X = self.applied_current_bias
                # L3_Y = 0
			
                if L3_X !=0: #K2 != 0: 
                    #R1 = 0.5e-3*1e6/K1
                    #R1 = K1/K2*1e7/100                                           # Process the data
                    Rxx = L1_X/L3_X*GainL3/GainL1
                    #R2 = K1/K3*1e6/100
                                        
                    Rxy = L2_X/L3_X*GainL3/GainL2 
                else:
                    Rxx = 1e7
                    #R2 = 1e7
                    Rxy = 0



                if Rxx != 0:
                    Gxx = 12906/Rxx
                    Gd = 12906/(Rxx+abs(Rxy))
                else:
                    Gxx = 1e5
            
                #K1=0
                #K2=0
                #if Nkeithleys == 2:
                #    K1 = keithley1.get_readlastval()
                #    K2 = keithley2.get_readlastval()
                #R=K2/GainK2/self.applied_current_bias
            
                #datavalues = [R,R2,K1,0,0,L1_X,L1_Y,L2_X,L2_Y,L3_X,L3_Y]
                datavalues = [Rxx,Rxy,K1,Gd,Gxx,L1_X,L1_Y,L2_X,L2_Y,L3_X,L3_Y]
                #datavalues = [R1,0,K1,K2,0,L1_X,L1_Y,L2_X,L2_Y,0,0]
                #print "Rxx: ",Rxx,"\t Rxy: ",Rxy
                qt.msleep(0.01)
        
        elif Nkeithleys == 3:
            
            if Nlockins == 0:
                qt.msleep(delay2)
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                K2 = keithley2.get_readlastval()                                     # Read out Keithley2
                K3 = keithley3.get_readlastval()                                     # Read out Keithley3 (Leakage TG)
                value2 = K2/GainK2                                                   #
                value1 = K1/GainK1                                                  # Process the data
                value3 = K3/GainK3
                #value = K1/GainK1/dcvoltage
                #if K1 == 0:
                #    value = 1e9
                #else:
                value = value2/value1
                # if value == 0:
                    # Rvalue = 1e9
                # else:
                    # Rvalue = 1/value
                #t_mc = float(triton.get_MCTemp())
                datavalues = [value1,value2,value3,K1,K2,K3,0,0,0,0]
                #qt.msleep(0.02)
                
            if Nlockins == 1:
                qt.msleep(delay2)
                K1 = keithley1.get_readlastval()                                     # Read out Keithley1
                K2 = keithley2.get_readlastval()                                     # Read out Keithley2
                K3 = keithley3.get_readlastval()                                     # Read out Keithley3 (Leakage TG)
                value2 = K2/GainK2                                                   #
                value1 = K1/GainK1                                                  # Process the data
                L1_X = lockin1.get_X()
                L1_Y = lockin1.get_Y()
                L1_R = lockin1.get_R()
                value_L=(L1_X/GainL1)/(amplitude)
                #value = K1/GainK1/dcvoltage
                #if K1 == 0:
                #    value = 1e9
                #else:
                value = value2/value1
                # if value == 0:
                    # Rvalue = 1e9
                # else:
                    # Rvalue = 1/value
                #t_mc = float(triton.get_MCTemp())
                datavalues = [value_L,value1,value2,K1,K2,K3,L1_X,L1_Y,L1_R,0]
                #qt.msleep(0.02)
            
            
        else:
            print 'You try to run a too complicated experiment...'
            qt.msleep(3.0)
            sys.exit()
        return datavalues
        qt.msleep(0.01)                                                              # Keep GUI responsive
    # Function to read out temperature
    # TODO: readout of AVS
    def read_T(self):
        try: 
            t_mc = float(triton.get_MCTemp())
        except:
            t_mc=0
        
        return t_mc
    
    ################ 1D scans #####################    
    
    # 1D sweep of a single dac
    def _single_dac_sweep(self,xname,dacx,xstart,xend,xsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                                # create data file, spyview metafile, copy script
        
        for x in x_vector:
            datavalues = self.take_data(dacx,x)                                                                                                 # Go to next sweep value and take data
            #datavalues = self.take_data(dacx,-300)
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])                               # write datapoint into datafile
            #print "Gate: ",x,"\t G: ",datavalues[4],"\t Leak: ",datavalues[2]  #"\t Rxx: ",datavalues[0]
        
        data.new_block()
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    
    
    # Repeatedly sweep a single dac n times, n = repetions
    def _repeat_single_dac_sweep(self,xname,dacx,xstart,xend,xsteps,repetions):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(1,repetions,repetions)                                                                                              # this sweep variable is defined to enable 2D plotting in spyview
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'n','repetions',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
        
        counter = 0
        T_init = timetrack.time()
        T_now = 0
        
        for i in arange(repetions):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
          
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],0, 0, 0, 0, 0)  # Note that the current time is stored in the T_mc column                         # write datapoint into datafile
            
            timetrack.remainingtime(starttime,repetions,counter)                                                                                # Calculate and print remaining scantime
            data.new_block()
            T_now = timetrack.time()-T_init

        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()    
    
    
    # 1D sweep of 2 dac's simultaneously; sweep vectors can have arbitrary start and end values.
    def _2dacs_sweep(self,xname,dacx,xstart,xend,mname,dacm,mstart,mend,steps):
        qt.mstart()
                
        # Create sweep vectors
        x_vector = linspace(xstart,xend,steps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                               # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dac
        m_vector = linspace(mstart,mend,steps+1)
        
        for i in arange(len(x_vector)):
            x = x_vector[i]
            m = m_vector[i]
            ivvi.set(dacm,m)                                                                                                                    # Other dac needs to be set before running take_data
            datavalues = self.take_data(dacx,x)                                                                                                 # Go to next sweep value and take data
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                               # write datapoint into datafile
        
        data.new_block()
        data._write_settings_file()
        data.close_file()
        qt.mend()


    # 1D sweep of 3 dac's simultaneously; sweep vectors can have arbitrary start and end values.
    def _3dacs_sweep(self,xname,dacx,xstart,xend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,steps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,steps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                               # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        m_vector = linspace(mstart,mend,steps+1)
        n_vector = linspace(nstart,nend,steps+1)
        
        for i in arange(len(x_vector)):
            x = x_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            ivvi.set(dacm,m)                                                                                                                    # Other dacs needs to be set before running take_data
            ivvi.set(dacn,n)
            datavalues = self.take_data(dacx,x)                                                                                                 # Go to next sweep value and take data
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                               # write datapoint into datafile
        
        data.new_block()
        data._write_settings_file()
        data.close_file()
        qt.mend()
    
    
    # 1D sweep of 4 dac's simultaneously; sweep vectors can have arbitrary start and end values.
    def _4dacs_sweep(self,xname,dacx,xstart,xend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,pname,dacp,pstart,pend,steps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,steps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                               # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        m_vector = linspace(mstart,mend,steps+1)
        n_vector = linspace(nstart,nend,steps+1)
        p_vector = linspace(pstart,pend,steps+1)
        
        for i in arange(len(x_vector)):
            x = x_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            p = p_vector[i]
            ivvi.set(dacm,m)                                                                                                                    # Other dacs needs to be set before running take_data
            ivvi.set(dacn,n)
            ivvi.set(dacp,p)
            datavalues = self.take_data(dacx,x)                                                                                                 # Go to next sweep value and take data
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                               # write datapoint into datafile
        
        data.new_block()
        data._write_settings_file()
        data.close_file()
        qt.mend()
        
        # 1D sweep of 5 dac's simultaneously; sweep vectors can have arbitrary start and end values.
    def _5dacs_sweep(self,xname,dacx,xstart,xend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,pname,dacp,pstart,pend,qname,dacq,qstart,qend,steps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,steps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                               # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        m_vector = linspace(mstart,mend,steps+1)
        n_vector = linspace(nstart,nend,steps+1)
        p_vector = linspace(pstart,pend,steps+1)
        q_vector = linspace(qstart,qend,steps+1) 
        
        for i in arange(len(x_vector)):
            x = x_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            p = p_vector[i]
            q = q_vector[i]
            ivvi.set(dacm,m)                                                                                                                    # Other dacs needs to be set before running take_data
            ivvi.set(dacn,n)
            ivvi.set(dacp,p)
            ivvi.set(dacq,q)
            datavalues = self.take_data(dacx,x)                                                                                                 # Go to next sweep value and take data
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                               # write datapoint into datafile
        
        data.new_block()
        data._write_settings_file()
        data.close_file()
        qt.mend()

        
        # 1D sweep of 11 dacs, all together, same range
    def _11_dacs_sweep(self,xname,dacx,yname,dacy,zname,dacz,kname,dack,lname,dacl,mname,dacm,nname,dacn,oname,daco,pname,dacp,qname,dacq,rname,dacr,xstart,xend,xsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                                # create data file, spyview metafile, copy script
        
        for x in x_vector:
            ivvi.set(dacy,x)
            ivvi.set(dacz,x)
            ivvi.set(dack,x)
            ivvi.set(dacl,x)
            ivvi.set(dacm,x)
            ivvi.set(dacn,x)
            ivvi.set(daco,x)
            ivvi.set(dacp,x)
            ivvi.set(dacq,x)
            ivvi.set(dacr,x)
            datavalues = self.take_data(dacx,x)                                                                                                 # Go to next sweep value and take data
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                               # write datapoint into datafile
        
        data.new_block()
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
        
    #################### 2D scans ####################
    
    # 2D scan of one dac vs another one
    def _dac_vs_dac(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,ysteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacy,y)
            ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _2dacs_vs_dac(self,xname,dacx,xstart,xend,xsteps,x2name,dacx2,x2start,x2end,yname,dacy,ystart,yend,ysteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        x2_vector = linspace(x2start,x2end,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacy,y)
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacx2,x2_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacx2,x2_vector[ii])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _2dacs_vs_dac_squid(self,xname,dacx,xstart,xend,xsteps,x2name,dacx2,x2start,x2end,yname,dacy,ystart,yend,ysteps,sweeprate,dac_reset):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        x2_vector = linspace(x2start,x2end,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z-parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacy,y)
            ivvi.set_parameter_rate(dacx,1,0.01)
            ivvi.set_parameter_rate(dacx2,1,0.01)
            ivvi.set(dacx,dac_reset)
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacx2,dac_reset)
            ivvi.set(dacx2,x2_vector[0])
            ivvi.set_parameter_rate(dacx,sweeprate,1)
            ivvi.set_parameter_rate(dacx2,sweeprate,1)
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacx2,x2_vector[ii])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,x2_vector[ii],datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _2dacs_vs_dac_squid_pm(self,xname,dacx,xstart,xend,xsteps,x2name,dacx2,x2start,x2end,yname,dacy,ystart,yend,ysteps,sweeprate,dac_reset):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        x2_vector = linspace(x2start,x2end,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z-parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacy,y)
            ivvi.set_parameter_rate(dacx,1,0.01)
            ivvi.set_parameter_rate(dacx2,1,0.01)
            ivvi.set(dacx,dac_reset)
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacx2,dac_reset)
            ivvi.set(dacx2,x2_vector[0])
            ivvi.set_parameter_rate(dacx,sweeprate,1)
            ivvi.set_parameter_rate(dacx2,sweeprate,1)
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacx2,x2_vector[ii])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,x2_vector[ii],datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacx2,-1*x2_vector[ii])
                datavalues = self.take_data(dacx,-1*x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(-1*x,y,-1*x2_vector[ii],datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
        
    def _dac_vs_dac_splitted_range(self,xname,dacx,xstart,xend,xsteps,xstart2,xend2,xsteps2,yname,dacy,ystart,yend,ysteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector1 = linspace(xstart,xend,xsteps+1)
        x_vector2 = linspace(xstart2,xend2,xsteps2+1)
        
        x_vector = concatenate([x_vector1,x_vector2])        
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacy,y)
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _dac_vs_rfpower(self,xname,dacx,xstart,xend,xsteps,freq,ystart,yend,ysteps,db_on):
        qt.mstart()
         
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        def db2amp(db):
            amp = 10.0**(db/20.0)
            return amp
        def amp2db(amp):
            db = 20*log10(amp)
            return db
            
        if db_on != 1:
            ystart = db2amp(ystart)
            yend = db2amp(yend)
            y_vector_lin = linspace(ystart,yend,ysteps+1)
            y_vector = amp2db(y_vector_lin)
            data = self.create_data(x_vector,xname,dacx,y_vector,'rfpower','sqrt(P)',z_vector,'none','z_parameter')  
        else:              
            data = self.create_data(x_vector,xname,dacx,y_vector,'rfpower','dBm',z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        agilent.set_frequency(freq)
        #agilent.set_power(-90.0)
        
        agilent.set_status('on')
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            #ivvi.set(dacy,y)
            #ivvi.set(dacx,x_vector[0])
            agilent.set_power(y)
            
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],0,0,0)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
        
        agilent.set_status('off')
        
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _dac_vs_rffreq(self,xname,dacx,xstart,xend,xsteps,power,ystart,yend,ysteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'rffreq','Hz',z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        counter = 0
        
        agilent.set_power(power)
        
        
        agilent.set_status('on')
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            #ivvi.set(dacy,y)
            #ivvi.set(dacx,x_vector[0])
            agilent.set_frequency(y)
            
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],0,0,0)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ysteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
        
        agilent.set_status('off')
        
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    # 2D scan of one dac vs 2 others; the 2 dacs that are stepped together can have arbitrary start and end values
    def _dac_vs_2dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,mname,dacm,mstart,mend,ymsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ymsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dac
        m_vector = linspace(mstart,mend,ymsteps+1)
        
        counter = 0
        
        for i in arange(len(y_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            y = y_vector[i]
            m = m_vector[i]
            ivvi.set(dacy,y)
            ivvi.set(dacm,m)
            ivvi.set(dacx,x_vector[0.0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ymsteps+1,counter)                                                                                # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    
    
    # 2D scan of one dac vs 3 others; the 3 dacs that are stepped together can have arbitrary start and end values
    def _dac_vs_3dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,ymnsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ymnsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        m_vector = linspace(mstart,mend,ymnsteps+1)
        n_vector = linspace(nstart,nend,ymnsteps+1)
        
        counter = 0
        
        for i in arange(len(y_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            y = y_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            ivvi.set(dacy,y)
            ivvi.set(dacm,m)
            ivvi.set(dacn,n)
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ymnsteps+1,counter)                                                                               # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    
    
    # 2D scan of one dac vs 4 others; the 4 dacs that are stepped together can have arbitrary start and end values
    def _dac_vs_4dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,pname,dacp,pstart,pend,ymnpsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ymnpsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        m_vector = linspace(mstart,mend,ymnpsteps+1)
        n_vector = linspace(nstart,nend,ymnpsteps+1)
        p_vector = linspace(pstart,pend,ymnpsteps+1)
        
        counter = 0
        
        for i in arange(len(y_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            y = y_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            p = p_vector[i]
            ivvi.set(dacy,y)
            ivvi.set(dacm,m)
            ivvi.set(dacn,n)
            ivvi.set(dacp,p)
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ymnpsteps+1,counter)                                                                              # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _dac_vs_5dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,pname,dacp,pstart,pend,qname,dacq,qstart,qend,ymnpsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ymnpsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        m_vector = linspace(mstart,mend,ymnpsteps+1)
        n_vector = linspace(nstart,nend,ymnpsteps+1)
        p_vector = linspace(pstart,pend,ymnpsteps+1)
        q_vector = linspace(qstart,qend,ymnpsteps+1)
		
        counter = 0
        
        for i in arange(len(y_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            y = y_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            p = p_vector[i]
            q = q_vector[i]
            ivvi.set(dacy,y)
            ivvi.set(dacm,m)
            ivvi.set(dacn,n)
            ivvi.set(dacp,p)
            ivvi.set(dacq,q)
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ymnpsteps+1,counter)                                                                              # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
        
    # 2D scan of 2dacs vs 5 dacs. Added by Ludo. Still work in progress
    def _2dacs_vs_5dacs(self,xname,dacx,xstart,xend,kname,dack,kstart,kend,xksteps,yname,dacy,ystart,yend,mname,dacm,mstart,mend,nname,dacn,nstart,nend,pname,dacp,pstart,pend,qname,dacq,qstart,qend,ymnpsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xksteps+1)
        y_vector = linspace(ystart,yend,ymnpsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                          # create data file, spyview metafile, copy script
        
        # Define sweep vector for other dacs
        k_vector = linspace(kstart,kend,xksteps+1)
        m_vector = linspace(mstart,mend,ymnpsteps+1)
        n_vector = linspace(nstart,nend,ymnpsteps+1)
        p_vector = linspace(pstart,pend,ymnpsteps+1)
        q_vector = linspace(qstart,qend,ymnpsteps+1)
		
        counter = 0
        
        for i in arange(len(y_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            y = y_vector[i]
            m = m_vector[i]
            n = n_vector[i]
            p = p_vector[i]
            q = q_vector[i]
            ivvi.set(dacy,y)
            ivvi.set(dacm,m)
            ivvi.set(dacn,n)
            ivvi.set(dacp,p)
            ivvi.set(dacq,q)
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,ymnpsteps+1,counter)                                                                              # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()        
    
    # 2D scan of one dac vs another one n times repeated, n = repetions
    def _repeat_dac_vs_dac(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,ysteps,repetions):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = linspace(1,repetions,repetions)
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'n','repetions')                                               # create data file, spyview metafile, copy script
        
        counter = 0
        numloops = repetions*(ysteps+1)
        
        for i in arange(repetions):
            ivvi.set(dacy,y[0])
            ivvi.set(dacx,x[0])
           
            for y in y_vector:
                [starttime, counter] = timetrack.start(counter)
                tstart = timetrack.time()
                ivvi.set(dacy,y)
                ivvi.set(dacx,x_vector[0])
                T_mc = self.read_T()                                                                                                            # Read out mixing chamber temperature 
                qt.msleep(delay1)                                                                                                               # use explained at the bottom of the script
            
                for x in x_vector:
                    datavalues = self.take_data(dacx,x)                                                                                         # Go to next sweep value and take data
                    data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                       # write datapoint into datafile
            
                timetrack.remainingtime(starttime,numloops,counter)                                                                             # Calculate and print remaining scantime
                data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    
    # 2D scan, every sweep consists of 2 times a dac sweep (first one from start to end of the sweep vector, 2nd one backwards from end to start of the sweep vector), this is done as a function of another dac.
    def _fwdbwd_dac_vs_dac(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,ysteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = [0]        
        
        data_fwd = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                      # create data file, spyview metafile, copy script for fwd sweep direction
        x_vector = x_vector[::-1]                                                                                                               # reverse direction of sweep vector to ensure proper spyview metafile
        data_bwd = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,'none','z_parameter')                                      # create data file, spyview metafile, copy script for bwd sweep direction
        x_vector = x_vector[::-1]                                                                                                               # reverse direction sweep vector back to original
        
        
        counter = 0
        numloops = ysteps+1
        
        for y in y_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart=timetrack.time();
            ivvi.set(y_parameter,y)
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            
            for data_loop in (data_fwd, data_bwd):
            
                for x in x_vector:
                    datavalues = self.take_data(dacx,x)                                                                                                      # Go to next sweep value and take data
                    data.add_data_point(x,y,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                       # write datapoint into datafile
                    
                data_loop.new_block()
                
                # Toggle forward / backward by reversing vector
                x_vector = x_vector[::-1]
            
            tstop = timetrack.time()
            timetrack.remainingtime(starttime,numloops,counter)                                                                                 # Calculate and print remaining scantime
            
        for data_loop in (data_fwd, data_bwd):
            data_loop._write_settings_file()                                                                                                    # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
            data_loop.close_file()
            
        qt.mend()

        
    ############### 3D scans ########################
    
    # 3D scan of one dac vs another dac vs another dac
    def _dac_vs_dac_vs_dac(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,ysteps,zname,dacz,zstart,zend,zsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,ysteps+1)
        z_vector = linspace(zstart,zend,zsteps+1)
        
        data = self.create_data(x_vector,xname,dacx,y_vector,yname,dacy,z_vector,zname,dacz)                                                    # create data file, spyview metafile, copy script
        
        counter = 0
        numloops = (zsteps+1)*(ysteps+1)
        
        for z in z_vector:
            ivvi.set(dacz,z)
            
            for y in y_vector:
                [starttime, counter] = timetrack.start(counter)
                tstart = timetrack.time()
                ivvi.set(dacy,y)
                ivvi.set(dacx,x_vector[0])
                T_mc = self.read_T()                                                                                                            # Read out mixing chamber temperature 
                qt.msleep(delay1)                                                                                                               # use explained at the bottom of the script
            
                for x in x_vector:
                    datavalues = self.take_data(dacx,x)                                                                                         # Go to next sweep value and take data
                    data.add_data_point(x,y,z,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                       # write datapoint into datafile
            
                timetrack.remainingtime(starttime,numloops,counter)                                                                             # Calculate and print remaining scantime
                data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

        
    ############### Scans involving other equipment (magnet supply, rf source) #################
    
    # 1D sweep of magnet     
    def _magnet_sweep_X(self,Bstart,Bend,Bsteps):
        qt.mstart()

        # Create sweep vectors
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(B_vector,'B(T)','triton',y_vector,'none','y_parameter',z_vector,'none','z_parameter')                                # create data file, spyview metafile, copy script
        
        #set field in x-direction, wait till finished
        triton.set_field_wait('CART',Bstart,0,0)
        
        print("waiting 5s to set endfield")
        qt.msleep(5)
        
        #set end field, do not wait till finished
        triton.set_field('CART',Bend,0,0)
        print("final field set")
        Bx=Bstart
        qt.msleep(1)
        bsweep = 1
        while bsweep:
            #extract field
            #print("call field")
            #fieldval = re.findall("[-+]?\d*\.\d+|[-+]?\d+", triton.get_field())
                        
            #store field (units T)
            #Bx = float(fieldval[0])
            #By = float(fieldval[1])
            #Bz = float(fieldval[2])
            
            Bx = triton.get_Magnet_C1()
            #print(Bx)
            
            #qt.msleep(0.25)
            
            #print("reading data")
            #T_mc = self.read_T()
            datavalues = self.take_data('dac15',0.0)
            data.add_data_point(Bx,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])
            
            if abs(Bx - Bend) < 0.001:
               bsweep = 0
                
         
            #qt.msleep(.25)
            
            #print("checking for magnetstatus")
            #get status
            #if triton.get_magnetstatus() == 'IDLE':
            #    break

        data.new_block()
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    def _magnet_sweep_Z(self,Bstart,Bend,Bsteps):
        qt.mstart()

        # Create sweep vectors
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(B_vector,'B(T)','triton',y_vector,'none','y_parameter',z_vector,'none','z_parameter')                                # create data file, spyview metafile, copy script
        
        #set field in x-direction, wait till finished
        triton.set_field_wait('CART',0,0,Bstart)
        
        print("waiting 5s to set endfield")
        qt.msleep(5)
        
        #set end field, do not wait till finished
        triton.set_field('CART',0,0,Bend)
        print("final field set")
        Bz=Bstart
        qt.msleep(1)
        bsweep = 1
        while bsweep:
            #extract field
            #print("call field")
            #fieldval = re.findall("[-+]?\d*\.\d+|[-+]?\d+", triton.get_field())
                        
            #store field (units T)
            #Bx = float(fieldval[0])
            #By = float(fieldval[1])
            #Bz = float(fieldval[2])
            
            Bz = triton.get_Magnet_C3()
            #print(Bx)
            
            #qt.msleep(0.25)
            
            #print("reading data")
            #T_mc = self.read_T()
            datavalues = self.take_data('dac15',0.0)
            data.add_data_point(Bz,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])
            
            if abs(Bz - Bend) < 0.001:
               bsweep = 0
                
         
            #qt.msleep(.25)
            
            #print("checking for magnetstatus")
            #get status
            #if triton.get_magnetstatus() == 'IDLE':
            #    break

        data.new_block()
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    
        # sweep of magnet 2D    
    def _magnet2D_sweep(self,Bstart,Bend,Bsteps,alpha):
        qt.mstart()
        
        #RampRateX = 0.00348                                                                                                                 #Ramp rates in T/sec. delay time after sweeping is adjusted accordingly
        #RampRateY = 0.00149
        #RampRateZ = 0.004
        # Create sweep vectors
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(B_vector,'B(T)','triton',y_vector,'none','y_parameter',z_vector,'none','z_parameter')                                # create data file, spyview metafile, copy script
        
        for B in B_vector:
            #[starttime, counter] = timetrack.start(counter)
            #tstart = timetrack.time()
               
            T_mc = self.read_T()                                                                                                               # Read out mixing chamber temperature             
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script            
            datavalues = self.take_data('dac15',0.0)        #dac that we don't use                                                                                     # Take data at fixed value given by dataval
            data.add_data_point(B,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile

            #timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    
    # To scan a dac as a function of B
    def _dac_vs_magnet(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Bx,By,Bz):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            if dir == 'X':
                triton.set_field_wait('CART',B,By,Bz)
            elif dir == 'Y':
                triton.set_field_wait('CART',Bx,B,Bz)
            elif dir == 'Z':
                triton.set_field_wait('CART',Bx,By,B) 
            elif dir == 'A':               #field perpendicular to the substrate. alignment angle is alpha
                # if alpha != magnet.get_alpha()
                    # magnet.set_alpha(alpha)
                # if phi != magnet.get_phi()
                    # magnet.set_phi(phi)
                # if B != magnet.get_field()    
                    # magnet.set_field(B)
                #if Boffset != 0
                    #Bxy = B*sin(phi*pi/180.0)
                    #alpha = alpha - (180.0/pi)*arctan(Boffset/Bxy))
                    #B = copysign(sqrt(B^2+Boffset^2),B)
                #magnet.set_field_XYZ(B,alpha,phi,Boffset,OffsetAlpha)               
                triton.set_field_wait('SPH', B , alpha*pi/180.0 , phi*pi/180.0)
            ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _3x_dac_vs_magnet_K5(self,xname,dacx,yname,dacy,zname,dacz,xstart,xend,xsteps,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Bx,By,Bz):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            if dir == 'X':
                triton.set_field_wait('CART',B,By,Bz)
            elif dir == 'Y':
                triton.set_field_wait('CART',Bx,B,Bz)
            elif dir == 'Z':
                triton.set_field_wait('CART',Bx,By,B) 
            elif dir == 'A':               #field perpendicular to the substrate. alignment angle is alpha
                # if alpha != magnet.get_alpha()
                    # magnet.set_alpha(alpha)
                # if phi != magnet.get_phi()
                    # magnet.set_phi(phi)
                # if B != magnet.get_field()    
                    # magnet.set_field(B)
                #if Boffset != 0
                    #Bxy = B*sin(phi*pi/180.0)
                    #alpha = alpha - (180.0/pi)*arctan(Boffset/Bxy))
                    #B = copysign(sqrt(B^2+Boffset^2),B)
                #magnet.set_field_XYZ(B,alpha,phi,Boffset,OffsetAlpha)               
                triton.set_field_wait('SPH', B , alpha*pi/180.0 , phi*pi/180.0)
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacy,0)
            ivvi.set(dacz,0)
			
			#T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])                           # write datapoint into datafile            
            ivvi.set(dacx,0)
            ivvi.set(dacy,0)

            for x in x_vector:
                datavalues = self.take_data(dacy,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])                           # write datapoint into datafile
            ivvi.set(dacx,0)
            ivvi.set(dacy,0)
	
            for x in x_vector:
                datavalues = self.take_data(dacz,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
		
    def _dac_vs_magnet_2dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Bx,By,Bz):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','triton',z_vector,'none','z-parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            if dir == 'X':
                triton.set_field_wait('CART',B,By,Bz)
            elif dir == 'Y':
                triton.set_field_wait('CART',Bx,B,Bz)
            elif dir == 'Z':
                triton.set_field_wait('CART',Bx,By,B) 
            elif dir == 'A':               #field perpendicular to the substrate. alignment angle is alpha
                # if alpha != magnet.get_alpha()
                    # magnet.set_alpha(alpha)
                # if phi != magnet.get_phi()
                    # magnet.set_phi(phi)
                # if B != magnet.get_field()    
                    # magnet.set_field(B)
                #if Boffset != 0
                    #Bxy = B*sin(phi*pi/180.0)
                    #alpha = alpha - (180.0/pi)*arctan(Boffset/Bxy))
                    #B = copysign(sqrt(B^2+Boffset^2),B)
                #magnet.set_field_XYZ(B,alpha,phi,Boffset,OffsetAlpha)               
                triton.set_field_wait('SPH', B , alpha*pi/180.0 , phi*pi/180.0)
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacy,y_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacy,y_vector[ii])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,y_vector[ii],datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

  # To scan a dac as a function of B
    def _dac_vs_magnet_squid(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Bx,By,Bz,sweeprate):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            if dir == 'X':
                triton.set_field_wait('CART',B,By,Bz)
            elif dir == 'Y':
                triton.set_field_wait('CART',Bx,B,Bz)
            elif dir == 'Z':
                triton.set_field_wait('CART',Bx,By,B) 
            elif dir == 'A':               #field perpendicular to the substrate. alignment angle is alpha      
                triton.set_field_wait('SPH', B , alpha*pi/180.0 , phi*pi/180.0)
            ivvi.set_parameter_rate(dacx,5,0.2)
            ivvi.set(dacx,0)
            ivvi.set(dacx,x_vector[0])
            ivvi.set_parameter_rate(dacx,sweeprate,50)
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _dac_vs_magnet_squid_2dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Bx,By,Bz,sweeprate):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            if dir == 'X':
                triton.set_field_wait('CART',B,By,Bz)
            elif dir == 'Y':
                triton.set_field_wait('CART',Bx,B,Bz)
            elif dir == 'Z':
                triton.set_field_wait('CART',Bx,By,B) 
            elif dir == 'A':               #field perpendicular to the substrate. alignment angle is alpha      
                triton.set_field_wait('SPH', B , alpha*pi/180.0 , phi*pi/180.0)
            ivvi.set_parameter_rate(dacx,sweeprate,1)
            ivvi.set(dacx,0)
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacy,0)
            ivvi.set(dacy,y_vector[0])
            ivvi.set_parameter_rate(dacx,sweeprate,1)
            
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacy,y_vector[ii])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,y_vector[ii],datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    def _dac_vs_magnet_YZangle(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Btotal,By=0,Bz=0):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        angle_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,angle_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for Bangle in angle_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacx,x_vector[0])

            if dir == 'YZangle':               #field perpendicular to the substrate. alignment angle is alpha
                # if alpha != magnet.get_alpha()
                    # magnet.set_alpha(alpha)
                # if phi != magnet.get_phi()
                    # magnet.set_phi(phi)
                # if B != magnet.get_field()    
                    # magnet.set_field(B)
                #if Boffset != 0
                    #Bxy = B*sin(phi*pi/180.0)
                    #alpha = alpha - (180.0/pi)*arctan(Boffset/Bxy))
                    #B = copysign(sqrt(B^2+Boffset^2),B)
                #magnet.set_field_XYZ(B,alpha,phi,Boffset,OffsetAlpha)               
                triton.set_field_wait('SPH', Btotal, pi/2, Bangle*pi/180.0) #(B,0,0) means Bz=B; (B,0,pi) means Bz=-B; (B,0,pi/2) means Bx=B,  (B,pi/2,pi/2) means By=B
            #ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,Bangle,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    def _dac_vs_magnet_YZangle_2dacs(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Btotal,By=0,Bz=0):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = linspace(ystart,yend,xsteps+1)
        angle_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,angle_vector,'B (T)','triton',z_vector,'none','z-parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for Bangle in angle_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacx,x_vector[0])
            ivvi.set(dacy,y_vector[0])

            if dir == 'YZangle':               #field perpendicular to the substrate. alignment angle is alpha            
                triton.set_field_wait('SPH', Btotal, pi/2, Bangle*pi/180.0) #(B,0,0) means Bz=B; (B,0,pi) means Bz=-B; (B,0,pi/2) means Bx=B,  (B,pi/2,pi/2) means By=B
            #ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for ii,x in enumerate(x_vector):
                ivvi.set(dacy,y_vector[ii])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,Bangle,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
  
    def _dac_vs_magnet_XZangle(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Btotal,By=0,Bz=0):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        angle_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,angle_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for Bangle in angle_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacx,x_vector[0])

            if dir == 'XZangle':               #field perpendicular to the substrate. alignment angle is alpha
                # if alpha != magnet.get_alpha()
                    # magnet.set_alpha(alpha)
                # if phi != magnet.get_phi()
                    # magnet.set_phi(phi)
                # if B != magnet.get_field()    
                    # magnet.set_field(B)
                #if Boffset != 0
                    #Bxy = B*sin(phi*pi/180.0)
                    #alpha = alpha - (180.0/pi)*arctan(Boffset/Bxy))
                    #B = copysign(sqrt(B^2+Boffset^2),B)
                #magnet.set_field_XYZ(B,alpha,phi,Boffset,OffsetAlpha)               
                triton.set_field_wait('SPH', Btotal, 0, Bangle*pi/180.0) #(B,0,0) means Bz=B; (B,0,pi) means Bz=-B; (B,0,pi/2) means Bx=B; (B,pi/2,pi/2) means By=B
            #ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,Bangle,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

    def _dac_vs_magnet_XYangle(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,dir,alpha,phi,Boffset,OffsetAlpha,Btotal,By=0,Bz=0):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        angle_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,angle_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for Bangle in angle_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacx,x_vector[0])

            if dir == 'XYangle':               #field perpendicular to the substrate. alignment angle is alpha          
                triton.set_field_wait('SPH', Btotal, Bangle*pi/180.0, pi/2) #(B,0,0) means Bz=B; (B,0,pi) means Bz=-B; (B,0,pi/2) means Bx=B; (B,pi/2,pi/2) means By=B
            #ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,Bangle,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7],datavalues[8],datavalues[9],datavalues[10])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()        
        
    def _2dacs_vs_magnet_XYZangle(self,xname,dacx,xstart,xend,xsteps,x2name,dacx2,x2start,x2end,alphastart,alphaend,alphasteps,phistart,phiend,dir,Btotal):
        qt.mstart()
        # Calculate start and end point in cartesian coordinates
        BX1=cos(alphastart*pi/180.0)*sin(phistart*pi/180.0)
        BY1=sin(alphastart*pi/180.0)*sin(phistart*pi/180.0)
        BZ1=cos(phistart*pi/180.0)
        
        BX2=cos(alphaend*pi/180.0)*sin(phiend*pi/180.0)
        BY2=sin(alphaend*pi/180.0)*sin(phiend*pi/180.0)
        BZ2=cos(phiend*pi/180.0)
        
        #Interpolate the cartesian values
        BX_vector=linspace(BX1,BX2,alphasteps+1)
        BY_vector=linspace(BY1,BY2,alphasteps+1)
        BZ_vector=linspace(BZ1,BZ2,alphasteps+1)
        
        #Normalize every vector.
        B_vector=[]
             
        for ii,BX in enumerate(BX_vector):
            BR=sqrt(BX_vector[ii]**2+BY_vector[ii]**2+BZ_vector[ii]**2)
            BX_vector[ii]=BX_vector[ii]*Btotal/BR
            BY_vector[ii]=BY_vector[ii]*Btotal/BR
            BZ_vector[ii]=BZ_vector[ii]*Btotal/BR
            B_vector.append([BX_vector[ii],BY_vector[ii],BZ_vector[ii]])
            
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        x2_vector = linspace(x2start,x2end,xsteps+1)
        #angle_vector = linspace(Bstart,Bend,Bsteps+1)
        #phi_vector = linspace(phistart,phiend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,BX_vector,'B(T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
              
        counter = 0
        
        for bb,B_angle in enumerate(B_vector):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            ivvi.set(dacx,x_vector[0])

            if dir == 'XYZangle':               #field perpendicular to the substrate. alignment angle is alpha            
                triton.set_field_wait('CART', BX_vector[bb], BY_vector[bb], BZ_vector[bb]) #(B,0,0) means Bz=B; (B,0,pi) means Bz=-B; (B,0,pi/2) means Bx=B; (B,pi/2,pi/2) means By=B
            #ivvi.set(dacx,x_vector[0])
            #T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for dd,x in enumerate(x_vector):
                ivvi.set(dacx2,x2_vector[dd])
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,bb,x2_vector[dd],B_angle[0],B_angle[1],B_angle[2],datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5],datavalues[6],datavalues[7])                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,alphasteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    def _dac_vs_magnet2D(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,alpha):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','triton',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
        
        counter = 0
        
        magnet.set_alpha(alpha)
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            magnet.set_field(B)               
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay3)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    # To sweep a dac as a function of B, every sweep consists of 2 times a dac sweep (first one from start to end of the sweep vector, 2nd one backwards from end to start of the sweep vector).
    def _fwdbwd_dac_vs_B(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]        
        
        data_fwd = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','kepco',z_vector,'none','z_parameter')                                 # create data file, spyview metafile, copy script for fwd sweep direction
        x_vector = x_vector[::-1]                                                                                                               # reverse direction of sweep vector to ensure proper spyview metafile
        data_bwd = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','kepco',z_vector,'none','z_parameter')                                 # create data file, spyview metafile, copy script for bwd sweep direction
        x_vector = x_vector[::-1]                                                                                                               # reverse direction sweep vector back to original
        
        
        counter = 0
        numloops = ysteps+1
        
        for B in B_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart=timetrack.time();
            kepco.set_B(B)                                                                                                                      # Specific for kepco as magnet supply
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            
            for data_loop in (data_fwd, data_bwd):
            
                for x in x_vector:
                    datavalues = self.take_data(dacx,x)                                                                                         # Go to next sweep value and take data
                    data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                       # write datapoint into datafile
                    
                data_loop.new_block()
                
                # Toggle forward / backward by reversing vector
                x_vector = x_vector[::-1]
            
            tstop = timetrack.time()
            timetrack.remainingtime(starttime,numloops,counter)                                                                                 # Calculate and print remaining scantime
            
        for data_loop in (data_fwd, data_bwd):
            data_loop._write_settings_file()                                                                                                    # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
            data_loop.close_file()
            
        qt.mend()
        
    
    # Scan a dac as a function of B, while at the same time another dac is stepped linearly, this allows to correct a bit for features affected by both gate and B field so they don't move much.
        
    def _dac_vs_dacmagnet(self,xname,dacx,xstart,xend,xsteps,yname,dacy,ystart,yend,Bstart,Bend,Bsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B (T)','kepco',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
        
        # Create sweep vector for the dac that needs to be stepped together with B
        y_vector = linspace(ystart,yend,Bsteps+1)
        
        counter = 0
        
        for i in arange(len(B_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            B = B_vector[i]
            y = y_vector[i]
            kepco.set_B(B)                                                                                                                      # Specific for kepco as magnet supply
            ivvi.set(dacy,y)
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature 
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
        
    
    # dac vs rf power, to do power dependence of Shapiro steps. rf power is stepped with non-uniform steps following P^2 ~ Vrf. Function only works well if you start the sweep at the lowest power.
    
    def _dac_vs_rfpower2(self,xname,dacx,xstart,xend,xsteps,Pstart,Pend,Psteps,freq):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        
        # P vector needs to have quadratic shape
        yend = (Pend-Pstart)*(Pend-Pstart)
        y_vector = linspace(0,yend,Psteps+1)
        P_vector = sqrt(y_vector)+Pstart
        
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,P_vector,'Prf (dB)','MW source',z_vector,'none','z_parameter')                               # create data file, spyview metafile, copy script
        
        counter = 0
        
        # initialization of MW source
        mw.set_power(-20.0)
        mw.set_frequency(freq)
        mw.set_status('ON')
        
        for P in P_vector:
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            mw.set_power(P)                                                                                                                     # Set mw power
            ivvi.set(dacx,x_vector[0])
            T_mc = self.read_T()                                                                                                                # Read out mixing chamber temperature
            qt.msleep(delay1)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,P,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],T_mc)                           # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Psteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
        
        mw.set_status('OFF')
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    
        
        
#################### INITIALIZATION #########################

# DON'T SKIP THIS PART, ITS CRUCIAL FOR PROPER MEASUREMENTS AND DATA PROCESSING!!!

# Gains and ranges
# Please set the gains and ranges before starting measurements. This ensures proper scaling of axis and data in Spyview.
# Make sure that you put the right gain at the right Keithley/Lockin.
GainK1=1e2                # Gain for Keitley 1 - M1b module 
GainK2=1e2                # Gain for Keitley 2 N/A: high voltage source, 1uA/V
GainK3=1e0               # Gain keithley 3. leakage current here.
GainL1=1e3                # Gain for Lockin 1 - M1b module @ 1M and x1
GainL2=1e6                  # Gain for Lockin 2 - N/A
GainL3=1e6
Vrange=10e-3                    # voltage range in V/V - S3b module
Irange=1000e-9                     # current range in A/V - S4m module
TGrange=30                       # Gate range in V/V
BGrange=15                       # Gate range in V/V

# Measurement setup:
#       -Current-biased with K1
#S0 settings: 50 KHz; 50 kHz
#S3b settings: (10m) N/A
#S4m settings: 100 nA/V; on; v2=-v4
#S1h settings: 15V/V
#S1f settings:
#M2b settings: 1k, dc
#M1b settings: Low noise; 2=gnd; off; 1M and x1
#M2m settings: 1e0 V/V; DC 
#M0 settings: Out1: 10 kHz; Out2: 10 kHz;
#External LP filter box: NONE (1 kHz on Keithley1-2700; Moving avg.10 times)

print '\nGainK1='+`GainK1`+'\t\tGain for Keithley 1\nGainK2='+`GainK2`+'\t\tGain for Keithley 2\nGainL1='+`GainL1`+'\t\tGain for Lockin 1\nGainL2='+`GainL2`+'\t\tGain for Lockin 2\nVrange='+`Vrange`+'\t\tVoltage range in V/V\nIrange='+`Irange`+'\t\tCurrent range in A/V\nBGrange='+`BGrange`+'\t\tGate range in V/V\n'
s=raw_input("Ensure smooth dataprocessing in spyview by checking if gains, Vrange, Irange and BGrange are stored correct. Press enter to continue, press any other key and enter to stop: ")
if s!='':
    print '\nVery kind of you to avoid future data processing problems.'
    time.sleep(3.0)
    sys.exit()

# Please update the number of Keithleys/Lockins used in the measurement, this ensures proper data readout and storage
# Remark: In the program its assumed that if you use a single Keithley, this one is Keithley 1. Same for the lockins.
# To ensure proper data processing, we encourage reading the 'take_data' function above.
Nkeithleys = 3
Nlockins = 0

# Set Keithley averaging
#keithley1.set_nplc(5)
#keithley2.set_nplc(10) 
keithley1.set_autorange(0)
keithley2.set_autorange(0)

#set dc/ac current
#accurrent = 1e-9
'''
amplitude=12e-6 #peak to peak amplitude set on lockin in volt. Conversion to excitation *10^-4
lockin1.set_frequency(27.77)
lockin1.set_amplitude(amplitude/(2*np.sqrt(2)*Vrange*1e-2))
lockin1.set_sensitivity(16)
lockin1.set_tau(9)
#ivvi.set_dac1(4+62)
'''
#set dc voltageivvi
#dcvoltage = 100e-6
#ivvi.set_dac2(100+30)


# This delay is needed at the beginning of a sweep, a good value is ~ 10*tau. If you don't use it, first few datapoints of the sweep will be weird. 
# Its safe to put it to 0 for Keithley measurements. 

delay1 = 5.0   #(10.0 for gate scans)                         

# Delay after setting dac during sweep, you should at least wait 1.5*tau, longer is better. This avoids integration over the previous dac value.
delay2 = 0.01 #0.3, (1.0 for gate scans)
#Delay for magnetic field sweeps. In order to prevent excessive hea ting, we wait some time before starting inner loop after the magnetic field settled.
delay3 = 10.0                                      

#agilent = qt.instruments.create('agilent', 'HP_8657B', address='GPIB0::7', reset=False)

filename= 'JJ_SQUID_gates_SQUID_6_7_2Vgate_dacmagnet'


#################### MEASUREMENTS #########################
#Note: dac single step is 0.06103515625 mV (4V range over 16 bit)
m = majorana()

ivvi.set_parameter_rate('dac1',5,.2) 
ivvi.set_parameter_rate('dac2',10,50) 
#ivvi.set_parameter_rate('dac3',0.1,10) #Vgate 15V/V


ivvi.set_parameter_rate('dac6',2,10) #TGate 5V/V
ivvi.set_parameter_rate('dac7',2,10) #Vgate 5V/V
ivvi.set_parameter_rate('dac8',2,10) #Bgate 5V/V




'''
triton.set_Magnet_Sweeprate(0.025) #Tesla per minute
#triton.set_field_wait('CART',0,0,-5.0)
#m._magnet_sweep_Z(7.5,10.0,2500)
triton.set_field_wait('CART',0,0,0.005)
triton.set_Magnet_Sweeprate(0.0025) #Tesla per minute

ivvi.set_dac6(0) # Tgate. pinchoff at -1100
ivvi.set_dac7(0) # Vgate. pinchoff at -900
ivvi.set_dac8(0) # Bgate. pinchoff at -1100
m._dac_vs_magnet('Ibias (1uA/V)','dac1',
				-400,400,400,
				0.002,-0.004,120,
				'Z',0,0,0,0,
				0,0,0)	
'''
#ivvi.set_dac2(100) # set voltage bias.
#ivvi.set_dac2(-30)
#ivvi.set_dac6(0) # Tgate. pinchoff at -1100
#ivvi.set_dac7(0) # Vgate. pinchoff at -900
#ivvi.set_dac8(0) # Bgate. pinchoff at -1100                      #name + dac #start # end #nr of steps
                      #name + dac #start # end #nr of steps
Imagnet_source=2e-2					  
dacmagnet=11.6583/Imagnet_source*1000
ivvi.set_dac3(0) # vgate SQUID 6 small 15V/V
ivvi.set_dac4(0) # vgate SQUID 6&7 big 5V/V

for i in range(-240,60,25):
	ivvi.set_dac4(i)
	m._dac_vs_dac('Ibias(1uA/V)','dac1',-300,300,300,
		    'Imagnet(20mA/V)','dac2',-0.060e-3*dacmagnet,0.06e-3*dacmagnet,120)				
for i in range(-50,1,5):
	ivvi.set_dac3(i)
	m._dac_vs_dac('Ibias(1uA/V)','dac1',-300,300,600,
		    'Imagnet(20mA/V)','dac2',-0.060e-3*dacmagnet,0.06e-3*dacmagnet,120)
ivvi.set_dacs_zero()
#ivvi.set_dac3(12.5)
#m._dac_vs_dac('Ibias(1uA/V)','dac1',-300,300,200,
#                'Imagnet(20mA/V)','dac2',-0.030e-3*dacmagnet,0.03e-3*dacmagnet,60)	
				
#m._dac_vs_dac('Ibias(100nA/V)','dac1',-1000,1000,200,
#                'Imagnet(20mA/V)','dac2',-3.4e-3*dacmagnet,3.4e-3*dacmagnet,80)				
#ivvi.set_dac1(1000) #1mV/V

#ivvi.set_dac1(55)
#ivvi.set_dac2(-0.01e-3*dacmagnet)
#m._single_dac_sweep('Vgate(15V/V)', 'dac3',0/15,-3000/15, 400)		
	
#Baselmans experiment, Vbias symmetric applied. Currnet measures is through the normal leads.
 #Tesla per minute

#ivvi.set_dac7(0)

'''
agilent.set_status('on')
agilent.set_frequency(3.464e9)
agilent.set_power(-9)
'''
#ivvi.set_dac2(0)
#m._dac_vs_dac('Ibias(10uA/V)','dac1',-1000,1000,400,
#             'VGate(5mV/V)','dac7',-300,-600,15) 	
 
 
#for i in range(300,601,20):
#	ivvi.set_dac7(-i)
#	m._dac_vs_dac('Ibias(1uA/V)','dac1',-200,200,200,
#              'Vcont(10mV/V)','dac2',-10,140,100) 	

			  
#agilent.set_status('off')


#ivvi.set_dac2(0)
#m._dac_vs_rffreq('Ibias(1uA/V)','dac1',0,300,150,0,3.44e9,3.48e9,10)
#agilent.set_status('off')
'''
for i in range(0,110,10):
	ivvi.set_dac2(i)
	m._dac_vs_rfpower('Ibias(1uA/V)','dac1',-500,500,500,3.464e9,-20,0,40,0)
'''
'''
B_offset=-0.0012
triton.set_Magnet_Sweeprate(0.0025)
triton.set_field_wait('CART',0,0,B_offset)
#ivvi.set_dac7(0)
m._dac_vs_magnet('Ibias (1uA/V)','dac1',
				-200,200,200,
				B_offset-50e-6, B_offset+50e-6,20,
				'Z',0,0,0,0,
				0,0,0)				
'''			

#ivvi.set_dacs_zero()
#ivvi.set_dac2(1000) #1mV/V
#m._single_dac_sweep('IBias(10uA/V)', 'dac1',-1000,1000, 400)                        #name + dac #start # end #nr of steps

#ivvi.set_dac2(1000) #1mV/V
#m._single_dac_sweep('Vgate(5V/V)', 'dac7',-1000,0, 500) 

'''
ivvi.set_dac6(-200) # Tgate. pinchoff at -1100
ivvi.set_dac7(0) # Vgate. pinchoff at -900
ivvi.set_dac8(0) # Bgate. pinchoff at -1100
'''
#m._repeat_single_dac_sweep('Ibias(100nA/V)','dac1',-1000,1000,100,10)

		
