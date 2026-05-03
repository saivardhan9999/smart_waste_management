"""
Training script for Smart Waste Management System
Uses MobileNetV2 for transfer learning
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import numpy as np
from pathlib import Path
from PIL import Image
import pickle

# Configuration
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / 'app' / 'ml'
DATA_DIR = BASE_DIR / 'Garbage classification' / 'Garbage classification'
TRAIN_FILE = BASE_DIR / 'one-indexed-files-notrash_train.txt'
VAL_FILE = BASE_DIR / 'one-indexed-files-notrash_val.txt'
TEST_FILE = BASE_DIR / 'one-indexed-files-notrash_test.txt'

# Model configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = 6
CLASS_NAMES = ['glass', 'paper', 'cardboard', 'plastic', 'metal', 'trash']


def load_data_from_txt(txt_file, data_dir):
    """Load images and labels from text file"""
    images = []
    labels = []
    
    print(f"Loading data from: {txt_file}")
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            filename, label = parts
            label = int(label) - 1  # Convert to 0-indexed
            
            # Get class name from label
            class_name = CLASS_NAMES[label]
            
            # Construct full path with class subdirectory
            img_path = data_dir / class_name / filename
            
            if img_path.exists():
                try:
                    img = Image.open(img_path).convert('RGB')
                    img = img.resize(IMG_SIZE)
                    img_array = np.array(img) / 255.0
                    images.append(img_array)
                    labels.append(label)
                    if len(images) % 50 == 0:
                        print(f"Loaded {len(images)} images...")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    print(f"Total loaded: {len(images)} images")
    return np.array(images), np.array(labels)


def create_model():
    """Create MobileNetV2 based model"""
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Add custom head
    inputs = keras.Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = keras.Model(inputs, outputs)
    
    return model


def train():
    """Train the model"""
    import sys
    import os
    
    # Set UTF-8 encoding for Windows
    if sys.platform.startswith('win'):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    print("Loading training data...")
    X_train, y_train = load_data_from_txt(TRAIN_FILE, DATA_DIR)
    X_val, y_val = load_data_from_txt(VAL_FILE, DATA_DIR)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    # Create model
    print("Creating model...")
    model = create_model()
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(model.summary())
    
    # Data augmentation
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2
    )
    
    # Callbacks
    checkpoint = ModelCheckpoint(
        str(MODEL_DIR / 'model.keras'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )
    
    # Train
    print("Starting training...")
    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
        steps_per_epoch=len(X_train) // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(X_val, y_val),
        callbacks=[checkpoint, early_stop, reduce_lr],
        verbose=1
    )
    
    # Fine-tune (optional)
    print("\nFine-tuning...")
    base_model = model.layers[1]
    base_model.trainable = True
    
    # Freeze first 100 layers
    for layer in base_model.layers[:100]:
        layer.trainable = False
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history_ft = model.fit(
        datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
        steps_per_epoch=len(X_train) // BATCH_SIZE,
        epochs=5,
        validation_data=(X_val, y_val),
        callbacks=[checkpoint, early_stop, reduce_lr],
        verbose=1
    )
    
    # Load best model
    print("\nTraining complete!")
    print("Loading best model...")
    final_model = keras.models.load_model(str(MODEL_DIR / 'model.keras'))
    
    # Evaluate
    print("\nEvaluating on validation set...")
    val_loss, val_acc = final_model.evaluate(X_val, y_val, verbose=1)
    print(f"Validation Accuracy: {val_acc:.4f}")
    print(f"Validation Loss: {val_loss:.4f}")
    
    # Save history
    with open(MODEL_DIR / 'training_history.pkl', 'wb') as f:
        pickle.dump(history.history, f)
    
    print(f"Model saved to: {MODEL_DIR / 'model.keras'}")


if __name__ == '__main__':
    train()

