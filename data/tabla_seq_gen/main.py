import os
import pandas as pd 
import numpy as np 
import params
import librosa
from scipy import signal
import matplotlib.pyplot as plt


unique_bols = params.unique_bols
ge_dirs = params.ge_dirs
ke_dirs = params.ke_dirs
sample_rate = params.sample_rate

def read_wave_file(filepath):
    y, sr = librosa.load(filepath, sr=None)
    return y, sr

def get_gtOnsets(filepath):
    data = pd.read_csv(filepath, header=None)
    time = data[0].values
    bols = data[1].values
    for i in range(len(bols)):
        bols[i] = bols[i].replace(" ", "")
    return time, bols

def get_onset_time(filepath):
    y, sr = read_wave_file(filepath)
    # y = y/np.max(y)
    window_len = 1024
    window = np.hamming(window_len)
    sig_energy = np.convolve(y**2,window**2,'same')
    sig_energy = sig_energy/max(sig_energy)     #Normalize energy
    onset_time = np.argmax(sig_energy)

    energy_threshold = params.energy_threshold
    sig_energy_thresh = (sig_energy > energy_threshold).astype('float')

    indices = np.nonzero(abs(sig_energy_thresh[1:] - sig_energy_thresh[0:-1]))[0]        
    
    start_indices = [indices[2*i] for i in range(len(indices)/2)]
    end_indices   = [indices[2*i+1] for i in range(len(indices)/2)]
    
    window = y[start_indices[0]: end_indices[0]]

    return window


        
def gen(transcription_file, transcription=True):
    if transcription:
        onset_times, bol_seq = get_gtOnsets(transcription_file)
        length = int(np.max(onset_times)*params.sample_rate + 1000)
        output_wav = np.zeros(length)

        for i in range(len(bol_seq)):
            # import pdb; pdb.set_trace()
            if bol_seq[i].lower() == ge_dirs[0].lower():
                print("1 :Ghe deteceted")
                filenames = os.listdir(params.isolated_drums_dir + ge_dirs[0])
                filepath = params.isolated_drums_dir + ge_dirs[0] + '/' +  filenames[0]
                window = get_onset_time(filepath)
                start = int(onset_times[i]*sample_rate - len(window)/2)
                end = int(onset_times[i]*sample_rate + len(window)/2) + 1
                output_wav[start:end] = window

            if bol_seq[i].lower() == ke_dirs[0].lower():    
                print("2 : Ke deteceted")
                filenames = os.listdir(params.isolated_drums_dir + ke_dirs[0])
                filepath = params.isolated_drums_dir + ke_dirs[0] + '/' +  filenames[0]
                window = get_onset_time(filepath)
                start = int(onset_times[i]*sample_rate - len(window)/2)
                end = int(onset_times[i]*sample_rate + len(window)/2) + 1
                output_wav[start:end] = window            
            
            else:
                for unique_bol in unique_bols: 
                    if bol_seq[i].lower() in unique_bol.lower():
                        print("3: ", bol_seq[i].lower() + " deteceted")
                        filenames = os.listdir(params.isolated_drums_dir + unique_bol)
                        filepath = params.isolated_drums_dir + unique_bol + '/' +  filenames[0]
                        window = get_onset_time(filepath)
                        start = int(onset_times[i]*sample_rate - len(window)/2)
                        end = int(onset_times[i]*sample_rate + len(window)/2) 
                        output_wav[start:end] = window[0:end-start]

    return output_wav        

                
            

transcription_file = params.onset_bol_dir + 'ajr_10_ajr.csv'
output_wav = gen(transcription_file, transcription=True)
librosa.output.write_wav('output.wav', output_wav, params.sample_rate)

# filepath = params.isolated_drums_dir + '/Da/' + 'Da_1_l_1.wav' 
# get_onset_time(filepath)

