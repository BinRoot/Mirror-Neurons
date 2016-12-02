import tensorflow as tf
import numpy as np
import glob
import os

class Classifier:
    def __init__(self, img_size, output_dim, learning_rate=0.0001):
        input_dim = img_size[0] * img_size[1]
        self.img_size = img_size

        # define placeholders
        self.x = tf.placeholder(tf.float32, [None, input_dim])
        self.y = tf.placeholder(tf.float32, [None, output_dim])
        self.keep_prob = tf.placeholder(tf.float32)

        # define variables
        conv_out1 = 2
        conv_out2 = 2
        lin_out = 4
        self.W1 = tf.Variable(tf.random_normal([5, 5, 1, conv_out1]))
        self.b1 = tf.Variable(tf.random_normal([conv_out1]))
        self.W2 = tf.Variable(tf.random_normal([5, 5, conv_out1, conv_out2]))
        self.b2 = tf.Variable(tf.random_normal([conv_out2]))
        rescaled_img_size = (img_size[0] / 4, img_size[1] / 4)
        self.W3 = tf.Variable(tf.random_normal([rescaled_img_size[0]*rescaled_img_size[1]*conv_out2, lin_out]))
        self.b3 = tf.Variable(tf.random_normal([lin_out]))
        self.W_out = tf.Variable(tf.random_normal([lin_out, output_dim]))
        self.b_out = tf.Variable(tf.random_normal([output_dim]))

        self.W = tf.Variable(tf.random_normal([input_dim, 20]))
        self.b = tf.Variable(tf.random_normal([20]))
        self.Ww = tf.Variable(tf.random_normal([20, output_dim]))
        self.bb = tf.Variable(tf.random_normal([output_dim]))

        # define cost functions
        self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(self.model(), self.y))
        self.train_op = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(self.cost)

    def _conv2d(self, x, W, b, strides=1):
        x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
        x = tf.nn.bias_add(x, b)
        return tf.nn.relu(x)

    def _maxpool2d(self, x, k=2):
        return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1], padding='SAME')

    def model_backup(self):
        mm = tf.matmul(self.x, self.W)
        h1 = tf.nn.relu(mm + self.b)
        h1 = tf.nn.dropout(h1, keep_prob=self.keep_prob)
        out = tf.matmul(h1, self.Ww) + self.bb
        return out

    def model(self):
        x = tf.reshape(self.x, shape=[-1, self.img_size[0], self.img_size[1], 1])

        conv1 = self._conv2d(x, self.W1, self.b1)
        conv1 = self._maxpool2d(conv1, k=2)

        conv2 = self._conv2d(conv1, self.W2, self.b2)
        conv2 = self._maxpool2d(conv2, k=2)

        fc1 = tf.reshape(conv2, [-1, self.W3.get_shape().as_list()[0]])
        fc1 = tf.add(tf.matmul(fc1, self.W3), self.b3)
        fc1 = tf.nn.relu(fc1)
        fc1 = tf.nn.dropout(fc1, keep_prob=self.keep_prob)
        out = tf.add(tf.matmul(fc1, self.W_out), self.b_out)
        return out

    def train(self, sess, train_x, train_y):
        _, cost_val = sess.run([self.train_op, self.cost], feed_dict={self.x: train_x, self.y: train_y, self.keep_prob: 0.75})
        return cost_val

    def test(self, sess, test_x):
        resp = sess.run(self.model(), feed_dict={self.x: test_x, self.keep_prob: 1})
        return resp


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    do_train = False
    num_epocs = 10

    folder_name = 'train_data_big' if do_train else 'test_data_10_small'

    classifier = Classifier(img_size=(12, 24), output_dim=3)

    train_xs = []
    train_ys = []

    train_x_filenames, train_y_filenames = [], []
    foldernames = glob.glob('{}/plots_*'.format(folder_name))
    for foldername in foldernames:
        train_x_filename = '{}/train_x.npy'.format(foldername)
        train_y_filename = '{}/train_y.npy'.format(foldername)
        train_x_data = np.load(train_x_filename)
        train_y_data = np.load(train_y_filename)
        print(np.shape(train_x_data), np.shape(train_y_data))
        train_xs.append(train_x_data)
        train_ys.append(train_y_data)

    saver_op = tf.train.Saver()

    if do_train:
        with tf.Session() as sess:
            sess.run(tf.initialize_all_variables())
            for i in range(num_epocs):
                for train_x, train_y in zip(train_xs, train_ys):
                    cost_val = classifier.train(sess, train_x, train_y)
                print(i, cost_val)
            mkdir('model')
            save_path = saver_op.save(sess, 'model/model.ckpt')
            print('Model saved to {}'.format(save_path))
    else:
        resps = []
        with tf.Session() as sess:
            saver_op.restore(sess, 'model/model.ckpt')
            for train_x, train_y in zip(train_xs, train_ys):
                resp = classifier.test(sess, train_x)
                resp = np.argmax(resp, axis=1)
                print(resp)
                resps.append(resp)
                # print(np.argmax(train_y, axis=1))
        with open('sentences.txt', 'w') as writer:
            writer.write('3\n0\n1\n2\n\n{}\n'.format(len(resps)))
            for resp in resps:
                for idx, r in enumerate(resp):
                    writer.write('{} [{} {}]'.format(r, idx, idx))
                    if idx < len(resp) - 1:
                        writer.write(' ')
                    else:
                        writer.write('\n')
