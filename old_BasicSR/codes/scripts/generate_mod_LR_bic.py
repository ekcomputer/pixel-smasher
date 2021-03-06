import os
import sys
import cv2
import numpy as np
import getpass
import pickle
import multiprocessing

try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.util import imresize_np
except ImportError:
    pass

def worker(filename, sourcedir, mod_scale, up_scale, saveHRpath, saveLRpath, saveBicpath):
    # read image
    image = cv2.imread(os.path.join(sourcedir, filename), cv2.IMREAD_UNCHANGED) # apparently, this loads as 8-bit bit depth... Changed!

    ## continue
    width = int(np.floor(image.shape[1] / mod_scale)) # LR width
    height = int(np.floor(image.shape[0] / mod_scale)) # LR height
    # modcrop
    if len(image.shape) == 3:
        image_HR = image[0:mod_scale * height, 0:mod_scale * width, :] # this simply makes the dimenions of the image even if they weren't originally
    else:
        image_HR = image[0:mod_scale * height, 0:mod_scale * width]
    # LR
    image_LR = imresize_np(image_HR, 1 / up_scale, True)
    # bic
    image_Bic = imresize_np(image_LR, up_scale, True) # uses bicubic resampling to recreate the HR image from the LR naively (the GAN will do this better)

    cv2.imwrite(os.path.join(saveHRpath, filename), image_HR) 
    cv2.imwrite(os.path.join(saveLRpath, filename), image_LR)
    cv2.imwrite(os.path.join(saveBicpath, filename), image_Bic)

def generate_mod_LR_bic():
    # set parameters
    up_scale = 4
    mod_scale = 4
    # stretch_multiplier=1 # to increase total dynamic range

    # set data dir
    if getpass.getuser()=='ethan_kyzivat' or getpass.getuser()=='ekaterina_lezine': # on GCP 
        sourcedir = '/data_dir/planet_sub'
        savedir = '/data_dir/planet_sub_LR'
    else: # other
        raise ValueError('input_folder not specified!')
        pass

    saveHRpath = os.path.join(savedir, 'HR', 'x' + str(mod_scale))
    saveLRpath = os.path.join(savedir, 'LR', 'x' + str(up_scale))
    saveBicpath = os.path.join(savedir, 'Bic', 'x' + str(up_scale))

    if not os.path.isdir(sourcedir):
        print('Error: No source data found')
        exit(0)
    if not os.path.isdir(savedir):
        os.mkdir(savedir)

    if not os.path.isdir(os.path.join(savedir, 'HR')):
        os.mkdir(os.path.join(savedir, 'HR'))
    if not os.path.isdir(os.path.join(savedir, 'LR')):
        os.mkdir(os.path.join(savedir, 'LR'))
    if not os.path.isdir(os.path.join(savedir, 'Bic')):
        os.mkdir(os.path.join(savedir, 'Bic'))

    if not os.path.isdir(saveHRpath):
        os.mkdir(saveHRpath)
    else:
        print('It will cover ' + str(saveHRpath))

    if not os.path.isdir(saveLRpath):
        os.mkdir(saveLRpath)
    else:
        print('It will cover ' + str(saveLRpath))

    if not os.path.isdir(saveBicpath):
        os.mkdir(saveBicpath)
    else:
        print('It will cover ' + str(saveBicpath))

    filepaths = [f for f in os.listdir(sourcedir) if f.endswith('.png')]
    num_files = len(filepaths)

    ## load hash
    # f=open("cal_hash.pkl", "rb")
    # hash=pickle.load(f)
    # b=[3,2,4]

    # prepare data with augementation
    n_thread=multiprocessing.cpu_count()
    pool = multiprocessing.Pool(n_thread)
    for i in range(num_files):
        print('No.{} -- Processing {}'.format(i, filepaths[i]))
        pool.apply_async(worker,
                         args=(filepaths[i], sourcedir, mod_scale, up_scale, saveHRpath, saveLRpath, saveBicpath))
    pool.close()
    pool.join()
    print('All subprocesses done.')


if __name__ == "__main__":
    generate_mod_LR_bic()
