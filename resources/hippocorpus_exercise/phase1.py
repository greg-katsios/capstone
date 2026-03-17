import pandas as pd
# import csv to be pandas df
df = pd.read_csv(
    'hippocorpus_exercise/hippocorpus-u20220112/hcV3-stories.csv')

if __name__ == '__main__':
    """
    ======================================================
                            PHASE 1:
    ======================================================

    How many stories are in each memType category?
    What is the average story length (in words) for recalled vs. imagined?
    Read 5-10 recalled stories. What do they actually sound like? What makes them feel "autobiographical"?
    Are there any empty rows, duplicates, or obvious data quality issues?
    Then filter to only recalled stories, extract the story column, and split 90/10 into train and validation sets.
    """
    
    # read full stories
    # pd.set_option('display.max_colwidth', None)

    # get columns
    columns = df.columns

    # all memtypes
    memtypes = df['memType']

    """
    print(memtypes.value_counts())
    recalled = 2779 stories
    imagined = 2756 stories 
    retold = 1319 stories
    """

    recalled = df[memtypes == 'recalled']
    imagined = df[memtypes == 'imagined']

    recalled_stories = recalled['story']
    imagined_stories = imagined['story']

    """
    print(recalled_stories.str.len().mean().round())
    print(imagined_stories.str.len().mean().round())
    1432 words
    1254 words
    """

    """
    print(recalled['story'].head().to_string())
   
    A lot of these stories focus on specific moments of the writers life, from concerts, to their niece and nephew being born, to road trips. They
    feel a lot personal and "autobiographical" because of the amount of depth the writing goes into each of these stories as well as the writing
    style they use evokes a lot of emotion, as if you're really stepping into this moment of the writer's life and viewing things as how they saw 
    it and how they felt during it. 
    """
    

    """
    rows_with_any_na = df.isna().any(axis=1).sum()
    print(rows_with_any_na)
    6854 rows with NAs
    """

    """
    duplicate_stories = df.duplicated(subset=['story']).sum()
    duplicate_summaries = df.duplicated(subset=['summary']).sum()
    print(duplicate_stories)
    print(duplicate_summaries)
    
    0 duplicate stories but 4066 duplicate summaries
    """
    
    # Splitting recalled stories into 90/10 train test sets
    train_set = recalled_stories.sample(frac=0.9, random_state=42)
    test_set = recalled_stories.drop(train_set.index)
    
    # Save splits to disk
    train_set.to_csv('hippocorpus_exercise/train.csv', index=False)
    test_set.to_csv('hippocorpus_exercise/test.csv', index=False)
    print(f"Saved {len(train_set)} train, {len(test_set)} test examples")
    
    print(train_set.head())
    print(test_set.head())