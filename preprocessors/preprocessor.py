import logging
import os

import numpy as np
import pandas as pd
from google.cloud import storage

import preprocessors.parsers as parsers
import preprocessors.transforms as transforms


def preprocess(bucket_name, roi_dir, output_dir):
    """Loads the data from the input directory and saves
    normalized, zero-centered, 200 x 200 x 200 3D renderings
    in output_dir.
    """
    # parsers.unzip_scans(bucket_name)
    # logging.debug('Unzipped data in {}'.format(bucket_name))
    # patient_ids = parsers.load_patient_infos(bucket_name)
    # logging.debug('Loaded patient ids in {}'.format(bucket_name))
    df = pd.read_excel('/home/shared/data/elvos_meta_drop1.xls')

    os.makedirs(output_dir)
    for id_ in df.items():
        try:
            filename = id_ + '.zip'
            _download_blob(bucket_name, filename, filename)
            print('Done')
            return
            slices = parsers.load_scan(path)
            logging.debug('Loaded slices for patient {}'.format(id_))
            scan = _preprocess_scan(slices)
            _save_scan(id_, scan, output_dir)
        except Exception as e:
            # TODO(Luke): Remove after first run
            logging.error('Failed to preprocess {}'.format(id_))
            logging.error(e)

    # Consider doing this step just before training the model
    # normalized = normalize(np.stack(processed_scans))

    _save_info(patient_ids, roi_dir, output_dir)


def _download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


def _preprocess_scan(slices):
    """Transforms the CT slices into a processed 3D numpy array.
    """
    scan = transforms.get_pixels_hu(slices)
    scan = transforms.standardize_spacing(scan, slices)
    # scan = transforms.crop(scan)
    # TODO: Generate an image at this point to verify the preprocessing
    logging.debug(
        'Finished converting to HU, standardizing pixels'
        ' to 1mm, and cropping the array to 200x200x200'
    )
    return scan


def _save_scan(id_, scan, output_dir):
    """Saves the scan for patient id_ in the output_dir
    as a numpy file."""
    outfile = '{}/patient-{}'.format(output_dir, id_)
    np.save(outfile, scan)
    logging.debug(
        'Finished saving scan as a .npy file'
    )


def _save_info(patient_ids, roi_dir, output_dir):
    """Saves labels by matching directory names in roi_dir to
    patient ids. Also saves the bounding boxes.
    """
    columns = [
        'label',
        'centerX', 'centerY', 'centerZ',
        'deviationX', 'deviationY', 'deviationZ'
    ]
    info = pd.DataFrame(index=patient_ids, columns=columns)
    info['label'] = 0  # Set a default

    for name in os.listdir(roi_dir):
        try:
            path = '{}/{}/AnnotationROI.acsv'.format(roi_dir, name)
            center, dev = parsers.parse_bounding_box(path)
            info.loc[name, 'label'] = 1
            info.loc[name, ['centerX', 'centerY', 'centerZ']] = center
            info.loc[name, ['deviationX', 'deviationY', 'deviationZ']] = dev
        except OSError:
            pass

    info.to_csv('{}/labels.csv'.format(output_dir))
