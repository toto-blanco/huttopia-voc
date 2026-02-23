import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_performance():
    df = pd.read_csv("../data/processed/huttopia_reviews_master.csv")
    sns.set_theme(style="whitegrid")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # 1. Note moyenne par Source
    order = df.groupby('source')['note_std'].mean().sort_values().index
    sns.barplot(data=df, x='source', y='note_std', ax=ax1, palette='viridis', order=order)
    ax1.set_title("Note Moyenne par Plateforme")
    ax1.set_ylim(0, 5)

    # 2. Volume d'avis par Source
    df['source'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax2, colors=['#ff9999','#66b3ff','#99ff99'])
    ax2.set_title("Répartition des Sources")

    plt.tight_layout()
    plt.savefig("../data/processed/performance_sources.png")
    plt.show()

if __name__ == "__main__":
    plot_performance()