"""
A simple 3D Convolutional network. It has 5 convolutional
layers and 3 FC layers, much like Alexnet.

Unfortunately, the architecture described in the paper is
severely lacking in details. Here I use 2D convolution
(with depth as channels) instead of 3D. In addition, I assume:
- The filter sizes
- The strides between convolutional layers
- The pooling size

Based on:
- https://github.com/ehosseiniasl/3d-convolutional-network
- https://www.nature.com/articles/s41746-017-0015-z.pdf
"""

from keras.models import Model
from keras.layers import Input, BatchNormalization, Dense, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D


class AlexNet2DBuilder(object):

    @staticmethod
    def build(input_shape):
        """Create a 3D Convolutional Autoencoder model.

        Parameters:
        - input_shape: Tuple of input shape in the format
            (conv_dim1, conv_dim2, conv_dim3, channels)
        - initial_filter: Initial filter size. This will be doubled
            for each hidden layer as it goes deeper.
        - num_encoding_layers: Number of encoding convolutional +
            pooling layers. The number of decoding
            layers will be the same.

        Returns:
        - A 3D CAD model that takes a 5D tensor (volumetric images
        in batch) as input and returns a 5D vector (prediction) as output.
        """

        if len(input_shape) != 3:
            raise ValueError("Input shape should be a tuple "
                             "(conv_dim1, conv_dim2, conv_dim3)")

        input_img = Input(shape=input_shape, name="cad_input")

        # Conv1 (Output 200 x 200 x 48)
        x = Conv2D(48, (11, 11), activation='relu',
                   padding='same')(input_img)
        x = BatchNormalization()(x)
        x = MaxPooling2D(pool_size=(4, 4), strides=(4, 4))(x)

        # Conv2 (Output 50 x 50 x 64)
        x = Conv2D(64, (5, 5), activation='relu', padding='same')(x)
        x = BatchNormalization()(x)
        x = MaxPooling2D(pool_size=(4, 4), strides=(4, 4))(x)

        # Conv3 (Output 12 x 12 x 96)
        x = Conv2D(96, (3, 3), activation='relu',
                   padding='same')(x)

        # Conv4 (Output 6 x 6 x 128)
        x = Conv2D(128, (3, 3), activation='relu', strides=(2, 2),
                   padding='same')(x)

        # Conv5 (Output 3 x 3 x 128)
        x = Conv2D(256, (3, 3), activation='relu', strides=(2, 2),
                   padding='same')(x)

        # Flatten
        x = MaxPooling2D(pool_size=(2, 2), strides=(1, 1))(x)
        x = Flatten()(x)

        # Fully connected layers
        x = Dense(1000, activation='relu', use_bias=True)(x)
        x = Dense(1000, activation='relu', use_bias=True)(x)
        x = Dense(2, activation='relu', use_bias=True)(x)

        model = Model(inputs=input_img, outputs=x)
        return model


# m = AlexNet3DBuilder.build((200, 200, 24))
# m.summary()
