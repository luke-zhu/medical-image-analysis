import logging
import numpy as np
import pandas as pd


def configure_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def process_labels():
    positives_df = pd.read_csv(
        'ELVO_Annotator_Key_Positives.csv')

    positives_df.drop([0, 1, 2])
    positives_df.drop(positives_df.columns[0], axis=1)
    positives_df = positives_df.filter(items=['Anon ID',
                                              'Location of occlusion/s'])
    logging.info(positives_df)
    negatives_df = pd.read_csv(
        'ELVO_Annotator_Key_Negatives.csv'
    )
    logging.info(negatives_df)
    to_add = {}
    for index, row in negatives_df.iterrows():
        patient_id = row[0]
        to_add[patient_id] = np.zeros(7)

    """
    Key for one-hot encoding types of strokes:
    idx 0: L MCA
    idx 1: R MCA
    idx 2: L ICA
    idx 3: R ICA
    idx 4: L Vertebral
    idx 5: R Vertebral
    idx 6: Basilar
    """
    for index, row in positives_df.iterrows():
        patient_id = row[0]
        occlusion_type = row[1].lower()
        occlusion_label = np.zeros(7)
        print("ID: " + patient_id
              + "\nOcclusion type: " + occlusion_type)

        # L MCAs
        if 'l m' in occlusion_type:
            occlusion_label[0] = 1
        # R MCAs
        if 'r m' in occlusion_type:
            occlusion_label[1] = 1
        # L ICA
        if 'l ica' in occlusion_type:
            occlusion_label[2] = 1
        # R ICA
        if 'r ica' in occlusion_type:
            occlusion_label[3] = 1
        # L Vertebral
        if 'l vert' in occlusion_type:
            occlusion_label[4] = 1
        # R Vertebral
        if 'r vert' in occlusion_type:
            occlusion_label[1] = 1
        # Basilar
        if 'basilar' in occlusion_type:
            occlusion_label[1] = 1

        to_add[patient_id] = occlusion_label

    to_add_df = pd.DataFrame.from_dict(to_add,
                                       orient='index',
                                       columns=['L MCA',
                                                'R MCA',
                                                'L ICA',
                                                'R ICA',
                                                'L Vert',
                                                'R Vert',
                                                'Basilar']
                                       )
    logging.info(to_add_df)

    to_add_df.to_csv(
        'classification_vectors.csv'
    )
    print("Saving file")


def run_preprocess():
    configure_logger()
    process_labels()


if __name__ == '__main__':
    run_preprocess()
