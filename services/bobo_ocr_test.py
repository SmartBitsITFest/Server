from easyocr import easyocr

eocr_reader = reader = easyocr.Reader(['en'], detect_network='dbnet18',
                                      model_storage_directory='../easy_ocr_models/')  # this needs to run only once to load the model into memory
