data_root = '../results/'
data_ext = '.out'
model_dir = 'models/'
num_workers = 4

# GRU options
# embed_size = 300
hidden_1 = 128
hidden_2 = 128

# Text_CNN options
kernel_dims = 100
kernel_heights = (1,2,3,4,5)

# Dropout
dropout = 0.3

# padding options
padding_ext = '90'
padding_all = True

# training options
learning_rate = 0.001
betas = (0.9,0.98)
eps = 1e-9

