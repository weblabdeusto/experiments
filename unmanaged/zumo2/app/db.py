from pymongo import MongoClient
import json
from datetime import datetime
try:
    from config import basedir
    from config import DB_URI
except:
    import os
    DB_URI = 'localhost'
    basedir = os.path.abspath(os.path.dirname(__file__)).split('/app/')[0]


class dbManager(object):
    def __init__(self):
        self.client = MongoClient(DB_URI)


    def getCompetitionsFromFile(self):
        data_file = open(basedir + '/competitions.json')
        return json.load(data_file)

    def startDB(self):
        try:

            if 'ardulab_db' not in self.client.database_names():
                db = self.client.ardulab_db
                competitions = db.competitions
                competitions.insert(self.getCompetitionsFromFile()['competitions'])
                return True, 'DB created'
            else:
                db = self.client.ardulab_db
                if 'competitions' not in db.collection_names():
                    competitions = db.competitions
                    competitions.insert(self.getCompetitionsFromFile()['competitions'])
                    return True, 'Collection created'
                else:
                    return False, 'Collection already exists'
        except:
            return False, 'Error creating database'

    def reloadFromFile(self):
        self.client.drop_database("ardulab_db")
        return self.startDB()

    def getCompetitions(self):
        try:
            if 'ardulab_db' not in self.client.database_names():
                return False, []
            db = self.client.ardulab_db
            if 'competitions' not in db.collection_names():
                return False, []
            competitions = db.competitions.find({})
            return True, competitions
        except:
            return False, []

    def canJoin(self,user_name,competition_name):
        user_competitions = self.getUserCompetitions(user_name)
        if competition_name in user_competitions:
            return False
        expired = self.getExpiredCompetitions()
        if competition_name in expired:
            return False
        return True


    def getCompetitionNames(self):
        success, competitions = self.getCompetitions()
        names = []
        for competition in competitions:
            names.append(competition['name'])
        return names

    def getCompetitionInfo(self,name):
        info = self.client.ardulab_db.competitions.find_one({'name':name},{"_id":0,"name":1,"group":1,"circuit":1,"start_time":1,"end_time":1})
        return info

    def getCompetitionRanking(self, competition_id):

        pipeline = [
            {"$match": {"name": competition_id}},
            {"$project": {"users.username": 1, "_id": 0, "users.uses.time": 1}},
            {"$unwind": "$users"}, {"$unwind": "$users.uses"},
            {"$sort": {"users.uses.time": 1}}
        ]

        result = list(self.client.ardulab_db.competitions.aggregate(pipeline))

        ranking_names = []
        ranking_times = []

        for element in result:
            if element['users']['username'] not in ranking_names:
                ranking_names.append(element['users']['username'])
                ranking_times.append(element['users']['uses']['time'])

        return ranking_names, ranking_times

    def getCompetitionUsernames(self, competition_id):

        user_names = []
        competition = self.client.ardulab_db.competitions.find_one({'name':competition_id})

        for users in  competition['users']:
            user_names.append(users['username'])

        return user_names

    def printCompetitionRanking(self, competition_id):
        ranking = self.getCompetitionRanking(competition_id)
        for i in range(1,len(ranking[0])+1):
            print '{}.\t{}\t\t\t(Lap time: {} seconds)'.format(i,ranking[0][i-1],ranking[1][i-1])

    def getUserTimes(self, competition_id, username):

        pipeline = [
            {"$match": {"name": competition_id}},
            {"$project": {"users.username": 1, "_id": 0, "users.uses.time": 1, "users.uses.date":1}},
            {"$unwind": "$users"},
            {"$unwind": "$users.uses"},
            {"$match": {"users.username": username}},
            {"$sort": {"users.uses.date": -1}}
        ]

        lap_times = []
        lap_dates = []
        result = list(self.client.ardulab_db.competitions.aggregate(pipeline))

        for element in result:
            lap_times.append(element["users"]["uses"]["time"])
            lap_dates.append(element["users"]["uses"]["date"])

        return lap_times,lap_dates

    def printUserTimes(self, competition_id, username):
        result = self.getUserTimes(competition_id,username)
        for i in range(1,len(result[0])+1):
            print 'Lap time: {}\t\t\tDate: {}'.format(result[0][i-1],result[1][i-1])

    def getUserCompetitions(self, username):

        pipeline = [
            {"$match": {"users.username": username}},
            {"$project": {"name": 1, "_id": 0}}
        ]

        response = list(self.client.ardulab_db.competitions.aggregate(pipeline))

        competitions = []
        for element in response:
            competitions.append(element["name"])

        return competitions

    def getActiveCompetitions(self):

        result = list(self.client.ardulab_db.competitions.find({"end_time":{"$gte": datetime.now().isoformat()}},{"name":1,"_id":0}))
        actives = []
        for element in result:
            actives.append(element["name"])
        return sorted(actives)

    def getCompetitionPassword(self, competition):
        result = self.client.ardulab_db.competitions.find_one({"name":competition},{"name":1,"password":1,"_id":0})
        return result["password"]

    def getExpiredCompetitions(self):

        result = list(self.client.ardulab_db.competitions.find({"end_time":{"$lt": datetime.now().isoformat()}},{"name":1,"_id":0}))
        expired = []
        for element in result:
            expired.append(element["name"])
        return sorted(expired)

    def getPrivateCompetitions(self):
        private = []
        result = list(self.client.ardulab_db.competitions.find({"private":True},{"name":1,"_id":0}))
        for element in result:
            private.append(element["name"])
        return private

    def addUserToCompetition(self, username, competition):

        try:
            response = list(self.client.ardulab_db.competitions.find({"name": competition}, {"name": 1, "_id": 0}))
            if len(response)==0:
                return False, "Competition doesn't exists"
            response = list(self.client.ardulab_db.competitions.find({"name": competition,"users.username": username }, {"name": 1, "_id": 0}))
            if len(response)>0:
                return False, "User already registered in the competition"
            self.client.ardulab_db.competitions.update_one(
                {"name": competition},
                {"$addToSet": {
                    "users": {
                        "username": username,
                        "uses": []
                    }
                }}
            )
            return True, "Success registering user"
        except:
            return False, "Unexpected error"

    def addUserTime(self, username, time, circuit):

        active = self.getActiveCompetitions()
        competitions = self.getUserCompetitions(username)
        for comp in competitions:
            if comp in active:
                self.client.ardulab_db.competitions.update_one({"name": comp,
                                                                "circuit": circuit,
                                                                "users.username": username
                                                           },
                                                           {"$push": {
                                                              "users.$.uses": {
                                                                  "date": datetime.now().isoformat(),
                                                                  "time": time
                                                              }
                                                           }})


    def deleteUserFromCompetition(self, username, competition):
        pass
