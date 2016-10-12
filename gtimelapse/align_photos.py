import os
import dlib
import glob
import skimage.io
import skimage.transform
import skimage.util.pad
import numpy as np


def pad_square(L, img):
    img_pad = skimage.util.pad(img,
                               ((np.int(np.floor((L - img.shape[0]) / 2.0)),
                                 np.int(np.ceil((L - img.shape[0]) / 2.0))),
                                (np.int(np.floor((L - img.shape[1]) / 2.0)),
                                np.int(np.ceil((L - img.shape[1]) / 2.0))),
                                (0, 0)),
                               'constant',
                               constant_values=0)
    return img_pad


def align_photos(predictor_path,
                 faces_folder_path,
                 output_folder_path='./',
                 pad_size=1000,
                 img_type="jpg"):

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    eyeL = np.arange(36, 42)
    eyeR = np.arange(42, 48)
    index = 0
    eye_target = np.array([[pad_size * .43, pad_size * .4],
                           [pad_size * .57, pad_size * .4]], dtype=np.int)

    for f in glob.glob(os.path.join(faces_folder_path, "*." + img_type)):
        print("Processing file: {}".format(f))
        img = skimage.io.imread(f)
        img = pad_square(pad_size, img)
        dets = detector(img, 1)

        for d in dets:
            shape = predictor(img, d)
            matrix = np.matrix([[p.x, p.y] for p in shape.parts()])
            pad_x_offset = np.int(np.floor((pad_size-img.shape[0])))
            pad_y_offset = np.int(np.floor((pad_size-img.shape[1])))
            eyes = np.array([[matrix[eyeL, 0].mean() + pad_x_offset,
                              matrix[eyeL, 1].mean() + pad_y_offset],
                             [matrix[eyeR, 0].mean() + pad_x_offset,
                              matrix[eyeR, 1].mean() + pad_y_offset]])
            mytf = skimage.transform.estimate_transform('similarity',
                                                        eye_target, eyes)
            img_out = skimage.transform.warp(img, mytf)
            skimage.io.imsave(os.path.join(output_folder_path,
                              '{:04d}'.format(index) + ".jpg"), img_out)
            index += 1
