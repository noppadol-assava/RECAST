CREATE TABLE `task` (
  `issuekey` varchar(30) DEFAULT NULL,
  `Note` varchar(30) DEFAULT NULL,
  `collecttime` date DEFAULT NULL,
  `type` varchar(15) DEFAULT NULL,
  `assignee` varchar(50) DEFAULT NULL,
  `reporter` varchar(50) DEFAULT NULL,
  `tstatus` varchar(30) DEFAULT NULL
);
CREATE TABLE `temp_collectedissue` (
  `issuekey` varchar(30) DEFAULT NULL,
  `Note` varchar(10) DEFAULT NULL
);
CREATE TABLE `subtask` (
  `issuekey` varchar(30) DEFAULT NULL,
  `STstatus` varchar(30) DEFAULT NULL,
  `type` varchar(15) DEFAULT NULL,
  `reporter` varchar(50) DEFAULT NULL,
  `assignee` varchar(50) DEFAULT NULL,
  `collecttime` date DEFAULT NULL,
  `parentKey` varchar(30) DEFAULT NULL
)


----------------------------------------------- new version-----------------------------------------------------------------
CREATE TABLE `collect_key` (
  `issuekey` varchar(30) DEFAULT NULL,
  `Note` varchar(30) DEFAULT NULL,
  `collecttime` date DEFAULT NULL
);
CREATE TABLE `temp_collectedissue` (
  `issuekey` varchar(30) DEFAULT NULL,
  `Note` varchar(10) DEFAULT NULL
);

CREATE TABLE `participant` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  `type` varchar(20),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `user_group` (
  `username` nvarchar(100),
  `groupinfo` varchar(200),
  PRIMARY KEY(`username`,`groupinfo`)
);

CREATE TABLE `temp_collecteduser` (
  `username` nvarchar(100) DEFAULT NULL,
  `Note` varchar(10) DEFAULT NULL
);

CREATE TABLE `user_applicationrole` (
  `username` nvarchar(100) DEFAULT NULL,
  `role` varchar(100) DEFAULT NULL
);

CREATE TABLE `tester` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `assignee` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `reporter` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `component_watcher` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `integrator` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `peer_reviewer` (
  `issuekey` varchar(30),
  `username` nvarchar(100),
  PRIMARY KEY(`issuekey`,`username`)
);

CREATE TABLE `developer` (
  `issuekey` varchar(30),
  `displayname` nvarchar(100),
  `username` nvarchar(100),
  `createtime` datetime,
  PRIMARY KEY(`issuekey`,`displayname`,`createtime`)
);

CREATE TABLE `issue_id` (
  `issuekey` varchar(30),
  `issueid` varchar(30),
  PRIMARY KEY(`issuekey`,`issueid`)
);

CREATE TABLE `user_displayname` (
  `username` nvarchar(100),
  `displayname` nvarchar(100),
  PRIMARY KEY(`username`,`displayname`)
);

CREATE TABLE `issueinformation` (
  `issuekey` varchar(30) DEFAULT NULL,
  `createdate` date DEFAULT NULL,
  `updatedate` date DEFAULT NULL,
  `resolvedate` date DEFAULT NULL,
  `duedate` date DEFAULT NULL,
  `resolution` varchar(100) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `priority` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `title` TEXT DEFAULT NULL
);

CREATE TABLE `process` (
  `issuekey` varchar(30) DEFAULT NULL,
  `statusseq` LONGTEXT DEFAULT NULL
);

CREATE TABLE `changelog` (
  `issuekey` varchar(30) DEFAULT NULL,
  `logid` varchar(30) DEFAULT NULL,
  `username` nvarchar(100) DEFAULT NULL,
  `timecreated` datetime DEFAULT NULL,
  `field` varchar(100) DEFAULT NULL,
  `from` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `fromString` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `to` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `toString` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL 
);

CREATE TABLE `comments` (
  `issuekey` varchar(30) DEFAULT NULL,
  `commentid` varchar(30) DEFAULT NULL,
  `timecreated` datetime DEFAULT NULL
);

CREATE TABLE `tags` (
  `commentid` varchar(30) DEFAULT NULL,
  `tagger` nvarchar(100) DEFAULT NULL,
  `taggee` nvarchar(100) DEFAULT NULL
);

CREATE TABLE `component` (
  `issuekey` varchar(30) DEFAULT NULL,
  `component` nvarchar(200) DEFAULT NULL
);

CREATE TABLE `issuelink` (
  `u` varchar(30) DEFAULT NULL,
  `v` varchar(30) DEFAULT NULL,
  `relation` nvarchar(100) DEFAULT NULL
);

-- PREPARE ROLE --
delete from <role> where username is NULL
-- combine all user--
CREATE TABLE `collect_user` (
  `username` nvarchar(100),
  PRIMARY KEY(`username`)
);

INSERT INTO collect_user (username) SELECT DISTINCT username FROM assignee UNION SELECT DISTINCT username FROM component_watcher UNION SELECT DISTINCT username FROM developer UNION SELECT DISTINCT username FROM integrator UNION SELECT DISTINCT username FROM participant UNION SELECT DISTINCT username FROM peer_reviewer UNION SELECT DISTINCT username FROM reporter UNION SELECT DISTINCT username FROM tester;
-- User and Role table --
CREATE TABLE user_role(
	username nvarchar(100),
    dev boolean,
    integrator boolean,
    tester boolean,
    peer boolean
);

INSERT INTO user_role (username) SELECT DISTINCT username FROM assignee UNION SELECT DISTINCT username FROM component_watcher UNION SELECT DISTINCT username FROM developer UNION SELECT DISTINCT username FROM integrator UNION SELECT DISTINCT username FROM participant UNION SELECT DISTINCT username FROM peer_reviewer UNION SELECT DISTINCT username FROM reporter UNION SELECT DISTINCT username FROM tester;

UPDATE user_role SET dev = TRUE WHERE username in (SELECT DISTINCT username FROM developer);
UPDATE user_role SET integrator = TRUE WHERE username in (SELECT DISTINCT username FROM integrator);
UPDATE user_role SET peer = TRUE WHERE username in (SELECT DISTINCT username FROM peer_reviewer);
UPDATE user_role SET tester = TRUE WHERE username in (SELECT DISTINCT username FROM tester);

-- TEAM --
create view team as
select `issueinformation`.`issuekey` AS `issuekey`,`developer`.`username` AS `dev`,`integrator`.`username` AS `integrator`,`peer_reviewer`.`username` AS `peer`,`tester`.`username` AS `tester` from ((((`issueinformation` left join `developer` on((`issueinformation`.`issuekey` = `developer`.`issuekey`))) left join `integrator` on((`issueinformation`.`issuekey` = `integrator`.`issuekey`))) left join `peer_reviewer` on((`issueinformation`.`issuekey` = `peer_reviewer`.`issuekey`))) left join `tester` on((`issueinformation`.`issuekey` = `tester`.`issuekey`)));
