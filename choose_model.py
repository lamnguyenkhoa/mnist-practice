import keras
from keras.layers import Dense, Conv2D, MaxPool2D, Flatten, BatchNormalization, Dropout, Input, Activation
from keras.optimizers import SGD


class ModelEnum:
    HOMEMADE_MODEL = 0
    VGG_MODEL = 1
    RESNET_MODEL = 2


def create_homemade_model(n_label):
    model = keras.Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1)))
    model.add(BatchNormalization())  # keep data in range(0,1)
    model.add(MaxPool2D((2, 2)))  # down-sampling/ reduce size of data
    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(MaxPool2D((2, 2), strides=(2, 2)))
    model.add(Dropout(0.2))  # randomly drop 20% input to prevent over-fitting
    model.add(Flatten())  # flatten into 1d for Dense layers
    model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))  # speedup training and simplify model
    model.add(Dense(n_label, activation='softmax'))  # normalize output into probability distribution
    opti = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opti, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def vgg_block(layer_in, n_filters, n_conv):
    """
    Function for creating a vgg block
    Copied from https://machinelearningmastery.com/how-to-implement-major-architecture-innovations-for-convolutional-neural-networks/
    """
    # add convolutional layers
    for _ in range(n_conv):
        layer_in = Conv2D(n_filters, (3, 3), padding="same", activation='relu', kernel_initializer='he_uniform')(layer_in)
    # add max pooling layer
    layer_in = MaxPool2D((2, 2), strides=(2, 2))(layer_in)
    return layer_in


def create_vgg_model(n_label):
    input_layer = Input(shape=(28, 28, 1))
    vgg_layer1 = vgg_block(input_layer, 32, 2)
    vgg_layer2 = vgg_block(vgg_layer1, 64, 2)
    vgg_layer3 = vgg_block(vgg_layer2, 128, 2)
    flatten_layer = Flatten()(vgg_layer3)
    output_layer = Dense(n_label, activation='softmax')(flatten_layer)
    model = keras.Model(inputs=input_layer, outputs=output_layer)
    opti = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opti, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def residual_module(layer_in, n_filters):
    merge_input = layer_in
    # check if the number of filters needs to be increase, assumes channels last format
    if layer_in.shape[-1] != n_filters:
        merge_input = Conv2D(n_filters, (1,1), padding='same', activation='relu', kernel_initializer='he_normal')(layer_in)
    # conv1
    conv1 = Conv2D(n_filters, (3,3), padding='same', activation='relu', kernel_initializer='he_normal')(layer_in)
    # conv2
    conv2 = Conv2D(n_filters, (3,3), padding='same', activation='linear', kernel_initializer='he_normal')(conv1)
    # add filters, assumes filters/channels last
    layer_out = keras.layers.add([conv2, merge_input])
    # activation function
    layer_out = Activation('relu')(layer_out)
    return layer_out


def create_resnet_model(n_label):
    input_layer = Input(shape=(28, 28, 1))
    resnet_layer1 = residual_module(input_layer, 64)
    flatten_layer = Flatten()(resnet_layer1)
    output_layer = Dense(n_label, activation='softmax')(flatten_layer)
    model = keras.Model(inputs=input_layer, outputs=output_layer)
    opti = SGD(lr=0.1, momentum=0.9, decay=0.01)
    model.compile(optimizer=opti, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def get_model(val, n_label):
    """
    Load a model skeleton to use in training.
    Not to be confused with get_trained_model(), which is used in handwriting_recognition
    :param val:
    :param n_label:
    :return:
    """
    if val == ModelEnum.HOMEMADE_MODEL:
        return create_homemade_model(n_label)
    if val == ModelEnum.VGG_MODEL:
        return create_vgg_model(n_label)
    if val == ModelEnum.RESNET_MODEL:
        return  create_resnet_model(n_label)