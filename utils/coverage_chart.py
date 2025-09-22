# Copyright (c) 2025 [Your Name/Organization]
# Licensed under the MIT License. See LICENSE file in the project root for details.

import matplotlib.pyplot as plt

def plot_coverage_chart(coverage_data: dict):
    languages = ["en", "de", "hr", "ko", "es", "fr", "ja", "zh"]
    values = [coverage_data.get(lang, 0) for lang in languages]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]

    plt.figure(figsize=(10, 6))
    plt.bar(languages, values, color=colors)
    plt.xlabel("Language")
    plt.ylabel("Coverage Rate (%)")
    plt.title("Language-wise Coverage Rate")
    plt.ylim(0, 100)
    plt.savefig("coverage_chart.png")
    plt.close()