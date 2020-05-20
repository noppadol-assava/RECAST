/*------Note-------
Created: 13 Jan 2016
Description: this code collects issue with story point > 0 from JIRA. 
This code query a list of issue key from DB 

Issue keys must be prepared by "CollectIssueKey.java" table using this api 
the save location can be modified in saveFile() method
*/
package com.data.collector;

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
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import com.data.utility.json.*;

import org.apache.commons.codec.binary.Base64;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

public class CollectIssue {
	private static int totalSub = 0;
	private static int count =0;
    static ResourcePointer casestudy = new ResourcePointer();
    public void setInputFile(String inputFile) {
    }


    public static void main(String[] args) throws SQLException, IOException, NoSuchAlgorithmException {


        SSLContext ctx = null;
        TrustManager[] trustAllCerts = new X509TrustManager[]{new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers() {
                return null;
            }

            public void checkClientTrusted(X509Certificate[] certs, String authType) {
            }

            public void checkServerTrusted(X509Certificate[] certs, String authType) {
            }
        }};
        try {
            ctx = SSLContext.getInstance("SSL");
            ctx.init(null, trustAllCerts, null);
        } catch (KeyManagementException e) {

        }

        SSLContext.setDefault(ctx);

        casestudy.setRunningCaseStudy();

        ResultSet rs = null;
        Connection connection = null;
        Statement statement = null;

        //------for Jira Decomposition
        String Note = "Collected";
        String query = "Select distinct issuekey from "+casestudy.getDbname()+".task where "
        		+ "issuekey not in (select issuekey from "+casestudy.getDbname()+".temp_collectedissue)";
        
        System.out.println(query);
        connection = JDBCMySQLConnection.getConnection();
        statement = connection.createStatement();
        rs = statement.executeQuery(query);

        while (rs.next()) {
            int check = 0;
            while (check == 0) {
                try {
                    System.out.println(rs.getString("issueKey"));
                    //System.out.println(rs.getString("id"));
                    getIssueDetail(rs.getString("issueKey"), casestudy.getRestApiAddress());
                    //sleepTime(3000);
                    getIssueChangelog(rs.getString("issueKey"), casestudy.getRestApiAddress());
                    //sleepTime(3000);
                    getIssueComment(rs.getString("issueKey"), casestudy.getRestApiAddress());
                    //sleepTime(5000);
                    System.out.println("-------------------------------------------------------");
                    RecordCollectedIssue((rs.getString("issueKey")));
                    check = 1;
                } catch (SQLException e) {
                    e.printStackTrace();
                    check = 0;
                } catch (IOException e) {
                    e.printStackTrace();
                    check = 0;
                }
            }
        }
        System.out.println("TotalSubtask: "+totalSub);
        System.out.println("----------------COMPLETED------------------");
    }

    private static void RecordCollectedIssue(String issuekey, String Note) throws SQLException {
        Connection connection = JDBCMySQLConnection.getConnection();


        String InsertSql = "INSERT INTO `" + casestudy.getDbname() + "`.`temp_collectedissue` "
                + "(`issuekey`) VALUES (?);";
        try {
            PreparedStatement preparedStatement = connection.prepareStatement(InsertSql);
            preparedStatement.setString(1, issuekey);
            preparedStatement.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        String UpdateSql = "Update `" + casestudy.getDbname() + "`.`temp_collectedissue` SET "
                + "Note = ? Where issueKey = ?;";
        try {
            PreparedStatement preparedStatement = connection.prepareStatement(UpdateSql);
            preparedStatement.setString(1, Note);
            preparedStatement.setString(2, issuekey);
            preparedStatement.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        connection.close();
    }
	
    private static void sleepTime(int time) {
        System.out.println("Sleep:" + time);
        try {
            Thread.sleep(time);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void getIssueDetail(String IssueKey, String resturl) throws IOException {
        URL url = new URL("https://" + resturl + "/rest/api/2/issue/"
                + IssueKey);
        System.out.println(url.toString());
        String issue = connectJiraAPI(url).toString();
        System.out.println("connect issue detail:" + IssueKey);
        saveFile(issue, IssueKey);
    }

    public static void getIssueChangelog(String IssueKey, String resturl) throws IOException {
        URL url = new URL("https://" + resturl + "/rest/api/2/issue/"
                + IssueKey + "?expand=changelog");
        String issue = connectJiraAPI(url).toString();
        System.out.println("connect issue changelog:" + IssueKey);
        saveFile(issue, IssueKey + "_CL");
    }

    public static void getIssueComment(String IssueKey, String resturl) throws IOException {
        URL url = new URL("https://" + resturl + "/rest/api/latest/issue/"
                + IssueKey + "/comment");
        String issue = connectJiraAPI(url).toString();
        System.out.println("connect issue comment:" + IssueKey);
        saveFile(issue, IssueKey + "_Comment");
    }

    public static String connectJiraAPI(URL url) throws IOException {
        URLConnection urlc = url.openConnection();
        urlc.addRequestProperty("User-Agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)");
        // Authentication is not required by Jira and WSO2
        //String userpass = "username:password";  // apache, duraspace, spring
       

        //String encoding = Base64Converter.encode(userpass.getBytes("UTF-8"));

//        String basicAuth = "Basic " + new String(new Base64().encode(userpass.getBytes()));
//        urlc.setRequestProperty("Authorization", basicAuth);

        BufferedReader rd = new BufferedReader(new InputStreamReader(urlc.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String line;

        while ((line = rd.readLine()) != null) {
            sb.append(line);
        }
        rd.close();
        return sb.toString();
    }

    public static void saveFile(String issue, String filename) throws IOException {
        java.io.FileWriter fw = new java.io.FileWriter(casestudy.getDatesetLocation() + "/issues/" + filename + ".json");
        fw.write(issue);
        System.out.println("File Name" + filename);
        fw.close();
    }
}
