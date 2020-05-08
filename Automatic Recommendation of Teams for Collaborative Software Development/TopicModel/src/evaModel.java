import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FileUtils;
import org.apache.commons.math3.stat.descriptive.moment.Mean;
import org.apache.commons.math3.stat.descriptive.moment.StandardDeviation;
import org.apache.commons.math3.stat.descriptive.rank.Median;

import cc.mallet.topics.ParallelTopicModel;
import opennlp.tools.stemmer.PorterStemmer;

public class evaModel {
	
    public static <T> List<T> intersection(List<T> list1, List<T> list2) {
        List<T> list = new ArrayList<T>();
        for (T t : list1) {
            if(list2.contains(t)) {
                list.add(t);
            }
        }
        return list;
    }

	/*
	 * evaluate topic coherence and output csv file wordOffset is the number of top
	 * words to consider doing pairwise Output: 2D array of [numTopics][num word
	 * Pairs] of PMI scores
	 */
	public static double[][] EvalCoherence(ParallelTopicModel model, Indexer wordIndex, int wordOffset) throws Exception {
		int numPairs = (wordOffset * (wordOffset - 1)) / 2; // number of possible unique pairs
		int numTopics = model.numTopics; // number of topics
		int numDocs = wordIndex.getNumDoc(); // num all documents in the index
		
		double[][] pmiScores = new double[numTopics][numPairs];
		Object[][] topWords = model.getTopWords(wordOffset);

		for (int topicIndex = 0; topicIndex < topWords.length; topicIndex++) {
			int pairCount = 0;
			for (int i = 0; i < topWords[topicIndex].length - 1; i++) {
				for (int j = i + 1; j < topWords[topicIndex].length; j++) {
					// calculate PMI
					String wordA = (String) topWords[topicIndex][i];
					String wordB = (String) topWords[topicIndex][j];
					List<Integer> docsContainingWordA = wordIndex.getMatchDocuments(wordA);
					List<Integer> docsContainingWordB = wordIndex.getMatchDocuments(wordB);
					List<Integer> docsContainingBothAB = intersection(docsContainingWordA,docsContainingWordB);

					double pAB = (double) docsContainingBothAB.size();
					if (pAB == 0.0)pAB = 1.0;
					pAB /= (double) numDocs;

					double pA = (double) docsContainingWordA.size();
					if (pA == 0.0)pA = 1.0;
					pA /= (double) numDocs;

					double pB = (double) docsContainingWordB.size();
					if (pB == 0.0)pB = 1.0;
					pB /= (double) numDocs;

					pmiScores[topicIndex][pairCount] = Math.log(pAB / (pA * pB));
					if (Double.isInfinite(pmiScores[topicIndex][pairCount])	|| Double.isNaN(pmiScores[topicIndex][pairCount])) {
						System.out.println("@@@ error NaN or Infi " + wordA + "(" + docsContainingWordA.size() + ")|"
								+ wordB + "(" + docsContainingWordB.size() + ")" + " A&B(" + docsContainingBothAB.size()
								+ ")\n");
						pmiScores[topicIndex][pairCount] = 0.0;
					}
					pairCount++;
				}
			}
		}

		return pmiScores;
	}

	public static void main(String[] args) throws Exception {
		// PARAMETER: | PATH_TO_MODEL | Test
		File modelPath = new File(args[0]);
		File document_test = new File(modelPath, "Train_1.txt");		// TODO
		String outputBaseDir = args[2];				// TODO
		// Experiment Setting
		int exp_init = Integer.parseInt(args[3]);					// TODO
		int exp_end = Integer.parseInt(args[4]);					// TODO
		int exp_increase = Integer.parseInt(args[5]);				// TODO
		
		ArrayList<Integer> numTopicList = new ArrayList<Integer>();
		// Find number of iteration
		for(int i=exp_init; i<=exp_end;i+=exp_increase) {
			numTopicList.add(i);
		}

		Indexer wordIndex = new Indexer(document_test);
		
		double[] avgTCScores = new double[numTopicList.size()];
		double[] medTCScores = new double[numTopicList.size()];
		double[] stdTCScores = new double[numTopicList.size()];
		
		int i=0;
		for(int numTopics=exp_init;numTopics<=exp_end; numTopics+=exp_increase) {
			File modelFile = new File(modelPath, args[1]+"_"+numTopics);		//TODO
			System.out.println("@@ RUNNING: "+args[1]+"_"+numTopics);
			ParallelTopicModel model = ParallelTopicModel.read(modelFile);	
			double rawPMIScores[][] = EvalCoherence(model, wordIndex, 10);
			double[] topicCoherenceScores = new double[rawPMIScores.length];
			Mean avgEval = new Mean();
			Median medEval = new Median();
			StandardDeviation stdEval = new StandardDeviation();
			for(int j = 0; j < rawPMIScores.length; j++)
			{
				topicCoherenceScores[j] = avgEval.evaluate(rawPMIScores[j]);
			}
			
			avgTCScores[i] = avgEval.evaluate(topicCoherenceScores);
			medTCScores[i] = medEval.evaluate(topicCoherenceScores);
			stdTCScores[i] = stdEval.evaluate(topicCoherenceScores);
			i++;
		}
		
		System.out.println("@@@ Writing out results\n");
		String avgResultFilename = outputBaseDir+"/coherence.avg.tsv";
		String medResultFilename = outputBaseDir+"/coherence.median.tsv";
		String stdResultFilename = outputBaseDir+"/coherence.std.tsv";
		StringBuilder avgOutputString = new StringBuilder();
		StringBuilder medOutputString = new StringBuilder();
		StringBuilder stdOutputString = new StringBuilder();
		
		//write out header
		int numIts = 3000; 
		{avgOutputString.append("\t"+numIts); medOutputString.append("\t"+numIts); stdOutputString.append("\t"+numIts);} 
		avgOutputString.append("\n"); medOutputString.append("\n"); stdOutputString.append("\n");
		
		for(int topicIndex = 0; topicIndex < numTopicList.size(); topicIndex++)
		{	int numTopics = numTopicList.get(topicIndex);
			avgOutputString.append(""+numTopics);	medOutputString.append(""+numTopics); stdOutputString.append(""+numTopics);
			avgOutputString.append("\t"+avgTCScores[topicIndex]);	medOutputString.append("\t"+medTCScores[topicIndex]); stdOutputString.append("\t"+stdTCScores[topicIndex]);
			avgOutputString.append("\n");	medOutputString.append("\n"); stdOutputString.append("\n");
		}

//		try {
			FileUtils.write(new File(avgResultFilename), avgOutputString, StandardCharsets.UTF_8);
			FileUtils.write(new File(medResultFilename), medOutputString, StandardCharsets.UTF_8);
			FileUtils.write(new File(stdResultFilename), stdOutputString, StandardCharsets.UTF_8);
//		} catch (IOException e) {
//			e.printStackTrace();
//		}
		
	}
}



class Indexer {
	private Map<String, ArrayList<Integer>> wordList;
	private int numDoc;
	private int numWord;
	
	public Indexer(File contentFile) throws Exception {
		wordList = new HashMap<String, ArrayList<Integer>>();
		BufferedReader reader = new BufferedReader(new FileReader(contentFile));
		String textReaders;
		int doc_id_runner = 0;
		int word_id_runner = 0;
		while ((textReaders = reader.readLine()) != null) {
			String[] textReader = textReaders.split("\t");
			if(textReader.length!=3) {
				System.out.println("There are some Error on LINE: "+doc_id_runner);
				continue;
			}
			String inputText = textReader[2];

			String[] word = inputText.split(" ");
			int temp = 0;
			ArrayList<String> localWord = new ArrayList<String>();
			while(temp<word.length) {
				String cleanWord = word[temp];
				if(!localWord.contains(cleanWord)) {
					localWord.add(cleanWord);
					if(!wordList.containsKey(cleanWord)) {
						wordList.put(cleanWord, new ArrayList<Integer>());
						word_id_runner++;
					}
					ArrayList<Integer> docList = wordList.get(cleanWord);
					docList.add(doc_id_runner);
				}
				temp++;
			}
			doc_id_runner++;
		}
		numDoc = doc_id_runner;
		numWord = word_id_runner;
	}

	public ArrayList<Integer> getMatchDocuments(String word) {
		if(wordList.containsKey(word))return wordList.get(word);
		System.err.println("COULD NOT FOUND @@ "+word+" @@");
		return null;
	}
	
	public int getNumDoc() {
		return numDoc;
	}
	
	public int getNumWord() {
		return numWord;
	}
}