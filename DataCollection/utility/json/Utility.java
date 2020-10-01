package com.data.utility.json;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.text.ParseException;
import java.text.SimpleDateFormat;

import jxl.Workbook;
import jxl.read.biff.BiffException;

public class Utility {

	public Workbook getWorkbook(String InputFile) {
		File InputWorkbookFile = new File(InputFile.toString());
		Workbook IssueWorkbook = null;
		try {
			IssueWorkbook = Workbook.getWorkbook(InputWorkbookFile);

		} catch (BiffException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return IssueWorkbook;
	}

	public Workbook getWorkbook() {
		ResourcePointer Resource = new ResourcePointer();
		Resource.setResourceLocation();
		System.out.println("Issue List Location:"
				+ Resource.getIssueListLocation());
		System.out.println("JSON file Location:"
				+ Resource.getJsonFileLocation());
		File InputWorkbookFile = new File(Resource.getIssueListLocation());
		Workbook IssueWorkbook = null;
		try {
			IssueWorkbook = Workbook.getWorkbook(InputWorkbookFile);

		} catch (BiffException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return IssueWorkbook;
	}

	public Timestamp ConvertStringToDate(String date,int number) {
		Timestamp crtdate = null;
		if (date != null) {
			date = date.replace("T", " ");
			date = date.substring(0, number);
			
			SimpleDateFormat format;
			if (number == 19) {
				format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
			}else{
				format = new SimpleDateFormat("yyyy-MM-dd");
			}
			java.util.Date parsed = null;
			try {
				parsed = format.parse(date);
			} catch (ParseException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			crtdate = new java.sql.Timestamp(parsed.getTime());
		}
		return crtdate;
	}
	
	public Timestamp ConvertStringToDate(String date) {
		Timestamp crtdate = null;
		if (date != null) {
			date = date.replace("T", " ");
			date = date.substring(0,19);
			//System.out.println("convert " + date);
			
			SimpleDateFormat format;
			format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		
			java.util.Date parsed = null;
			try {
				parsed = format.parse(date);
				//System.out.println(parsed.getTime());
			} catch (ParseException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			crtdate = new java.sql.Timestamp(parsed.getTime());
		}
		return crtdate;
	}
	
	public Timestamp ConvertStringToDate2(String date) {
		Timestamp crtdate = null;
		
		if (!date.equals("None")) {
			if (date != null) {
				//date = date.replace("T", " ");
				//date = date.substring(0,19);
				//System.out.println("convert " + date);

				SimpleDateFormat format;
				format = new SimpleDateFormat("dd/MMM/yy KK:mm a");

				java.util.Date parsed = null;
				try {
					parsed = format.parse(date);
					//System.out.println(parsed.getTime());
				} catch (ParseException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				crtdate = new java.sql.Timestamp(parsed.getTime());
			}
			
		}
		return crtdate;
	}
	
	public float SQLDateDiff(Timestamp after, Timestamp before) throws SQLException{
		float timediff = 0;
		String TimeDiffQuery = "select datediff('"+after+"','"+before+"') as datediff";
		
		ResultSet rs = null;
		Connection connection = null;
		Statement statement = null;
		
		try {
			connection = JDBCMySQLConnection.getConnection();
			statement = connection.createStatement();
			rs = statement.executeQuery(TimeDiffQuery);
			rs.next();
			timediff = rs.getFloat("datediff");
			rs.close();
		} catch (SQLException e) {
			e.printStackTrace();
		} finally {
			if (connection != null) {
				try {
					connection.close();
				} catch (SQLException e) {
					e.printStackTrace();
				}
			}

		}
		connection.close();
		return timediff;
	}
}