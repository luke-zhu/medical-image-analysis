"""
Purpose: This script implements maximum intensity projections (MIP). This process involves
taking 3D brain scans, chunking them into three relevant sections, and compressing each section's
maximum values down into a 2D array. When these are recombined, we get an array with the shape
(3, X, Y) — which is ready to be fed directly into standardized Keras architecture with pretrained
feature detection weights from ImageNet/CIFAR10.
"""

import io
import logging

import numpy as np
from matplotlib import pyplot as plt
from google.cloud import storage
from tensorflow.python.lib.io import file_io
import imageio


def authenticate():
    return storage.Client.from_service_account_json(
        './credentials/client_secret.json'
    )


def configure_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def mip_array(array: np.ndarray, type: str) -> np.ndarray:
    to_return = np.zeros((3, len(array[0][0]), len(array[0][0][0])))
    print(to_return.shape)
    for i in range(3):
        print(array[i].shape)
        to_return[i] = np.max(array[i], axis=0)
    return to_return


def crop(arr: np.ndarray, whence: str):
    print(arr.shape)

    if whence == 'numpy':
        to_return = np.zeros((3, 25, len(arr[0]), len(arr[0][0])))
        print(to_return.shape)
        chunk_start = 30
        chunk_end = chunk_start + 25
        inc = 25
    else:
        to_return = np.zeros((3, 21, len(arr[0]), len(arr[0][0])))
        print(to_return.shape)
        chunk_start = 1
        chunk_end = chunk_start + 21
        inc = 21

    for i in range(3):
        to_return[i] = arr[len(arr)-chunk_end:len(arr)-chunk_start]
        chunk_start += inc
        chunk_end += inc
    return to_return


def remove_extremes(arr: np.ndarray):
    a = arr > 270
    b = arr < 0
    arr[a] = -50
    arr[b] = -50
    return arr


def download_array(blob: storage.Blob) -> np.ndarray:
    in_stream = io.BytesIO()
    blob.download_to_file(in_stream)
    in_stream.seek(0)  # Read from the start of the file-like object
    return np.load(in_stream)


def normalize(image, lower_bound=None, upper_bound=None):
    if lower_bound is None:
        lower_bound = image.min()
    if upper_bound is None:
        upper_bound = image.max()

    image[image > upper_bound] = upper_bound
    image[image < lower_bound] = lower_bound

    return (image - image.mean()) / image.std()


def upload_png(arr: np.ndarray, id: str, type: str, bucket: storage.Bucket):
    """Uploads MIP PNGs to gs://elvos/mip_data/<patient_id>/<scan_type>_mip.png.
    """
    try:
        # arr = arr.astype(np.uint8)
        out_stream = io.BytesIO()
        imageio.imwrite(out_stream, arr, format='png')
        out_filename = f'mip_data/{id}/{type}_mip.png'
        print(out_filename)
        out_blob = storage.Blob(out_filename, bucket)
        out_stream.seek(0)
        out_blob.upload_from_file(out_stream)
        print("Saved png file.")
    except Exception as e:
        logging.error(f'for patient ID: {id} {e}')


def save_npy_to_cloud(arr: np.ndarray, id: str, whence: str):
    """Uploads MIP .npy files to gs://elvos/multichannel_mip_data/from_numpy/<patient id>_mip.npy
    """
    try:
        print(f'gs://elvos/multichannel_mip_data/from_{whence}/{id}_mip.npy')
        np.save(file_io.FileIO(f'gs://elvos/multichannel_mip_data/from_{whence}/{id}_mip.npy', 'w'), arr)
    except Exception as e:
        logging.error(f'for patient ID: {id} {e}')


if __name__ == '__main__':
    configure_logger()
    client = authenticate()
    bucket = client.get_bucket('elvos')

    # from numpy directory
    for in_blob in bucket.list_blobs(prefix='numpy/'):

        # blacklist
        if in_blob.name == 'numpy/LAUIHISOEZIM5ILF.npy':
            continue

        logging.info(f'downloading {in_blob.name}')
        input_arr = download_array(in_blob)
        logging.info(f"blob shape: {input_arr.shape}")

        cropped_arr = crop(input_arr, 'numpy')
        not_extreme_arr = remove_extremes(cropped_arr)

        logging.info(f'removed array extremes')
        # create folder w patient ID
        axial = mip_array(not_extreme_arr, 'axial')
        logging.info(f'mip-ed CTA image')
        normalized = normalize(axial, lower_bound=-400)
        # for i in range(3):
        #     plt.figure(figsize=(6, 6))
        #     plt.imshow(axial[i], interpolation='none')
        #     plt.show()
        file_id = in_blob.name.split('/')[1]
        file_id = file_id.split('.')[0]
        save_npy_to_cloud(axial, in_blob.name[6:22], 'numpy')

        logging.info(f'saved .npy file to cloud')

    # from preprocess_luke/training directory
    for in_blob in bucket.list_blobs(prefix='preprocess_luke/training/'):
        if in_blob.name == 'numpy/LAUIHISOEZIM5ILF.npy':
            continue
        logging.info(f'downloading {in_blob.name}')
        input_arr = download_array(in_blob)
        logging.info(f"blob shape: {input_arr.shape}")
        transposed_arr = np.transpose(input_arr, (2, 0, 1))
        logging.info(f'transposed to: {transposed_arr.shape}')

        cropped_arr = crop(transposed_arr, 'luke')
        not_extreme_arr = remove_extremes(cropped_arr)

        logging.info(f'removed array extremes')
        # create folder w patient ID
        axial = mip_array(not_extreme_arr, 'axial')
        logging.info(f'mip-ed CTA image')
        normalized = normalize(axial, lower_bound=-400)
        # for i in range(3):
        #     plt.figure(figsize=(6, 6))
        #     plt.imshow(axial[i], interpolation='none')
        #     plt.show()
        file_id = in_blob.name.split('/')[1]
        file_id = file_id.split('.')[0]
        save_npy_to_cloud(axial, in_blob.name[25:41], 'luke_training')

        logging.info(f'saved .npy file to cloud')

    # from preprocess_luke/validation directory
    for in_blob in bucket.list_blobs(prefix='preprocess_luke/validation/'):

        # blacklist
        if in_blob.name == 'preprocess_luke/validation/LAUIHISOEZIM5ILF.npy':
            continue
        logging.info(f'downloading {in_blob.name}')
        input_arr = download_array(in_blob)
        logging.info(f"blob shape: {input_arr.shape}")
        transposed_arr = np.transpose(input_arr, (2, 0, 1))
        logging.info(f'transposed to: {transposed_arr.shape}')

        cropped_arr = crop(transposed_arr, 'luke')
        not_extreme_arr = remove_extremes(cropped_arr)

        logging.info(f'removed array extremes')
        # create folder w patient ID
        axial = mip_array(not_extreme_arr, 'axial')
        logging.info(f'mip-ed CTA image')
        normalized = normalize(axial, lower_bound=-400)
        # for i in range(3):
        #     plt.figure(figsize=(6, 6))
        #     plt.imshow(axial[i], interpolation='none')
        #     plt.show()
        file_id = in_blob.name.split('/')[1]
        file_id = file_id.split('.')[0]
        save_npy_to_cloud(axial, in_blob.name[27:43], 'luke_validation')

        logging.info(f'saved .npy file to cloud')