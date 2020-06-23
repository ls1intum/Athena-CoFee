from keras.callbacks import EarlyStopping
from keras.models import model_from_json, Model, Sequential
from keras.layers import Dense, Input, Dropout, MaxPooling1D, Dot, Conv1D, Flatten
from keras.regularizers import l2
from keras import optimizers
from sklearn.model_selection import train_test_split
import numpy as np
from typing import List
from sklearn.preprocessing import StandardScaler
from .entities import ElmoVector, Embedding, EmbeddingsPair


class SiameseNetwork:

    model: Model = None

    def load_model(self, model_path: str):
        # load json and create model
        json_file = open(model_path + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights(model_path + ".h5")
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])

    def build_siamese_model(self, input_shape):
        initialize_weights = 'he_normal'
        initialize_bias = 'he_normal'

        # define the tensors for the two input vectors
        left_input = Input(input_shape)
        right_input = Input(input_shape)

        # define network architecture
        model = Sequential()

        model.add(Conv1D(32, 3, strides=1, padding='same', activation='relu', input_shape=input_shape,
                         kernel_initializer=initialize_weights, kernel_regularizer=l2(2e-4)))
        model.add(MaxPooling1D(pool_size=2, strides=2, padding='same'))
        model.add(Dropout(0.25))

        model.add(Conv1D(64, 3, strides=1, padding='same', activation='relu', input_shape=input_shape,
                         kernel_initializer=initialize_weights, kernel_regularizer=l2(2e-4)))
        model.add(MaxPooling1D(pool_size=2, strides=2, padding='same'))
        model.add(Dropout(0.25))

        model.add(Flatten())

        model.add(Dense(256, activation='sigmoid',
                        kernel_regularizer=l2(1e-3),
                        kernel_initializer=initialize_weights, bias_initializer=initialize_bias))

        # Generate the encodings (feature vectors) for both input vectors
        encoded_l = model(left_input)
        encoded_r = model(right_input)

        # Add a customized layer to compute the cosine distance between the encodings
        Cosine_distance = Dot(axes=1, normalize=True)([encoded_l, encoded_r])
        prediction = Dense(1, activation='sigmoid', bias_initializer=initialize_bias)(Cosine_distance)

        # Connect the inputs with the outputs
        siamese_model = Model(inputs=[left_input, right_input], outputs=prediction)

        # return the model
        return siamese_model

    def train_siamese_network(self, embeddingPairs: List[EmbeddingsPair], path: str):
        #split into training and test set
        embeddingPairs_train, embeddingPairs_test = train_test_split(embeddingPairs, test_size=0.2, shuffle=True)

        embeddings1_train: List[Embedding] = list(map(lambda e: e.embedding1, embeddingPairs_train))
        embeddings2_train: List[Embedding] = list(map(lambda e: e.embedding2, embeddingPairs_train))
        labels_train: List[int] = list(map(lambda e: e.label, embeddingPairs_train))

        embeddings1_test: List[Embedding] = list(map(lambda e: e.embedding1, embeddingPairs_test))
        embeddings2_test: List[Embedding] = list(map(lambda e: e.embedding2, embeddingPairs_test))
        labels_test: List[int] = list(map(lambda e: e.label, embeddingPairs_test))

        #standardize and reshape
        scaler = StandardScaler()
        train1 = np.array(embeddings1_train)
        train1 = scaler.fit_transform(train1)
        train1 = train1.reshape(train1.shape[0], train1.shape[1], 1)

        train2 = np.array(embeddings2_train)
        train2 = scaler.fit_transform(train2)
        train2 = train2.reshape(train2.shape[0], train2.shape[1], 1)

        test1 = np.array(embeddings1_test)
        test1 = scaler.fit_transform(test1)
        test1 = test1.reshape(test1.shape[0], test1.shape[1], 1)

        test2 = np.array(embeddings2_test)
        test2 = scaler.fit_transform(test2)
        test2 = test2.reshape(test2.shape[0], test2.shape[1], 1)

        optimizer = optimizers.adam(learning_rate=0.01)
        self.model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=['acc'])
        earlystopping = EarlyStopping(monitor="val_acc", patience=20, verbose=1, mode='auto')

        history = self.model.fit([train1, train2], np.array(labels_train),
                                validation_data=([test1, test2], np.array(labels_test)),
                                epochs=30, batch_size=32, shuffle=True,
                                callbacks=[earlystopping])

        # serialize model to JSON
        model_json = self.model.to_json()
        with open(path + ".json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights(path + ".h5")

        return history

    def compute_similarity_matrix(self, vectors: List[ElmoVector]) -> np.array:
        matrix = np.zeros(len(vectors), len(vectors))
        for i in range(0, len(vectors)):
            input1 = np.array(vectors[i])
            input1 = input1.reshape((input1.shape[0], 1))
            input_list1 = [input1] * (len(vectors) - i)
            input_list2 = []
            for j in range(i, len(vectors)):
                input2 = np.array(vectors[j])
                input2 = input2.reshape((input2.shape[0], 1))
                input_list2.append(input2)

            prediction = self.model.predict([input_list1, input_list2])[:, 0]
            zeros = np.array([0.0] * (len(vectors) - len(prediction)))
            if len(zeros) > 0:
                prediction = np.concatenate([zeros, prediction])
            matrix[i] = prediction
        return matrix
