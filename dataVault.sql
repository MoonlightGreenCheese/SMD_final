CREATE TABLE HubExperiment ( 
    ExperimentHashKey TEXT NOT NULL UNIQUE, 
		ExperimentTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ExperimentRecSrc TEXT NOT NULL, 
		PRIMARY KEY ( ExperimentHashKey, ExperimentTimestamp, ExperimentRecSrc ) 
);

CREATE TABLE HubFactor(
    FactorHashKey TEXT NOT NULL UNIQUE, 
		FactorTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		FactorRecSrc TEXT NOT NULL, 
		Experiment TEXT NOT NULL,
		IsCofactor BOOL DEFAULT FALSE,
		PRIMARY KEY ( FactorHashKey, FactorTimestamp, FactorRecSrc ),
		FOREIGN KEY ( Experiment ) REFERENCES HubExperiment ( ExperimentHashKey )
);

CREATE TABLE HubTreatment ( 
    TreatmentHashKey TEXT NOT NULL UNIQUE, 
		TreatmentTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		TreatmentRecSrc TEXT NOT NULL, 
		Experiment TEXT NOT NULL,
		PRIMARY KEY ( TreatmentHashKey, TreatmentTimestamp, TreatmentRecSrc ),
		FOREIGN KEY ( Experiment ) REFERENCES HubExperiment ( ExperimentHashKey )
);

CREATE TABLE HubGroup ( 
    GroupHashKey TEXT NOT NULL UNIQUE, 
		GroupTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		GroupRecSrc TEXT NOT NULL, 
		Treatment TEXT NOT NULL,
		PRIMARY KEY ( GroupHashKey, GroupTimestamp, GroupRecSrc ),
		FOREIGN KEY ( Treatment ) REFERENCES HubTreatment ( TreatmentHashKey )
);

CREATE TABLE HubExperimentalUnit ( 
    ExpUnitHashKey TEXT NOT NULL UNIQUE, 
		ExpUnitTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ExpUnitRecSrc TEXT NOT NULL, 
		PRIMARY KEY ( ExpUnitHashKey, ExpUnitTimestamp, ExpUnitRecSrc ) 
);

CREATE TABLE HubSubject ( 
    SubjectHashKey TEXT NOT NULL UNIQUE, 
		SubjectTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		SubjectRecSrc TEXT NOT NULL,
		SubjectName VARCHAR(40), 
		PRIMARY KEY ( SubjectHashKey, SubjectTimestamp, SubjectRecSrc ) 
);


CREATE TABLE HubSession ( 
    SessionHashKey TEXT NOT NULL UNIQUE, 
		SessionTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		SessionRecSrc TEXT NOT NULL,
		PRIMARY KEY ( SessionHashKey, SessionTimestamp, SessionRecSrc ) 
);

CREATE TABLE HubObservation ( 
    ObservationHashKey TEXT NOT NULL UNIQUE, 
		ObservationTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ObservationRecSrc TEXT NOT NULL,
		CollectedAtSession TEXT NOT NULL,
		PRIMARY KEY ( ObservationHashKey, ObservationTimestamp, ObservationRecSrc ),
		FOREIGN KEY ( CollectedAtSession ) REFERENCES HubSession ( SessionHashKey )
);

CREATE TABLE HubMetaData ( 
    MetaDataHashKey TEXT NOT NULL UNIQUE, 
		MetaDataTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		MetaDataRecSrc TEXT NOT NULL,
		PRIMARY KEY ( MetaDataHashKey, MetaDataTimestamp, MetaDataRecSrc ) 
);


------------------------------------

CREATE TABLE ParticipatesIn(
    ParticipatesInHashKey TEXT NOT NULL UNIQUE, 
		ParticipatesInTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ParticipatesInRecSrc TEXT NOT NULL,
		ExperimentalUnit TEXT NOT NULL,
		ExperimentID TEXT NOT NULL,
		PRIMARY KEY ( ParticipatesInHashKey, ParticipatesInTimestamp, ParticipatesInRecSrc ),
		FOREIGN KEY ( ExperimentalUnit ) REFERENCES HubExperimentalUnit ( ExpUnitHashKey ),
		FOREIGN KEY ( ExperimentID ) REFERENCES HubExperiment ( ExperimentHashKey )
);

CREATE TABLE AssignedTo(
    AssignedToHashKey TEXT NOT NULL UNIQUE, 
		AssignedToTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		AssignedToRecSrc TEXT NOT NULL,
		ExperimentalUnit TEXT NOT NULL,
		GroupID TEXT NOT NULL,
		PRIMARY KEY ( AssignedToHashKey, AssignedToTimestamp, AssignedToRecSrc ),
		FOREIGN KEY ( ExperimentalUnit ) REFERENCES HubExperimentalUnit ( ExpUnitHashKey ),
		FOREIGN KEY ( GroupID ) REFERENCES HubGroup ( GroupHashKey )
);

CREATE TABLE AttendsSession(
    AttendHashKey TEXT NOT NULL UNIQUE, 
		AttendTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		AttendRecSrc TEXT NOT NULL,
		ExperimentalUnit TEXT NOT NULL,
		GroupID TEXT NOT NULL,
		SessionID TEXT NOT NULL,
		PRIMARY KEY ( AttendHashKey, AttendTimestamp, AttendRecSrc ),
		FOREIGN KEY ( ExperimentalUnit ) REFERENCES HubExperimentalUnit ( ExpUnitHashKey ),
		FOREIGN KEY ( GroupID ) REFERENCES HubGroup ( GroupHashKey ),
		FOREIGN KEY ( SessionID ) REFERENCES HubSession ( SessionHashKey )
);


CREATE TABLE SessionMetaData(
    SessionMDHashKey TEXT NOT NULL UNIQUE, 
		SessionMDTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		SessionMDRecSrc TEXT NOT NULL,
		SessionID TEXT NOT NULL,
		MetaDataID TEXT NOT NULL,
		PRIMARY KEY ( SessionMDHashKey, SessionMDTimestamp, SessionMDRecSrc ),
		FOREIGN KEY ( SessionID ) REFERENCES HubSession ( SessionHashKey ),
		FOREIGN KEY ( MetaDataID ) REFERENCES HubMetaData ( MetaDataHashKey )
);

CREATE TABLE ObservationMetaData(
    ObservationMDHashKey TEXT NOT NULL UNIQUE, 
		ObservationMDTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ObservationMDRecSrc TEXT NOT NULL,
		ObservationID TEXT NOT NULL,
		MetaDataID TEXT NOT NULL,
		PRIMARY KEY ( ObservationMDHashKey, ObservationMDTimestamp, ObservationMDRecSrc ),
		FOREIGN KEY ( ObservationID ) REFERENCES HubObservation ( ObservationHashKey ),
		FOREIGN KEY ( MetaDataID ) REFERENCES HubMetaData ( MetaDataHashKey )
);

CREATE TABLE ObservationGroup(
	  ObvGrpHashKey TEXT NOT NULL UNIQUE, 
	  ObvGrpTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	  ObvGrpRecSrc TEXT NOT NULL,
	  ObservationID TEXT NOT NULL,
		GroupID TEXT NOT NULL,
		PRIMARY KEY ( ObvGrpHashKey, ObvGrpTimestamp, ObvGrpRecSrc ),
		FOREIGN KEY ( ObservationID ) REFERENCES HubObservation ( ObservationHashKey ),
		FOREIGN KEY ( GroupID ) REFERENCES HubGroup ( GroupHashKey )
);


------------------------------------

CREATE TABLE SatExperimentUnitIdentifier ( 
    UnitIDHashKey TEXT NOT NULL, 
		UnitIDTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		UnitIDRecSrc TEXT NOT NULL,
		ID VARCHAR(15), 
		PRIMARY KEY ( UnitIDHashKey, UnitIDTimestamp, UnitIDRecSrc ),
		FOREIGN KEY ( UnitIDHashKey ) REFERENCES ParticipatesIn ( ParticipatesInHashKey )
);

CREATE TABLE SatExperimentTitle ( 
    TitleHashKey TEXT NOT NULL, 
		TitleTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		TitleRecSrc TEXT NOT NULL,
		Title VARCHAR(255), 
		PRIMARY KEY ( TitleHashKey, TitleTimestamp, TitleRecSrc ),
		FOREIGN KEY ( TitleHashKey ) REFERENCES HubExperiment ( ExperimentHashKey )
);

CREATE TABLE SatExperimentAcronym ( 
    AcronymHashKey TEXT NOT NULL, 
		AcronymTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		AcronymRecSrc TEXT NOT NULL,
		Acronym VARCHAR(15), 
		PRIMARY KEY ( AcronymHashKey, AcronymTimestamp, AcronymRecSrc ),
		FOREIGN KEY ( AcronymHashKey ) REFERENCES HubExperiment ( ExperimentHashKey )
);

CREATE TABLE SatSubjectAge ( 
    AgeHashKey TEXT NOT NULL, 
		AgeTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		AgeRecSrc TEXT NOT NULL,
		Age INT, 
		PRIMARY KEY ( AgeHashKey, AgeTimestamp, AgeRecSrc ),
		FOREIGN KEY ( AgeHashKey ) REFERENCES HubSubject ( SubjectHashKey )
);

CREATE TABLE SatSubjectName ( 
    SbjNameHashKey TEXT NOT NULL, 
		SbjNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		SbjNameRecSrc TEXT NOT NULL,
		SbjName VARCHAR(40), 
		PRIMARY KEY ( SbjNameHashKey, SbjNameTimestamp, SbjNameRecSrc ),
		FOREIGN KEY ( SbjNameHashKey ) REFERENCES HubSubject ( SubjectHashKey )
);

CREATE TABLE SatMetaDataKeyValuePair ( 
    KeyValueHashKey TEXT NOT NULL, 
		KeyValueTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		KeyValueRecSrc TEXT NOT NULL,
		MetaDataKey VARCHAR(40) NOT NULL,
		ValuePair TEXT, 
		PRIMARY KEY ( KeyValueHashKey, KeyValueTimestamp, KeyValueRecSrc ),
		FOREIGN KEY ( KeyValueHashKey ) REFERENCES HubMetaData ( MetaDataHashKey )
);

CREATE TABLE SatGroupName ( 
    GrpNameHashKey TEXT NOT NULL, 
		GrpNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		GrpNameRecSrc TEXT NOT NULL,
		GrpName VARCHAR(40), 
		PRIMARY KEY ( GrpNameHashKey, GrpNameTimestamp, GrpNameRecSrc ),
		FOREIGN KEY ( GrpNameHashKey ) REFERENCES HubGroup ( GroupHashKey )
);

CREATE TABLE SatSessionName ( 
    SsnNameHashKey TEXT NOT NULL, 
		SsnNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		SsnNameRecSrc TEXT NOT NULL,
		SsnName VARCHAR(40), 
		PRIMARY KEY ( SsnNameHashKey, SsnNameTimestamp, SsnNameRecSrc ),
		FOREIGN KEY ( SsnNameHashKey ) REFERENCES HubSession ( SessionHashKey )
);

CREATE TABLE SatObservationName ( 
    ObvNameHashKey TEXT NOT NULL, 
		ObvNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ObvNameRecSrc TEXT NOT NULL,
		ObvName VARCHAR(40), 
		PRIMARY KEY ( ObvNameHashKey, ObvNameTimestamp, ObvNameRecSrc ),
		FOREIGN KEY ( ObvNameHashKey ) REFERENCES HubObservation ( ObservationHashKey )
);

CREATE TABLE SatObservationValue ( 
    ValueNameHashKey TEXT NOT NULL, 
		ValueNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		ValueNameRecSrc TEXT NOT NULL,
		ObvValue VARCHAR[][],
		timestamps VARCHAR[],
		PRIMARY KEY ( ValueNameHashKey, ValueNameTimestamp, ValueNameRecSrc ),
		FOREIGN KEY ( ValueNameHashKey ) REFERENCES HubObservation ( ObservationHashKey )
);

CREATE TABLE SatFactorName ( 
    FctNameHashKey TEXT NOT NULL, 
		FctNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		FctNameRecSrc TEXT NOT NULL,
		FctName VARCHAR(40), 
		PRIMARY KEY ( FctNameHashKey, FctNameTimestamp, FctNameRecSrc ),
		FOREIGN KEY ( FctNameHashKey ) REFERENCES HubFactor ( FactorHashKey )
);

CREATE TABLE SatTreatmentName ( 
    TreatNameHashKey TEXT NOT NULL, 
		TreatNameTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		TreatNameRecSrc TEXT NOT NULL,
		TreatName VARCHAR(40), 
		PRIMARY KEY ( TreatNameHashKey, TreatNameTimestamp, TreatNameRecSrc ),
		FOREIGN KEY ( TreatNameHashKey ) REFERENCES HubTreatment ( TreatmentHashKey )
);

CREATE TABLE SatFactorLevel ( 
    LevelHashKey TEXT NOT NULL, 
		LevelTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		LevelRecSrc TEXT NOT NULL,
		LevelValue VARCHAR(40), 
		PRIMARY KEY ( LevelHashKey, LevelTimestamp, LevelRecSrc ),
		FOREIGN KEY ( LevelHashKey ) REFERENCES HubFactor ( FactorHashKey )
);

CREATE TABLE SatTreatmentFactorLevel ( 
    TreatLevelHashKey TEXT NOT NULL, 
		TreatLevelTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
		TreatLevelRecSrc TEXT NOT NULL,
		TreatLevelValue TEXT NOT NULL,
		PRIMARY KEY ( TreatLevelHashKey, TreatLevelTimestamp, TreatLevelRecSrc ),
		FOREIGN KEY ( TreatLevelHashKey ) REFERENCES HubTreatment ( TreatmentHashKey )
);



