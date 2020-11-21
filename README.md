# Automatic Recommendation of Teams for Collaborative Software Development

## Running Experiment
Since this research was broken down into many sections, the instruction for running/compile/execute on each section will be written in __README.md__ on each folder of each part.

The order for running the code are as follows:
1. [Data Collection](DataCollection/)
2. Data Preparation
   - [Data Cleaning & Preprocessing](DataPreparation/)
   - [Sentiment Analysis](SentimentAnalysis/)
   - [Topic Modeling](TopicModel/)
3. [Network Generation](NetworkGeneration/)
4. [Feature enginering](FeatureExtraction/)
5. [Team Scoring Model Selection](ModelSelection/)
6. [Team Recommendation](TeamRecommendation/)
7. [Evaluation by P, R, F1, MRR](Evaluation/)

## Note to rerun experiment
The "Files" directory is needed to be placed in the same directory as the project. Please download it in the data link ("Files.zip" is in the Processed Data directory in the data download link.) The filepathhelper.py file is the utility file for helping with the path of the files in the "Files" directory. In addition, please edit config.json according to the dataset ("Moodle", "Apache", or "Atlassian"). Steps 1-5 are used for getting the processed files from the raw data. If you download the processed files, you can skip and run the Team Recommendation code.

## Support
If you have any questions on this project or get stuck during code execution, feel free to create issue on this repository together with `hitnothit` label.
We will generate the assignee team by using our code to fix your issue.

## Data
The raw data, preprocessed data, and the result of team recommendation can be download [here](https://drive.google.com/drive/folders/1D12UKF_05uh4AS9XiLdocxEP8nqFcS8q?usp=sharing).
