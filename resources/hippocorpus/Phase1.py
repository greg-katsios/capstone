import pandas as pd
import numpy as np
from collections import Counter
import re

# Load the dataset
df = pd.read_csv('hcV3-stories.csv')

print("=" * 80)
print("PHASE 1: DATA EXPLORATION")
print("=" * 80)

# 1. How many stories in each memType category?
print("\n1. Story count by memType:")
print(df['memType'].value_counts())
print(f"\nTotal stories: {len(df)}")

# 2. Check for data quality issues
print("\n2. Data Quality Check:")
print(f"Missing values per column:\n{df.isnull().sum()}")
print(f"\nDuplicate rows: {df.duplicated().sum()}")
print(f"Duplicate stories: {df['story'].duplicated().sum()}")

# 3. Calculate average story length by memType
print("\n3. Average story length (in words) by memType:")
df['word_count'] = df['story'].fillna('').apply(lambda x: len(str(x).split()))
length_by_type = df.groupby('memType')['word_count'].agg(['mean', 'median', 'min', 'max'])
print(length_by_type)

# 4. Compare recalled vs imagined
print("\n4. Recalled vs Imagined comparison:")
recalled_stats = df[df['memType'] == 'recalled']['word_count'].describe()
imagined_stats = df[df['memType'] == 'imagined']['word_count'].describe()
print(f"\nRecalled stories:\n{recalled_stats}")
print(f"\nImagined stories:\n{imagined_stats}")

# 5. Display sample recalled stories
print("\n5. Sample Recalled Stories (first 5):")
recalled_stories = df[df['memType'] == 'recalled']['story'].dropna()
for i, story in enumerate(recalled_stories.head(5), 1):
    print(f"\n--- Story {i} ---")
    print(story[:300] + "..." if len(story) > 300 else story)

# 6. Check for empty stories
print("\n6. Empty/null stories:")
empty_stories = df[df['story'].isnull() | (df['story'].str.strip() == '')]
print(f"Count: {len(empty_stories)}")

# 7. Filter to recalled stories only
print("\n" + "=" * 80)
print("FILTERING TO RECALLED STORIES")
print("=" * 80)

recalled_df = df[df['memType'] == 'recalled'].copy()
recalled_df = recalled_df.dropna(subset=['story'])
recalled_df = recalled_df[recalled_df['story'].str.strip() != '']

print(f"\nRecalled stories after filtering: {len(recalled_df)}")
print(f"Total words: {recalled_df['word_count'].sum():,}")

# 8. Train/validation split (90/10)
print("\n" + "=" * 80)
print("TRAIN/VALIDATION SPLIT")
print("=" * 80)

train_size = int(0.9 * len(recalled_df))
train_df = recalled_df.iloc[:train_size]
val_df = recalled_df.iloc[train_size:]

print(f"Train set: {len(train_df)} stories ({len(train_df)/len(recalled_df)*100:.1f}%)")
print(f"Validation set: {len(val_df)} stories ({len(val_df)/len(recalled_df)*100:.1f}%)")
print(f"Train set total words: {train_df['word_count'].sum():,}")
print(f"Validation set total words: {val_df['word_count'].sum():,}")

# 9. Save the split datasets
train_df[['story']].to_csv('train_stories.csv', index=False)
val_df[['story']].to_csv('val_stories.csv', index=False)

print("\nDatasets saved:")
print("  - train_stories.csv")
print("  - val_stories.csv")

# 10. Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print(f"\nTrain set word count stats:")
print(train_df['word_count'].describe())
print(f"\nValidation set word count stats:")
print(val_df['word_count'].describe())