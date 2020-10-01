package com.data.utility.json;

public class ResourcePointer {

    private String IssueListLocation;
    private String JsonFileLocation;
    private String casestudy;
    private String RestApiAddress;
    private String dbname;
    private String DatesetLocation;


    private String UserPass;

    public void setRunningCaseStudy() {


//        setApache();
    	setMoodle();
//        setAtlassian();

    }


    public String getDatesetLocation() {
        return DatesetLocation;
    }

    public void setDatesetLocation(String datesetLocation) {
        DatesetLocation = datesetLocation;
    }

    public String getDbname() {
        return dbname;
    }

    public void setDbname(String dbname) {
        this.dbname = dbname;
    }

    public String getRestApiAddress() {
        return RestApiAddress;
    }

    public void setRestApiAddress(String restApiAddress) {
        RestApiAddress = restApiAddress;
    }

    public String getCasestudy() {
        return casestudy;
    }

    public void setCasestudy(String casestudy) {
        this.casestudy = casestudy;
    }

4
    /**
     * @return the jsonFileLocation
     */
    public String getJsonFileLocation() {
        return JsonFileLocation;
    }

    /**
     * @param jsonFileLocation the jsonFileLocation to set JSON file location
     */
    public void setJsonFileLocation(String jsonFileLocation) {
        JsonFileLocation = jsonFileLocation;
    }



    public void setMoodle() {
        System.out.println("Current case study: Moodle");
        setCasestudy("Moodle");
//        setRestApiAddress("jira.moodle.org");
        setRestApiAddress("tracker.moodle.org");
        setDbname("Moodle");
        setDatesetLocation("MoodleDataSet");
        setJsonFileLocation("MoodleDataSet");
    }


    public void setApache() {
        System.out.println("Current case study: Apache");
        setCasestudy("Apache");
        setRestApiAddress("issues.apache.org/jira");
        setDbname("apache_ph2");
        setDatesetLocation("ApacheDataSet");
        setJsonFileLocation("ApacheDataSet");
    }

    public void setAtlassian() {
        System.out.println("Current case study: Atlassian");
        setCasestudy("Jira");
        setRestApiAddress("jira.atlassian.com");
        setDbname("jira");
        setDatesetLocation("JiraDataSet");
        setJsonFileLocation("AtlassianDataSet");
    }

}
