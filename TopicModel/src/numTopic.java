import java.util.*;
import java.util.regex.*;
import java.io.*;

import cc.mallet.util.*;
import cc.mallet.types.*;
import cc.mallet.pipe.*;
import cc.mallet.pipe.iterator.*;
import cc.mallet.topics.*;

public class numTopic {

	public static void main(String[] args) throws Exception {
		// Find # of data
		int num_data = 0;
		File inputFile = new File(args[0]);
		BufferedReader reader = new BufferedReader(new FileReader(inputFile));
		while (reader.readLine() != null) {
			num_data++;
		}
		reader.close();

		// Experiment Setting
		int exp_init = Integer.parseInt(args[3]);					// TODO
		int exp_end = Integer.parseInt(args[4]);					// TODO
		int exp_increase = Integer.parseInt(args[5]);				// TODO
		int exp_size = 0;
		
		// Split Test and Train data
		int num_experiment = 1;				// TODO
		int ratio_train = 9;				// TODO
		int ratio_test = 1;					// TODO
		int num_train = (int) ((ratio_train * 1.0 / (ratio_train + ratio_test)) * num_data);
		int num_test = num_data - num_train;
		
		ArrayList<Integer> x_axis = new ArrayList<Integer>();
		// Find number of iteration
		for(int i=exp_init; i<=exp_end;i+=exp_increase) {
			x_axis.add(i);
			exp_size++;
		}
		double[][] y_axis = new double[num_experiment][exp_size];
		
		// Output Path
		File dir = new File(args[1]);
		dir.mkdirs();
		
		// Graph Color
		String[] color = {"b", "g", "r", "c", "m", "y", "k", "w"};
		
		// Start Log
		File logFile = new File(dir, "output.log");					// TODO
		BufferedWriter writerLog = new BufferedWriter(new FileWriter(logFile));
		writerLog.write("Input: "+ inputFile + System.getProperty("line.separator"));
		writerLog.write("Experiment: "+ num_experiment + System.getProperty("line.separator"));
		writerLog.write("Ratio(train:test): " + ratio_train + ":" + ratio_test + System.getProperty("line.separator"));
		writerLog.write("Num_train: " + num_train + System.getProperty("line.separator"));
		writerLog.write("Num_test: " + num_test + System.getProperty("line.separator"));
		writerLog.write("Interval Number of Topic: " + exp_init + " - " + exp_end + System.getProperty("line.separator"));
		writerLog.write("Increasing: " + exp_increase +System.getProperty("line.separator"));
		
		for (int experiment = 0; experiment < num_experiment; experiment++) {
			writerLog.write("RUN: "+ (experiment+1) +" - " + num_experiment +System.getProperty("line.separator"));
			ArrayList<Integer> randLine = new ArrayList<Integer>();
			
			File trainFile = new File(dir, "Train_"+ (experiment+1) +".txt");
			File testFile = new File(dir, "Test_"+ (experiment+1) +".txt");

			reader = new BufferedReader(new FileReader(inputFile));
			BufferedWriter writerTrain = new BufferedWriter(new FileWriter(trainFile));
			BufferedWriter writerTest = new BufferedWriter(new FileWriter(testFile));

			// random line number
			for (int i = 0; i < num_test; i++) {
				int temp = new Random().nextInt(num_data) + 1;
				while (randLine.contains(temp))
					temp = new Random().nextInt(num_data) + 1;
				randLine.add(temp);
			}
			Collections.sort(randLine);
			writerLog.write("Rand "+ testFile +": " + randLine +System.getProperty("line.separator"));
			
			// when it reach the random line number, put issue to another file
//			System.out.println(randLine);
			String currentLine;
			int nline = 0;
			int pointerRandList = 0;
			while ((currentLine = reader.readLine()) != null) {
				nline++;
				if (pointerRandList >= num_test || nline != randLine.get(pointerRandList)) {		//TODO
					writerTrain.write(currentLine + System.getProperty("line.separator"));
				} else {
					writerTest.write(currentLine + System.getProperty("line.separator"));
					pointerRandList++;
				}
			}
			
			// close pointer
			reader.close();
			writerTrain.close();
			writerTest.close();

			//put for loop to experiment number topic every t 50 topic [50, 100, ..., 2000]
			
			// Begin by importing documents from text to feature sequences
			ArrayList<Pipe> pipeList = new ArrayList<Pipe>();
			
			// Pipes: lowercase, tokenize, remove stopwords, map to features
			pipeList.add(new CharSequenceLowercase()); 
			pipeList.add(new CharSequence2TokenSequence(Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")));
			pipeList.add(new TokenSequenceRemoveStopwords(new File("stoplists/en.txt"), "UTF-8", false, false, false)); 
			pipeList.add(new TokenSequence2FeatureSequence());
			
			InstanceList instancesTrain = new InstanceList(new SerialPipes(pipeList));			
			Reader fileTrain = new InputStreamReader(new FileInputStream(trainFile), "UTF-8"); 
			instancesTrain.addThruPipe(new CsvIterator(fileTrain, Pattern.compile("^(\\S*)[\\s,]*(\\S*)[\\s,]*(.*)$"), 3, 2, 1));
			
			// Create a model with 100 topics, alpha_t = 0.01, beta_w = 0.01 
			// Note that the first parameter is passed as the sum over topics, while 
			// the second is the parameter for a single dimension of the Dirichlet prior. 
			int i=0;
			for(int numTopics=exp_init;numTopics<=exp_end; numTopics+=exp_increase) {
				writerLog.write((numTopics) +" / " + exp_end +System.getProperty("line.separator"));
				ParallelTopicModel model = new ParallelTopicModel(numTopics, 1.0, 0.01);
				model.addInstances(instancesTrain); 
				model.setNumThreads(20);								// TODO
				model.setNumIterations(3000); 							// TODO
				model.estimate();
				model.write(new File(dir, args[2]+"_"+numTopics));
				MarginalProbEstimator evaluator = model.getProbEstimator();
			}
		} //End Experiment
		
		writerLog.close();
	}
}
