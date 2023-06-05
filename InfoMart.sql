CREATE VIEW Q1 AS ( SELECT obvname, obvvalue :: FLOAT [][], timestamps FROM satobservationname JOIN satobservationvalue ON valuenamehashkey = obvnamehashkey );

CREATE VIEW Q2 AS (
	SELECT
		grpname,
		obvname,
		val,
		timestamps 
	FROM
		satobservationname
		JOIN (
		SELECT
			grpname,
			observationid,
			val,
			timestamps 
		FROM
			satgroupname
			JOIN ( SELECT observationid, groupid, obvvalue :: FLOAT [][] AS val, timestamps FROM observationgroup JOIN satobservationvalue ON observationid = valuenamehashkey ) AS A ON grpnamehashkey = groupid 
		) AS B ON observationid = obvnamehashkey 
	WHERE
		obvname LIKE'%HBA%' 
	OR obvname LIKE'%.dat' 
	);
	
CREATE VIEW Q3 AS (
	SELECT
		ExperimentSequence,
		ExperimentTitle,
		ExperimentAcronym,
		Treatment 
	FROM
		(
		SELECT A
			.experimenthashkey AS ExperimentSequence,
			A.experimenttimestamp AS ExperimentLoadTime,
			A.experimentrecsrc AS ExperimentRecSrc,
			title AS ExperimentTitle,
			acronym AS ExperimentAcronym 
		FROM
			( hubexperiment JOIN satexperimenttitle ON hubexperiment.experimenthashkey = satexperimenttitle.titlehashkey )
			AS A JOIN ( hubexperiment JOIN satexperimentacronym ON hubexperiment.experimenthashkey = satexperimentacronym.acronymhashkey ) AS B ON A.experimenthashkey = B.experimenthashkey 
		) AS X
	JOIN ( SELECT treatmenthashkey AS treatmenthashkey, treatname AS Treatment, experiment FROM hubtreatment JOIN sattreatmentname ON hubtreatment.treatmenthashkey = sattreatmentname.treatnamehashkey ) AS Y ON X.ExperimentSequence = Y.Experiment 
	);

CREATE VIEW Q4 AS (
	SELECT
		title AS Experiment,
		A.grpname AS GROUP,
		A.sbjname AS ExperimentalUnit 
	FROM
		satexperimenttitle
		JOIN (
		SELECT
			experiment,
			grpname,
			sbjname 
		FROM
			( SELECT * FROM hubtreatment JOIN hubgroup ON treatmenthashkey = treatment )
			AS A JOIN (
			SELECT
				* 
			FROM
				(
				SELECT A
					.groupid,
					grpname,
					sbjnamehashkey,
					sbjname 
				FROM
					( assignedto JOIN satgroupname ON groupid = grpnamehashkey )
					AS A JOIN ( assignedto JOIN satsubjectname ON sbjnamehashkey = experimentalunit ) AS B ON A.assignedtohashkey = B.assignedtohashkey 
				ORDER BY
					groupid 
				) AS X 
			) AS B ON B.groupid = A.grouphashkey 
		) AS A ON titlehashkey = A.experiment 
	ORDER BY
	title 
	);
	
CREATE VIEW Q5 AS (
	SELECT
		obvname,
		metadatakey,
		valuepair 
	FROM
		satobservationname
	JOIN ( SELECT * FROM observationmetadata JOIN satmetadatakeyvaluepair ON metadataid = keyvaluehashkey ) AS A ON obvnamehashkey = observationid 
	);
	
CREATE VIEW Q6 AS (
	SELECT
		obvname,
		subjectname,
		obvvalue :: FLOAT [][],
		timestamps 
	FROM
		satobservationvalue
		JOIN (
		SELECT
			obvname,
			observationhashkey,
			subjectname,
			subjecthashkey 
		FROM
			satobservationname
			JOIN (
			SELECT
				observationhashkey,
				subjectname,
				subjecthashkey,
				B.sessionid 
			FROM
				hubobservation
				JOIN (
				SELECT
					subjectname,
					subjecthashkey,
					A.sessionid 
				FROM
					attendssession
					JOIN ( SELECT subjectname, subjecthashkey, sessionid FROM hubsubject JOIN attendssession ON subjecthashkey = experimentalunit ) AS A ON attendssession.sessionid = A.sessionid 
				) AS B ON B.sessionid = collectedatsession 
			) AS C ON observationhashkey = obvnamehashkey 
		) AS D ON valuenamehashkey = observationhashkey
		WHERE obvname LIKE '%HBA%' OR obvname LIKE '%.dat'
	);