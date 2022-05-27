from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import Dense, Activation, Conv2D, MaxPooling2D, GlobalMaxPooling2D, BatchNormalization
from tensorflow.keras.optimizers import Adam
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)


class ResnetBlock(Model):
    def __init__(self, filters, strides=1, same_dim=False):
        super().__init__()
        self.filters = filters
        self.strides= strides
        # 是否與輸入層相同維度
        self.same_dim = same_dim

        self.c1 = Conv2D(self.filters, (3,3), strides=self.strides, padding='same', use_bias=False)
        self.b1 = BatchNormalization()
        self.a1 = Activation('relu')

        self.c2 = Conv2D(self.filters, (3,3), strides=self.strides, padding='same', use_bias=False)
        self.b2 = BatchNormalization()

        if not self.same_dim:
            self.down_c1 = Conv2D(self.filters, (1,1), strides=self.strides, padding='same', use_bias=False)
            self.down_b1 = BatchNormalization()

        self.a2 = Activation('relu')

    def call(self, inputs):
        residual = inputs

        # 第一個區塊
        x = self.c1(inputs)
        x = self.b1(x)
        x = self.a1(x)

        #第二個區塊
        x = self.c2(x)
        y = self.b2(x)

        if not self.same_dim:
            residual = self.down_c1(inputs)
            residual = self.b1(residual)

        out = self.a2(y + residual)

        return out

"""
    input shape : (1,300,400,3)
    output shape : (1,300,400,512)
"""

class EncodeNetwork(Model):
    def __init__(self):
        super().__init__()
        self.layerSequential = Sequential()
        self.filters_list = [16,32]

        self.c1 = Conv2D(16, (3, 3), strides=1, padding='same', use_bias=False)
        self.b1 = BatchNormalization()
        self.a1 = Activation('relu')

        for block_id in range(len(self.filters_list)):
            for i in range(2):
                if block_id != 0 and i == 0:
                    layer = ResnetBlock(filters=self.filters_list[block_id],same_dim=False)
                else:
                    layer = ResnetBlock(filters=self.filters_list[block_id],same_dim=True)
                self.layerSequential.add(layer)

        self.layerSequential.build(input_shape=(1,300,400,64))
        self.layerSequential.summary()

    def call(self,input):
        output = self.c1(input)
        output = self.b1(output)
        output = self.a1(output)
        output = self.layerSequential(output)

        return output
