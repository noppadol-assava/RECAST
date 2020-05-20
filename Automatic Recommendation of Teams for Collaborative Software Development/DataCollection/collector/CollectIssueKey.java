package com.data.collector;

import com.data.utility.json.JDBCMySQLConnection;
import com.data.utility.json.ResourcePointer;
import com.data.utility.json.Utility;
import org.apache.commons.codec.binary.Base64;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.X509Certificate;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class CollectIssueKey {
	static ResourcePointer casestudy = new ResourcePointer();
	
	public static void main(String[] args) throws IOException, NoSuchAlgorithmException, ParseException, SQLException {
		SSLContext ctx = null;
        TrustManager[] trustAllCerts = new X509TrustManager[]{new X509TrustManager(){
            public X509Certificate[] getAcceptedIssuers(){return null;}
            public void checkClientTrusted(X509Certificate[] certs, String authType){}
            public void checkServerTrusted(X509Certificate[] certs, String authType){}
        }};
        try {
            ctx = SSLContext.getInstance("SSL");
            ctx.init(null, trustAllCerts, null);
        } catch (KeyManagementException e) {
        	//LOGGER.info("Error loading ssl context {}", ((Throwable) e).getMessage());
        }
        
        SSLContext.setDefault(ctx);
        
		casestudy.setRunningCaseStudy();
		String RestURL = casestudy.getRestApiAddress();

        //String[] projectName = {"CARBON","APPFAC","ESBJAVA"};
        String[] projectName = {"No project"};
        for (int i=0; i<projectName.length;i++ ) {
            //String query = "project="+projectName[i]; // test query string on issue navigation first
            String query = "";
            String note = "new pretrain data for story point paper";
            URL url = new URL("https://"+RestURL+"/rest/api/2/search?jql="+query+"&maxResults=1000");
            //String final urlSafe = org.apache.commons.codec.net.URLCodec.encode(url);
            System.out.println(url);
            String queryResult = connectJiraAPI(url).toString();
            JSONParser parser = new JSONParser();
            JSONObject queryResultJson = (JSONObject) parser.parse(queryResult);

            long maxResults = (long) queryResultJson.get("maxResults");
            long startAt = (long) queryResultJson.get("startAt");
            long total = (long) queryResultJson.get("total");

            System.out.println("Start at:"+startAt);
            System.out.println("Max results:"+maxResults);
            System.out.println("Total:"+total);

            System.out.println("Collecting issue keys...");

            Connection connection = null;
            connection = JDBCMySQLConnection.getConnection();

            DateFormat dateFormat = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
            Date date = new Date();
            //System.out.println(dateFormat.format(date)); //2014/08/06 15:59:48
            int check = 0;
            int issueCount = 0;
            while(startAt <= total){
                check = 0;
                url = new URL("https://"+RestURL+"/rest/api/2/search?jql="+query+"&maxResults=1000&startAt="+startAt);
                try {
                    queryResult = connectJiraAPI(url).toString();
                    queryResultJson = (JSONObject) parser.parse(queryResult);
                    JSONArray issueList = (JSONArray) queryResultJson.get("issues");
                    Iterator issues = issueList.iterator();

                    while (issues.hasNext()) {
                        JSONObject issue = (JSONObject) issues.next();
                        String issueKey = (String) issue.get("key");
                        //String created = (String) issue.get("created");
                        System.out.println(issueKey);

                        String InsertSql = "INSERT INTO `"
                                + casestudy.getDbname()
                                + "`.`collect_key` "
                                + "(`issuekey`,"
                                + " `Note`,"
                                + " `collecttime`) VALUES "
                                + " (?,?,?);";

                        PreparedStatement preparedStatement = connection.prepareStatement(InsertSql);
                        preparedStatement.setString(1, issueKey);
                        preparedStatement.setString(2, note);
                        preparedStatement.setString(3, dateFormat.format(date));

                        preparedStatement.executeUpdate();
                        issueCount++;
                        check = 1;
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                    check = 0;
                }

                if (check==1) {
                    startAt = startAt + maxResults;
                }
            }

            System.out.println("Total issues:"+total);
            System.out.println("Collected keys:"+issueCount);
            System.out.println("-----------------COMPLETED-------------------");
        }

    }
	
	public static void saveFile(String issue, String filename) throws IOException {	
		java.io.FileWriter fw = new java.io.FileWriter("C:/RiskAssessmentResearch/"+casestudy.getDatesetLocation()+"/rapidboard/"+ filename +".json");
		fw.write(issue);
		System.out.println("File Name " + filename);
		fw.close();
	}
	
	public static String connectJiraAPI(URL url) throws IOException {
		URLConnection urlc = url.openConnection();
        urlc.addRequestProperty("User-Agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)");
        // Authentication is not required by Jira ,WSO2, Java.net
        //String userpass = "username:password";  // apache, duraspace, spring

        //String encoding = Base64Converter.encode(userpass.getBytes("UTF-8"));

        //String basicAuth = "Basic " + new String(new Base64().encode(userpass.getBytes()));
        //urlc.setRequestProperty ("Authorization", basicAuth);
		
		BufferedReader rd = new BufferedReader(new InputStreamReader(urlc.getInputStream()));
		StringBuilder sb = new StringBuilder();
		String line;

		while ((line = rd.readLine()) != null) {
			sb.append(line);
		}
		rd.close();
		return sb.toString();
	}
}
