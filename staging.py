import pandas as pd
import os
import hashlib
import psycopg2


def ReadLoadMetadata1(filepath):
    files_list = os.listdir(filepath)  # get file names

    tmp1 = []
    tmp2 = []

    for file in files_list:
        f = pd.read_csv(filepath + "\\" + file, header=None)
        column_name = f.iloc[1:18][0]

        values = f.iloc[1:18][1].copy()

        values[12] = f.iloc[12][1:3].values.tolist()
        values[15] = f.iloc[16][0:20].values.tolist()

        to_Series = pd.Series(values.tolist(), index=column_name)
        to_Series = to_Series.drop(['A'])

        print("filename:  " + str(file))

        if to_Series["ID"] == "VM0004_Viso" and str(file).find("VM0004_ViMo") != -1:
            to_Series["ID"] = "VM0004_ViMo"

        if to_Series["ID"] not in tmp1:
            # insert data into table "HubSession"
            insert_sql = "INSERT INTO HubSession(SessionHashKey, SessionRecSrc) VALUES(%s, %s) ON CONFLICT (SessionHashKey, SessionTimestamp, SessionRecSrc) DO NOTHING; "
            tmp = [(GetHash(to_Series["ID"]),
                    GetHash(filepath[filepath.rfind('\\') + 1:]))]
            curs.executemany(insert_sql, tmp)

            # insert data into table "SatSessionName"
            insert_sql = "INSERT INTO SatSessionName(SsnNameHashKey, SsnNameRecSrc, SsnName) VALUES(%s, %s, %s) ON CONFLICT (SsnNameHashKey,SsnNameTimestamp, SsnNameRecSrc) DO NOTHING; "
            tmp = [(GetHash(to_Series["ID"]),
                    GetHash(filepath[filepath.rfind('\\') + 1:]),
                    to_Series["ID"])]
            curs.executemany(insert_sql, tmp)

            tmp1.append(to_Series["ID"])

        if to_Series["Name"] not in tmp2:
            # insert data into table "HubExperimentalUnit"
            insert_sql = "INSERT INTO HubExperimentalUnit(ExpUnitHashKey, ExpUnitRecSrc) VALUES(%s, %s) ON CONFLICT (ExpUnitHashKey, ExpUnitTimestamp, ExpUnitRecSrc) DO NOTHING;"
            tmp = [(GetHash(to_Series["Name"]),
                    GetHash(filepath[filepath.rfind('\\') + 1:]))]
            curs.executemany(insert_sql, tmp)

            # insert data into table "HubSubject"
            insert_sql = "INSERT INTO HubSubject(SubjectHashKey, SubjectRecSrc, SubjectName) VALUES(%s, %s, %s) ON CONFLICT (SubjectHashKey, SubjectTimestamp, SubjectRecSrc) DO UPDATE SET SubjectName = EXCLUDED.SubjectName;"
            tmp = [(GetHash(to_Series["Name"]),
                    GetHash(filepath[filepath.rfind('\\') + 1:]),
                    to_Series["Name"])]
            curs.executemany(insert_sql, tmp)

            # insert data into table "SatSubjectName"
            insert_sql = "INSERT INTO SatSubjectName(SbjNameHashKey, SbjNameRecSrc, SbjName) VALUES(%s, %s, %s) ON CONFLICT (SbjNameHashKey, SbjNameTimestamp, SbjNameRecSrc) DO NOTHING;"
            tmp = [(GetHash(to_Series["Name"]),
                    GetHash(filepath[filepath.rfind('\\') + 1:]),
                    to_Series["Name"])]
            curs.executemany(insert_sql, tmp)

            # insert data into table "SatSubjectAge"
            insert_sql = "INSERT INTO SatSubjectAge(AgeHashKey, AgeRecSrc, Age) VALUES(%s, %s, %s) ON CONFLICT (AgeHashKey, AgeTimestamp, AgeRecSrc) DO NOTHING;"
            tmp = [(GetHash(to_Series["Name"]),
                    GetHash(filepath[filepath.rfind('\\') + 1:]),
                    int(to_Series["Age"][:to_Series["Age"].rfind('y')]))]
            curs.executemany(insert_sql, tmp)

            # insert data into table "ParticipatesIn"
            insert_sql = "INSERT INTO ParticipatesIn(ParticipatesInHashKey, ParticipatesInRecSrc, ExperimentalUnit, ExperimentID) VALUES(%s, %s, %s, %s) ON CONFLICT (ParticipatesInHashKey, ParticipatesInTimestamp, ParticipatesInRecSrc) DO NOTHING;"
            tmp = [(GetHash(to_Series["Name"] + "VM"),
                    GetHash(filepath[filepath.rfind('\\') + 1:]),
                    GetHash(to_Series["Name"]),
                    GetHash("VM"))]
            curs.executemany(insert_sql, tmp)

            # insert data into table "SatExperimentUnitIdentifier"
            insert_sql = "INSERT INTO SatExperimentUnitIdentifier(UnitIDHashKey, UnitIDRecSrc, ID) VALUES(%s, %s, %s) ON CONFLICT (UnitIDHashKey, UnitIDTimestamp, UnitIDRecSrc) DO NOTHING;"
            tmp = [(GetHash(to_Series["Name"] + "VM"),
                    GetHash(filepath[filepath.rfind('\\') + 1:]),
                    to_Series["ID"][0:to_Series["ID"].find('_')])]
            curs.executemany(insert_sql, tmp)

            tmp2.append(to_Series["Name"])

        # insert data into table "AssignedTo"
        insert_sql = "INSERT INTO AssignedTo(AssignedToHashKey, AssignedToRecSrc, ExperimentalUnit, GroupID) VALUES(%s, %s, %s, %s) ON CONFLICT (AssignedToHashKey, AssignedToTimestamp, AssignedToRecSrc) DO NOTHING;"
        tmp = [(GetHash(to_Series["Name"] + to_Series["ID"][to_Series["ID"].rfind("_") + 1:]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                GetHash(to_Series["Name"]),
                GetHash(to_Series["ID"][to_Series["ID"].rfind("_") + 1:]))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "AttendsSession"
        insert_sql = "INSERT INTO AttendsSession(AttendHashKey, AttendRecSrc, ExperimentalUnit, GroupID, SessionID) VALUES(%s, %s, %s, %s, %s) ON CONFLICT (AttendHashKey, AttendTimestamp, AttendRecSrc) DO NOTHING;"
        tmp = [(GetHash(to_Series["Name"] + to_Series["ID"]),
                GetHash(filepath[filepath.rfind('\\') + 1:]), GetHash(to_Series["Name"]),
                GetHash(to_Series["ID"][to_Series["ID"].rfind("_") + 1:]),
                GetHash(to_Series["ID"]))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "HubObservation"
        insert_sql = "INSERT INTO HubObservation(ObservationHashKey, ObservationRecSrc, CollectedAtSession) VALUES(%s, %s, %s) ON CONFLICT (ObservationHashKey, ObservationTimestamp, ObservationRecSrc) DO UPDATE SET CollectedAtSession=EXCLUDED.CollectedAtSession;"
        tmp = [(GetHash(file[0:file.rfind('.')]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                GetHash(to_Series["ID"]))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "ObservationGroup"
        insert_sql = "INSERT INTO ObservationGroup(ObvGrpHashKey, ObvGrpRecSrc, ObservationID, GroupID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObvGrpHashKey, ObvGrpTimestamp, ObvGrpRecSrc) DO UPDATE SET ObservationID=EXCLUDED.ObservationID,GroupID=EXCLUDED.GroupID;"
        tmp = [(GetHash(file[0:file.rfind('.')] + to_Series["ID"][to_Series["ID"].rfind("_") + 1:]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                GetHash(file[0:file.rfind('.')]),
                GetHash(to_Series["ID"][to_Series["ID"].rfind("_") + 1:]))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "SatObservationName"
        insert_sql = "INSERT INTO SatObservationName(ObvNameHashKey, ObvNameRecSrc, ObvName) VALUES(%s, %s, %s) ON CONFLICT (ObvNameHashKey, ObvNameTimestamp, ObvNameRecSrc) DO UPDATE SET ObvName=EXCLUDED.ObvName;"
        tmp = [(GetHash(file[0:file.rfind('.')]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                file[0:file.rfind('.')])]
        curs.executemany(insert_sql, tmp)

        # insert data into table "HubMetaData"
        insert_sql = "INSERT INTO HubMetaData(MetaDataHashKey, MetaDataRecSrc) VALUES(%s, %s) ON CONFLICT (MetaDataHashKey, MetaDataTimestamp, MetaDataRecSrc) DO NOTHING;"
        tmp = [(GetHash(file[0:file.rfind('.')] + "MD"),
                GetHash(filepath[filepath.rfind('\\') + 1:]))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "SessionMetaData"
        insert_sql = "INSERT INTO SessionMetaData(SessionMDHashKey, SessionMDRecSrc, SessionID, MetaDataID) VALUES(%s, %s, %s, %s) ON CONFLICT (SessionMDHashKey, SessionMDTimestamp, SessionMDRecSrc) DO NOTHING;"
        tmp = [(GetHash(file[0:file.rfind('.')] + "MD" + to_Series["ID"]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                GetHash(to_Series["ID"]),
                GetHash(file[0:file.rfind('.')] + "MD"))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "ObservationMetaData"
        insert_sql = "INSERT INTO ObservationMetaData(ObservationMDHashKey, ObservationMDRecSrc, ObservationID, MetaDataID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObservationMDHashKey, ObservationMDTimestamp, ObservationMDRecSrc) DO NOTHING;"
        tmp = [(GetHash(file[0:file.rfind('.')] + "MD" + file[0:file.rfind('.')]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                GetHash(file[0:file.rfind('.')]),
                GetHash(file[0:file.rfind('.')] + "MD"))]
        curs.executemany(insert_sql, tmp)

        # insert data into table "SatMetaDataKeyValuePair"
        for key in to_Series.index.to_list():
            insert_sql = "INSERT INTO SatMetaDataKeyValuePair(KeyValueHashKey, KeyValueRecSrc, MetaDataKey, ValuePair) VALUES(%s, %s, %s, %s);"
            tmp = [(GetHash(file[0:file.rfind('.')] + "MD"),
                    GetHash(filepath[filepath.rfind('\\') + 1:] + key),
                    key,
                    str(to_Series[key]))]
            curs.executemany(insert_sql, tmp)

    conn.commit()

    print("```````````````````````End Reading Dataset1-MetaData```````````````````````")
    return


def ReadLoadData1(filepath):
    files_list = os.listdir(filepath)  # get file names

    for file in files_list:
        f = pd.read_csv(filepath + "\\" + file, skiprows=27, header=None)

        column_name = f.iloc[0][1:].dropna()
        size = column_name.size

        values = f.iloc[1:, 1:size + 1]

        to_DataFrame = pd.DataFrame(values.values, columns=column_name)

        print("filename:  " + str(file))
        obv_value = to_DataFrame.loc[:, :"Mark"]

        tmp = []

        for col in obv_value:
            tmp.append(lst2pgarr(numlst2strlst(to_DataFrame[col].tolist())))

        pg_arr = lst2pgarr(tmp)

        timestamps = lst2pgarr(numlst2strlst(to_DataFrame.loc[:, "Time"]))

        # insert data into table "SatObservationValue"
        insert_sql = "INSERT INTO SatObservationValue(ValueNameHashKey, ValueNameRecSrc, ObvValue, Timestamps) VALUES(%s, %s, %s, %s) ON CONFLICT (ValueNameHashKey, ValueNameTimestamp, ValueNameRecSrc) DO UPDATE SET ObvValue=EXCLUDED.ObvValue,Timestamps=EXCLUDED.Timestamps;"
        tmp = [(GetHash(file[0:file.rfind('.')]),
                GetHash(filepath[filepath.rfind('\\') + 1:]),
                pg_arr,
                timestamps)]
        curs.executemany(insert_sql, tmp)

    conn.commit()
    print("```````````````````````End Reading Dataset1-Data```````````````````````")
    return


def find_field(file, fieldName):
    line = file.readline()
    while line:
        if ('[' + fieldName + ']') in line:
            return True
        line = file.readline()
    return False


def find_kv(file):
    tmp_k = []
    tmp_v = []
    line = file.readline()

    while '=' in line:
        key = line[:line.rfind('=')]
        value = line[line.rfind('=') + 1:]
        tmp_k.append(key)
        tmp_v.append(value[:value.rfind('\\')])
        line = file.readline()

    to_Series = pd.Series(tmp_v, index=tmp_k)
    return to_Series


def GetHash(s):
    new_md5 = hashlib.md5()
    new_md5.update(s.encode("utf8"))
    ret = new_md5.hexdigest()
    return ret


def numlst2strlst(alist):
    strlist = [str(num) for num in alist]
    return strlist


def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'


def ReadLoadData2(filepath):
    tmp1 = []

    for root, dirs, files in os.walk(filepath):
        for d in dirs:

            ss_hk = ""
            dathk = ""
            hdrhk = ""
            evthk = ""

            filedir = filepath + "\\" + d

            for filelist in os.walk(filedir):
                for f in filelist:
                    for file in f:
                        file = d + "\\" + file
                        if file.endswith(".hdr"):
                            with open(filepath + "\\" + file, encoding='gbk', errors='ignore') as f:
                                print(file)

                                find_field(f, "GeneralInfo")
                                key_value = find_kv(f)

                                # insert data into table "HubMetaData"
                                insert_sql = "INSERT INTO HubMetaData(MetaDataHashKey, MetaDataRecSrc) VALUES(%s, %s) ON CONFLICT (MetaDataHashKey, MetaDataTimestamp, MetaDataRecSrc) DO NOTHING;"
                                tmp = [(GetHash(file + "MD"),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]))]
                                curs.executemany(insert_sql, tmp)

                                hdrhk = GetHash(file + "MD")

                                # insert data into table "SessionMetaData"
                                insert_sql = "INSERT INTO SessionMetaData(SessionMDHashKey, SessionMDRecSrc, SessionID, MetaDataID) VALUES(%s, %s, %s, %s) ON CONFLICT (SessionMDHashKey, SessionMDTimestamp, SessionMDRecSrc) DO NOTHING;"
                                tmp = [(GetHash(file + "MD") + ss_hk,
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        ss_hk,
                                        GetHash(file + "MD"))]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "ObservationMetadata"
                                insert_sql = "INSERT INTO ObservationMetadata(ObservationMDHashKey, ObservationMDRecSrc, ObservationID, MetadataID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObservationMDHashKey, ObservationMDTimestamp, ObservationMDRecSrc) DO UPDATE SET ObservationID=EXCLUDED.ObservationID,MetadataID=EXCLUDED.MetadataID;"
                                tmp = [(dathk + GetHash(file + "MD"),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        dathk,
                                        GetHash(file + "MD"))]
                                curs.executemany(insert_sql, tmp)

                                for key in key_value.index.to_list():
                                    insert_sql = "INSERT INTO SatMetaDataKeyValuePair(KeyValueHashKey, KeyValueRecSrc, MetaDataKey, ValuePair) VALUES(%s, %s, %s, %s);"
                                    tmp = [(GetHash(file + "MD"),
                                            GetHash(filepath[filepath.rfind('\\') + 1:] + key),
                                            key,
                                            str(key_value[key]))]
                                    curs.executemany(insert_sql, tmp)

                                # conn.commit()

                        if file.endswith(".evt"):
                            with open(filepath + "\\" + file, encoding='gbk', errors='ignore') as f:
                                print(file)

                                try:
                                    # insert data into table "HubMetaData"
                                    insert_sql = "INSERT INTO HubMetaData(MetaDataHashKey, MetaDataRecSrc) VALUES(%s, %s) ON CONFLICT (MetaDataHashKey, MetaDataTimestamp, MetaDataRecSrc) DO NOTHING;"
                                    tmp = [(GetHash(file + "MD"),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]))]
                                    curs.executemany(insert_sql, tmp)

                                    evthk = GetHash(file + "MD")

                                    # insert data into table "SessionMetaData"
                                    insert_sql = "INSERT INTO SessionMetaData(SessionMDHashKey, SessionMDRecSrc, SessionID, MetaDataID) VALUES(%s, %s, %s, %s) ON CONFLICT (SessionMDHashKey, SessionMDTimestamp, SessionMDRecSrc) DO NOTHING;"
                                    tmp = [(GetHash(file + "MD" + file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            GetHash(file[:file.find('-')]),
                                            GetHash(file + "MD"))]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "ObservationMetadata"
                                    insert_sql = "INSERT INTO ObservationMetadata(ObservationMDHashKey, ObservationMDRecSrc, ObservationID, MetadataID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObservationMDHashKey, ObservationMDTimestamp, ObservationMDRecSrc) DO UPDATE SET ObservationID=EXCLUDED.ObservationID,MetadataID=EXCLUDED.MetadataID;"
                                    tmp = [(dathk + GetHash(file + "MD"),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            dathk,
                                            GetHash(file + "MD"))]
                                    curs.executemany(insert_sql, tmp)

                                    df = pd.read_csv(f, sep="	", header=None, index_col=0, engine='python')
                                    for index, row in df.iterrows():
                                        value = ""
                                        for i in row.index:
                                            value += str(row[i])

                                        # insert data into table "SatMetaDataKeyValuePair"
                                        insert_sql = "INSERT INTO SatMetaDataKeyValuePair(KeyValueHashKey, KeyValueRecSrc, MetaDataKey, ValuePair) VALUES(%s, %s, %s, %s);"
                                        tmp = [(GetHash(file + "MD"),
                                                GetHash(
                                                    filepath[filepath.rfind('\\') + 1:] + str(index)),
                                                index,
                                                value)]
                                        curs.executemany(insert_sql, tmp)

                                except pd.errors.EmptyDataError:
                                    evthk = "Empty .evt File"
                                    print("Get empty .evt file. Please check if the data is properly collected.")

                        if file.endswith(".dat"):
                            with open(filepath + "\\" + file, encoding='gbk', errors='ignore') as f:
                                print(file)

                                ss_hk = GetHash(file[:file.find('-')])

                                if file[:file.find('-')] not in tmp1:
                                    tmp1.append(file[:file.find('-')])

                                    # insert data into table "HubSession"
                                    insert_sql = "INSERT INTO HubSession(SessionHashKey, SessionRecSrc) VALUES(%s, %s) ON CONFLICT (SessionHashKey, SessionTimestamp, SessionRecSrc) DO NOTHING; "
                                    tmp = [(GetHash(file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]))]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "SatSessionName"
                                    insert_sql = "INSERT INTO SatSessionName(SsnNameHashKey, SsnNameRecSrc, SsnName) VALUES(%s, %s, %s) ON CONFLICT (SsnNameHashKey,SsnNameTimestamp, SsnNameRecSrc) DO NOTHING; "
                                    tmp = [(GetHash(file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            file[:file.find('-')])]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "HubExperimentalUnit"
                                    insert_sql = "INSERT INTO HubExperimentalUnit(ExpUnitHashKey, ExpUnitRecSrc) VALUES(%s, %s) ON CONFLICT (ExpUnitHashKey, ExpUnitTimestamp, ExpUnitRecSrc) DO NOTHING;"
                                    tmp = [(GetHash("Subject: " + file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]))]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "HubSubject"
                                    insert_sql = "INSERT INTO HubSubject(SubjectHashKey, SubjectRecSrc, SubjectName) VALUES(%s, %s, %s) ON CONFLICT (SubjectHashKey, SubjectTimestamp, SubjectRecSrc) DO UPDATE SET SubjectName = EXCLUDED.SubjectName;"
                                    tmp = [(GetHash("Subject: " + file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            "Subject: " + file[:file.find('-')])]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "SatSubjectName"
                                    insert_sql = "INSERT INTO SatSubjectName(SbjNameHashKey, SbjNameRecSrc, SbjName) VALUES(%s, %s, %s) ON CONFLICT (SbjNameHashKey, SbjNameTimestamp, SbjNameRecSrc) DO NOTHING;"
                                    tmp = [(GetHash("Subject: " + file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            "Subject: " + file[:file.find('-')])]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "SatSubjectAge"
                                    insert_sql = "INSERT INTO SatSubjectAge(AgeHashKey, AgeRecSrc, Age) VALUES(%s, %s, %s) ON CONFLICT (AgeHashKey, AgeTimestamp, AgeRecSrc) DO NOTHING;"
                                    tmp = [(GetHash("Subject: " + file[:file.find('-')]),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            -1)]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "ParticipatesIn"
                                    insert_sql = "INSERT INTO ParticipatesIn(ParticipatesInHashKey, ParticipatesInRecSrc, ExperimentalUnit, ExperimentID) VALUES(%s, %s, %s, %s) ON CONFLICT (ParticipatesInHashKey, ParticipatesInTimestamp, ParticipatesInRecSrc) DO NOTHING;"
                                    tmp = [(GetHash("Subject: " + file[:file.find('-')] + "PreAutism"),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            GetHash("Subject: " + file[:file.find('-')]),
                                            GetHash("PreAutism"))]
                                    curs.executemany(insert_sql, tmp)

                                    # insert data into table "SatExperimentUnitIdentifier"
                                    insert_sql = "INSERT INTO SatExperimentUnitIdentifier(UnitIDHashKey, UnitIDRecSrc, ID) VALUES(%s, %s, %s) ON CONFLICT (UnitIDHashKey, UnitIDTimestamp, UnitIDRecSrc) DO NOTHING;"
                                    tmp = [(GetHash("Subject: " + file[:file.find('-')] + "PreAutism"),
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            "Sbj:" + file[:file.find('-')])]
                                    curs.executemany(insert_sql, tmp)

                                # insert data into table "AssignedTo"
                                insert_sql = "INSERT INTO AssignedTo(AssignedToHashKey, AssignedToRecSrc, ExperimentalUnit, GroupID) VALUES(%s, %s, %s, %s) ON CONFLICT (AssignedToHashKey, AssignedToTimestamp, AssignedToRecSrc) DO NOTHING;"
                                tmp = [(GetHash(
                                    "Subject: " + file[:file.find('-')] + file[file.find('_') + 1:file.rfind('C')]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash("Subject: " + file[:file.find('-')]),
                                        GetHash(file[file.find('_') + 1:file.rfind('C')]))]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "AttendsSession"
                                insert_sql = "INSERT INTO AttendsSession(AttendHashKey, AttendRecSrc, ExperimentalUnit, GroupID, SessionID) VALUES(%s, %s, %s, %s, %s) ON CONFLICT (AttendHashKey, AttendTimestamp, AttendRecSrc) DO NOTHING;"
                                tmp = [(GetHash(
                                    "Subject: " + file[:file.find('-')] + file[:file.find('-')] + file[file.find(
                                        '_') + 1:file.rfind('C')]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash("Subject: " + file[:file.find('-')]),
                                        GetHash(file[file.find('_') + 1:file.rfind('C')]),
                                        GetHash(file[:file.find('-')]))]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "HubObservation"
                                insert_sql = "INSERT INTO HubObservation(ObservationHashKey, ObservationRecSrc, CollectedAtSession) VALUES(%s, %s, %s) ON CONFLICT (ObservationHashKey, ObservationTimestamp, ObservationRecSrc) DO UPDATE SET CollectedAtSession=EXCLUDED.CollectedAtSession;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash(file[:file.find('-')]))]
                                curs.executemany(insert_sql, tmp)

                                dathk = GetHash(file[file.find('\\') + 1:])

                                # insert data into table "ObservationGroup"
                                insert_sql = "INSERT INTO ObservationGroup(ObvGrpHashKey, ObvGrpRecSrc, ObservationID, GroupID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObvGrpHashKey, ObvGrpTimestamp, ObvGrpRecSrc) DO UPDATE SET ObservationID=EXCLUDED.ObservationID,GroupID=EXCLUDED.GroupID;"
                                tmp = [(GetHash(
                                    file[file.find('\\') + 1:] + file[file.find('_') + 1:file.rfind('C')]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash(file[file.find('\\') + 1:]),
                                        GetHash(file[file.find('_') + 1:file.rfind('C')]))]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "SatObservationName"
                                insert_sql = "INSERT INTO SatObservationName(ObvNameHashKey, ObvNameRecSrc, ObvName) VALUES(%s, %s, %s) ON CONFLICT (ObvNameHashKey, ObvNameTimestamp, ObvNameRecSrc) DO UPDATE SET ObvName=EXCLUDED.ObvName;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        file[file.find('\\') + 1:])]
                                curs.executemany(insert_sql, tmp)

                                obv_value = pd.read_csv(f, sep=" ", header=None)

                                tmp = []

                                for col in obv_value:
                                    tmp.append(
                                        lst2pgarr(numlst2strlst(obv_value[col].tolist())))

                                pg_arr = lst2pgarr(tmp)

                                timestamps = lst2pgarr(numlst2strlst(obv_value.index.tolist()))

                                # insert data into table "SatObservationValue"
                                insert_sql = "INSERT INTO SatObservationValue(ValueNameHashKey, ValueNameRecSrc, ObvValue, Timestamps) VALUES(%s, %s, %s, %s) ON CONFLICT (ValueNameHashKey, ValueNameTimestamp, ValueNameRecSrc) DO UPDATE SET ObvValue=EXCLUDED.ObvValue,Timestamps=EXCLUDED.Timestamps;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        pg_arr,
                                        timestamps)]
                                curs.executemany(insert_sql, tmp)

                        if file.endswith(".wl1") or file.endswith(".wl2"):
                            with open(filepath + "\\" + file, encoding='gbk', errors='ignore') as f:
                                print(file)

                                # insert data into table "HubObservation"
                                insert_sql = "INSERT INTO HubObservation(ObservationHashKey, ObservationRecSrc, CollectedAtSession) VALUES(%s, %s, %s) ON CONFLICT (ObservationHashKey, ObservationTimestamp, ObservationRecSrc) DO UPDATE SET CollectedAtSession=EXCLUDED.CollectedAtSession;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash(file[:file.find('-')]))]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "ObservationGroup"
                                insert_sql = "INSERT INTO ObservationGroup(ObvGrpHashKey, ObvGrpRecSrc, ObservationID, GroupID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObvGrpHashKey, ObvGrpTimestamp, ObvGrpRecSrc) DO UPDATE SET ObservationID=EXCLUDED.ObservationID,GroupID=EXCLUDED.GroupID;"
                                tmp = [(GetHash(
                                    file[file.find('\\') + 1:] + file[file.find('_') + 1:file.rfind('C')]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash(file[file.find('\\') + 1:]),
                                        GetHash(file[file.find('_') + 1:file.rfind('C')]))]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "SatObservationName"
                                insert_sql = "INSERT INTO SatObservationName(ObvNameHashKey, ObvNameRecSrc, ObvName) VALUES(%s, %s, %s) ON CONFLICT (ObvNameHashKey, ObvNameTimestamp, ObvNameRecSrc) DO UPDATE SET ObvName=EXCLUDED.ObvName;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        file[file.find('\\') + 1:])]
                                curs.executemany(insert_sql, tmp)

                                # insert data into table "ObservationMetadata"
                                insert_sql = "INSERT INTO ObservationMetadata(ObservationMDHashKey, ObservationMDRecSrc, ObservationID, MetadataID) VALUES(%s, %s, %s, %s) ON CONFLICT (ObservationMDHashKey, ObservationMDTimestamp, ObservationMDRecSrc) DO UPDATE SET ObservationID=EXCLUDED.ObservationID,MetadataID=EXCLUDED.MetadataID;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]) + hdrhk,
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        GetHash(file[file.find('\\') + 1:]),
                                        hdrhk)]
                                curs.executemany(insert_sql, tmp)

                                if evthk != "Empty .evt File":
                                    tmp = [(GetHash(file[file.find('\\') + 1:]) + evthk,
                                            GetHash(filepath[filepath.rfind('\\') + 1:]),
                                            GetHash(file[file.find('\\') + 1:]),
                                            evthk)]
                                    curs.executemany(insert_sql, tmp)

                                obv_value = pd.read_csv(f, sep=" ", header=None)

                                tmp = []

                                for col in obv_value:
                                    tmp.append(
                                        lst2pgarr(numlst2strlst(obv_value[col].tolist())))

                                pg_arr = lst2pgarr(tmp)

                                timestamps = lst2pgarr(numlst2strlst(obv_value.index.tolist()))

                                # insert data into table "SatObservationValue"
                                insert_sql = "INSERT INTO SatObservationValue(ValueNameHashKey, ValueNameRecSrc, ObvValue, Timestamps) VALUES(%s, %s, %s, %s) ON CONFLICT (ValueNameHashKey, ValueNameTimestamp, ValueNameRecSrc) DO UPDATE SET ObvValue=EXCLUDED.ObvValue,Timestamps=EXCLUDED.Timestamps;"
                                tmp = [(GetHash(file[file.find('\\') + 1:]),
                                        GetHash(filepath[filepath.rfind('\\') + 1:]),
                                        pg_arr,
                                        timestamps)]
                                curs.executemany(insert_sql, tmp)

    # submit transaction to database
    conn.commit()
    return


if __name__ == '__main__':
    conn = psycopg2.connect(database="smdvault", user="smd", password="smd2022", host="127.0.0.1",
                            port="5432")
    curs = conn.cursor()
    print("Connected to smdvault!!!")

    # insert data into table "HubExperiment"
    insert_sql = "INSERT INTO HubExperiment(ExperimentHashKey, ExperimentRecSrc) VALUES(%s, %s) ON CONFLICT (ExperimentHashKey) DO NOTHING;"
    tmp = [(GetHash("VM"), GetHash("VMData_Blinded"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("PreAutism"), GetHash("PreAutismData_Blinded"))]
    curs.executemany(insert_sql, tmp)

    # insert data into table "HubFactor"
    insert_sql = "INSERT INTO HubFactor(FactorHashKey, FactorRecSrc, Experiment, IsCofactor) VALUES(%s, %s, %s, %s) ON CONFLICT (FactorHashKey) DO UPDATE SET Experiment = EXCLUDED.Experiment, IsCofactor = EXCLUDED.IsCofactor;"
    tmp = [(GetHash("Visual Stimulus"), GetHash("Factor: Visual Stimulus (in VM)"),
            GetHash("VM"), True)]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Motor Stimulus"), GetHash("Factor: Motor Stimulus (in VM)"),
            GetHash("VM"), True)]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Normal/Stressed"), GetHash("Factor: Normal/Stressed (in PreAutism)"),
            GetHash("PreAutism"), True)]
    curs.executemany(insert_sql, tmp)

    # insert data into table "HubTreatment"
    insert_sql = "INSERT INTO HubTreatment(TreatmentHashKey, TreatmentRecSrc, Experiment) VALUES(%s, %s, %s) ON CONFLICT (TreatmentHashKey) DO UPDATE SET Experiment = EXCLUDED.Experiment;"
    tmp = [(GetHash("VS + MS"), GetHash("Treatment: Visual Stimulus + Motor Stimulus (in VM)"),
            GetHash("VM"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("N/S"), GetHash("Treatment: Normal/Stressed (in PreAutism)"),
            GetHash("PreAutism"))]
    curs.executemany(insert_sql, tmp)

    # insert data into table "HubGroup"
    insert_sql = "INSERT INTO HubGroup(GroupHashKey, GroupRecSrc, Treatment) VALUES(%s, %s, %s) ON CONFLICT (GroupHashKey) DO UPDATE SET Treatment = EXCLUDED.Treatment;"
    tmp = [(GetHash("Moto"), GetHash("Moto Group"),
            GetHash("VS + MS"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Rest"), GetHash("Rest Group"),
            GetHash("VS + MS"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Viso"), GetHash("Viso Group"),
            GetHash("VS + MS"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("ViMo"), GetHash("ViMo Group"),
            GetHash("VS + MS"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Normal"), GetHash("Normal Group"),
            GetHash("N/S"))]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Stressed"), GetHash("Stressed Group"),
            GetHash("N/S"))]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatFactorName"
    insert_sql = "INSERT INTO SatFactorName(FctNameHashKey, FctNameRecSrc, FctName) VALUES(%s, %s, %s);"
    tmp = [(GetHash("Visual Stimulus"), GetHash("VM FactorName"),
            "Visual Stimulus")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Motor Stimulus"), GetHash("VM FactorName"),
            "Motor Stimulus")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Normal/Stressed"), GetHash("PreAutism FactorName"),
            "Normal/Stressed")]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatTreatmentName"
    insert_sql = "INSERT INTO SatTreatmentName(TreatNameHashKey, TreatNameRecSrc, TreatName) VALUES(%s, %s, %s);"
    tmp = [(GetHash("VS + MS"), GetHash("VM TreatmentName"),
            "[Visual Stimulus, Motor Stimulus]")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("N/S"), GetHash("PreAutism TreatmentName"),
            "Normal/Stressed")]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatFactorLevel"
    insert_sql = "INSERT INTO SatFactorLevel(LevelHashKey, LevelRecSrc, LevelValue) VALUES(%s, %s, %s);"
    tmp = [(GetHash("Visual Stimulus"), GetHash("Factor Level VS Value: Present"),
            "Present")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Visual Stimulus"), GetHash("Factor Level VS Value: Not Present"),
            "Not Present")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Motor Stimulus"), GetHash("Factor Level MS Value: Present"),
            "Present")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Motor Stimulus"), GetHash("Factor Level MS Value: Not Present"),
            "Not Present")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Normal/Stressed"), GetHash("Factor Level N/S Value: Normal"),
            "Normal")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Normal/Stressed"), GetHash("Factor Level N/S Value: Stressed"),
            "Stressed")]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatTreatmentFactorLevel"
    insert_sql = "INSERT INTO SatTreatmentFactorLevel(TreatLevelHashKey, TreatLevelRecSrc, TreatLevelValue) VALUES(%s, %s, %s);"
    tmp = [(GetHash("VS + MS"), GetHash("Treatment Factor Level VS + MS Value: Moto"),
            "Moto")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("VS + MS"), GetHash("Treatment Factor Level VS + MS Value: Rest"),
            "Rest")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("VS + MS"), GetHash("Treatment Factor Level VS + MS Value: ViMo"),
            "ViMo")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("VS + MS"), GetHash("Treatment Factor Level VS + MS Value: Viso"),
            "Viso")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("N/S"), GetHash("Treatment Factor Level N/S Value: Normal"),
            "Normal")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("N/S"), GetHash("Treatment Factor Level N/S Value: Stressed"),
            "Stressed")]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatGroupName"
    insert_sql = "INSERT INTO SatGroupName(GrpNameHashKey, GrpNameRecSrc, GrpName) VALUES(%s, %s, %s);"
    tmp = [(GetHash("Moto"),
            GetHash("Moto Group"),
            "Moto Group")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Rest"),
            GetHash("Rest Group"),
            "Rest Group")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Viso"),
            GetHash("Viso Group"),
            "Viso Group")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("ViMo"),
            GetHash("ViMo Group"),
            "ViMo Group")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Normal"),
            GetHash("Normal Group"),
            "Normal Group")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("Stressed"),
            GetHash("Stressed Group"),
            "Stressed Group")]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatExperimentTitle"
    insert_sql = "INSERT INTO SatExperimentTitle(TitleHashKey, TitleRecSrc, Title) VALUES(%s, %s, %s) ON CONFLICT (TitleHashKey, TitleTimestamp, TitleRecSrc) DO UPDATE SET Title=EXCLUDED.Title;"
    tmp = [(GetHash("VM"),
            GetHash("VMData_Blinded"),
            "Visuomotor functional connectivity")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("PreAutism"),
            GetHash("PreAutismData_Blinded"),
            "Pre-autism")]
    curs.executemany(insert_sql, tmp)

    # insert data into table "SatExperimentAcronym"
    insert_sql = "INSERT INTO SatExperimentAcronym(AcronymHashKey, AcronymRecSrc, Acronym) VALUES(%s, %s, %s) ON CONFLICT (AcronymHashKey, AcronymTimestamp, AcronymRecSrc) DO UPDATE SET Acronym=EXCLUDED.Acronym;"
    tmp = [(GetHash("VM"),
            GetHash("VMData_Blinded"),
            "VM")]
    curs.executemany(insert_sql, tmp)

    tmp = [(GetHash("PreAutism"),
            GetHash("PreAutismData_Blinded"),
            "PreAutism")]
    curs.executemany(insert_sql, tmp)

    ReadLoadMetadata1("..\\data\\VMData")
    ReadLoadData1("..\\data\\VMData")

    ReadLoadData2("..\\data\\PreAutismData")

    # submit transaction to database
    # conn.commit()

    curs.close()
    conn.close()
