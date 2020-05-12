# Downlaad ELMo model from AllenNLP
# https://allennlp.org/elmo

deps: elmo_2x4096_512_2048cnn_2xhighway_5.5B weights_book.hdf5

elmo_2x4096_512_2048cnn_2xhighway_5.5B: elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5 elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json

elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5:
	@curl -O "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway_5.5B/elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5"

elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json:
	@curl -O "https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway_5.5B/elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json"

weights_book.hdf5:
	@curl -O "https://nextcloud.in.tum.de/index.php/s/piTR588t369YXND/download"