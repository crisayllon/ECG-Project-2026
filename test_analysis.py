import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks


# CONFIGURATION

FS = 512  # Sampling frequency (Hz)
BASE_PATH = "samples-renamed"

ACTIVITY_FOLDERS = {
    "1-sit": "sitting",
    "2-stand": "standing",
    "3-walk": "walking",
    "4-jump": "skipping",
    "5-run": "running",
    "6-climbup": "climbing_up_stairs",
    "7-climbdown": "climbing_down_stairs"
}

OUTPUT_DIR = "results"
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


# BANDPASS FILTER

def bandpass_filter(signal, lowcut=0.5, highcut=40, fs=512, order=2):
    """
    Apply a bandpass filter to remove baseline drift and high-frequency noise.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)


# SIGNAL LOADING

def load_signal(file_path):
    """
    Load ECG signal from CSV file.
    Attempts to extract the first numeric column.
    """
    df = pd.read_csv(file_path)

    # Attempt 1: use first numeric column
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        signal = df[numeric_cols[0]].dropna().values
        return signal

    # Attempt 2: convert first column to numeric
    signal = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().values
    return signal

# R-PEAK DETECTION

def detect_r_peaks(ecg_filtered, fs=512):
    """
    Detect R-peaks using a simple threshold and minimum distance.
    """
    min_distance = int(0.3 * fs)  # Minimum distance between peaks

    # Simple adaptive threshold (can be adjusted)
    threshold = np.mean(ecg_filtered) + 0.5 * np.std(ecg_filtered)

    peaks, properties = find_peaks(
        ecg_filtered,
        distance=min_distance,
        height=threshold
    )
    return peaks, properties


# RR INTERVAL COMPUTATION

def compute_rr_intervals(peaks, fs=512):
    """
    Compute RR intervals from detected R-peaks.
    """
    peak_times = peaks / fs
    rr_intervals = np.diff(peak_times)
    return rr_intervals


# SUBJECT ID EXTRACTION

def extract_subject_id(filename):
    """
    Extract subject identifier from filename.
    Example: subject1.csv -> subject1
    """
    name = os.path.splitext(filename)[0]
    return name


# MAIN PROCESSING LOOP

summary_rows = []
rr_by_activity = {activity_label: [] for activity_label in ACTIVITY_FOLDERS.values()}

for folder_name, activity_label in ACTIVITY_FOLDERS.items():
    folder_path = os.path.join(BASE_PATH, folder_name)

    if not os.path.isdir(folder_path):
        print(f"Folder not found: {folder_path}")
        continue

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".csv")])

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        try:
            signal = load_signal(file_path)

            if len(signal) < FS:
                print(f"File too short: {file_name}")
                continue

            # Signal preprocessing
            signal_filtered = bandpass_filter(signal, fs=FS)

            # R-peak detection
            peaks, _ = detect_r_peaks(signal_filtered, fs=FS)

            if len(peaks) < 2:
                print(f"Not enough peaks detected in {file_name}")
                continue

            # RR interval computation
            rr = compute_rr_intervals(peaks, fs=FS)

            # Basic physiological filtering (remove unrealistic values)
            rr = rr[(rr > 0.3) & (rr < 2.0)]

            if len(rr) == 0:
                print(f"Empty RR after filtering in {file_name}")
                continue

            # Heart rate in bpm
            hr_bpm = 60 / rr

            subject_id = extract_subject_id(file_name)

            # Store summary metrics
            summary_rows.append({
                "subject": subject_id,
                "activity_folder": folder_name,
                "activity": activity_label,
                "file": file_name,
                "num_samples": len(signal),
                "num_r_peaks": len(peaks),
                "num_rr_intervals": len(rr),
                "RR_mean_s": np.mean(rr),
                "RR_std_s": np.std(rr),
                "HR_mean_bpm": np.mean(hr_bpm),
                "HR_std_bpm": np.std(hr_bpm)
            })

            # Store RR values per activity
            rr_by_activity[activity_label].extend(rr.tolist())

        except Exception as e:
            print(f"Error processing {file_path}: {e}")


# SUMMARY TABLE

df_summary = pd.DataFrame(summary_rows)

summary_csv = os.path.join(OUTPUT_DIR, "results_summary.csv")
df_summary.to_csv(summary_csv, index=False)

print(f"Summary saved to: {summary_csv}")


# HISTOGRAMS PER ACTIVITY

for activity_label, rr_values in rr_by_activity.items():
    if len(rr_values) == 0:
        continue

    plt.figure(figsize=(8, 5))
    plt.hist(rr_values, bins=20)
    plt.title(f"RR Histogram - {activity_label}")
    plt.xlabel("RR interval (s)")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)

    out_path = os.path.join(FIGURES_DIR, f"hist_{activity_label}.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Histogram saved to: {out_path}")


# AGGREGATED ACTIVITY STATISTICS

if not df_summary.empty:
    df_activity_stats = df_summary.groupby("activity").agg(
        RR_mean_activity_s=("RR_mean_s", "mean"),
        RR_std_activity_s=("RR_mean_s", "std"),
        HR_mean_activity_bpm=("HR_mean_bpm", "mean"),
        HR_std_activity_bpm=("HR_mean_bpm", "std"),
        num_subjects=("subject", "count")
    ).reset_index()

    activity_csv = os.path.join(OUTPUT_DIR, "activity_statistics.csv")
    df_activity_stats.to_csv(activity_csv, index=False)

    print(f"Activity statistics saved to: {activity_csv}")
else:
    print("No summary generated because no files were processed successfully.")