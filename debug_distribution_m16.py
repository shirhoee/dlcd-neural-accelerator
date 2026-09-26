import numpy as np
from sklearn.datasets import load_digits

def main():
    digits = load_digits()
    data_8x8 = digits.images / 16.0  # normalize to [0, 1]
    
    # Pad to 10x10 like the model expects
    data_10x10 = np.pad(data_8x8, ((0, 0), (1, 1), (1, 1)), mode='constant', constant_values=0)

    # 10x10 stats
    mean_intensity = np.mean(data_10x10)
    nonzero_fraction = np.mean(data_10x10 > 0.05)

    print(f"Sklearn digits 10x10 Mean Intensity: {mean_intensity:.4f}")
    print(f"Sklearn digits 10x10 Nonzero Fraction (>0.05): {nonzero_fraction:.4f}")
    
    # 8x8 stats just in case
    mean_intensity_8 = np.mean(data_8x8)
    nonzero_fraction_8 = np.mean(data_8x8 > 0.05)
    print(f"Sklearn digits 8x8 Mean Intensity: {mean_intensity_8:.4f}")
    print(f"Sklearn digits 8x8 Nonzero Fraction (>0.05): {nonzero_fraction_8:.4f}")

if __name__ == "__main__":
    main()
