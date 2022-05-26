import sqlite3
from time import time
from datetime import datetime

class dbQuery():
    def __init__(self, db, mdb):
        self.db = db
        self.mdb = mdb
    
    #: Add the user into the database if not registered
    def setUser(self, userId):
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        isRegistered = cur.execute(f'SELECT * FROM users WHERE userId={userId}').fetchone()
        con.commit()

        isRegistered = bool(isRegistered)

        if not isRegistered:
            cur.execute(
                f"""Insert into users (userId, date) values ({userId}, "{datetime.now().strftime('%Y-%m-%d')}")"""
            )

            cur.execute(f'Insert into settings (ownerId) values ({userId})')
            cur.execute(f'Insert into flood (ownerId) values ({userId})')
            con.commit()

        return isRegistered

    #: Get all the registered users
    def getAllUsers(self):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()

        users = cur.execute('SELECT userId FROM users').fetchall()
        con.commit()

        return users or None

    #: Get all user's with GitHub oauth
    def getAllGhUsers(self):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()

        users = cur.execute(
            'SELECT DISTINCT settings.ownerId FROM settings INNER JOIN accounts ON accounts.id = settings.defaultAcId WHERE githubId != 0 and accounts.invitesRemaining != 0'
        ).fetchall()

        con.commit()

        return users or None
    
    #: Get all the users with date
    def getAllUsersDate(self):
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        users = cur.execute('SELECT * FROM users').fetchall()
        con.commit()

        return users or None

    #: Get users of particular language
    def getUsers(self, language):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()

        users = cur.execute(f'SELECT ownerId FROM settings WHERE language="{language}"').fetchall()
        con.commit()

        return users or None
    
    #: Get all users exclude certain languages
    #: languages must be of list type
    def getUsersExcept(self, languages):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()

        users = cur.execute('SELECT * FROM users WHERE userId NOT NULL').fetchall()
        con.commit()

        for language in languages:
            users = [item for item in users if item not in self.getUsers(language)] if self.getUsers(language) else users

        return users or None
    
    #: Get the user's settings
    def getSetting(self, userId, var, table='settings'):
        self.setUser(userId)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        
        setting = cur.execute(f'SELECT {var} FROM {table} WHERE ownerId={userId} limit 1').fetchone()
        con.commit()

        return setting[0] if setting else None

    #: Set the user's settings    
    def setSetting(self, userId, var, value, table='settings'):
        self.setUser(userId)
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        #!? If value is None, put value as NULL else "{string}"
        value = f'"{value}"' if value else 'NULL'
        cur.execute(f'INSERT OR IGNORE INTO {table} (ownerId, {var}) VALUES ({userId}, {value})')
        cur.execute(f'UPDATE {table} SET {var}={value} WHERE ownerId={userId}')
        con.commit()

    #: Add account in the user's accounts table
    def setAccount(self, userId, accountId, userName, token, deviceCode, isPremium, invitesRemaining):
        self.setUser(userId)
        con = sqlite3.connect(self.db)
        cursor = con.cursor()

        #!? If the seedrId not on the table, insert new
        if (
            cursor.execute(
                f'SELECT * FROM accounts WHERE ownerId={userId} AND accountId="{accountId}"'
            ).fetchone()
            is None
        ):
            id = cursor.execute(f'INSERT INTO accounts (accountId, ownerId, userName, token, deviceCode, isPremium, invitesRemaining, timestamp) VALUES ({accountId},{userId},"{userName}","{token}","{deviceCode}",{isPremium},{invitesRemaining},{int(time())})').lastrowid
        else:
            cursor.execute(f'UPDATE accounts SET token="{token}", deviceCode="{deviceCode}", isPremium={isPremium}, invitesRemaining={invitesRemaining}, timestamp={int(time())} WHERE ownerId={userId} AND accountId={accountId}')
            id = cursor.execute(f'SELECT id FROM accounts WHERE ownerID={userId} AND accountId="{accountId}"').fetchone()[0]
        con.commit()

        #!? Set the added account as the default account
        self.setDefaultAc(userId, id)
    
    #: Delete a user's account
    def deleteAccount(self, userId, accountId):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        defaultAcId = self.getSetting(userId, 'defaultAcId')
        cur.execute(f'DELETE FROM accounts WHERE ownerId={userId} AND id={accountId}')
        con.commit()

        #!? If the deleted account is the default account, set another account as a default account
        if str(accountId) == str(defaultAcId):
            if accounts := self.getAccounts(userId):
                lastAccountId = accounts[-1]['id']
                self.setSetting(userId, 'defaultAcId', lastAccountId)

            else:
                self.setSetting(userId, 'defaultAcId', None)

    #: Gel all accounts of certain user
    def getAccounts(self, userId):
        con = sqlite3.connect(self.db)
        con.row_factory = dict_factory
        cur = con.cursor()
        accounts = cur.execute(f'SELECT * FROM accounts WHERE ownerId={userId}').fetchall()
        con.commit()

        return accounts or None

    #: Gel certain account of a user
    def getAccount(self, userId, accountId):
        con = sqlite3.connect(self.db)
        con.row_factory = dict_factory
        cur = con.cursor()
        accounts = cur.execute(f'SELECT * FROM accounts WHERE ownerId={userId} and id={accountId}').fetchone()
        con.commit()

        return accounts or None

    #: Get the default account of the user
    def getDefaultAc(self, userId):
        con = sqlite3.connect(self.db)
        con.row_factory = dict_factory
        cur = con.cursor()
        if defaultAcId := self.getSetting(userId, 'defaultAcId'):
            account = cur.execute(f'SELECT * FROM accounts WHERE ownerId={userId} AND id={defaultAcId}').fetchone()
            con.commit()

            return account
        else:
            return None

    #: Set a user's default account
    def setDefaultAc(self, userId, accountId):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        cur.execute(f'INSERT OR IGNORE INTO settings (ownerId, defaultAcId) VALUES ({userId}, {accountId})')
        cur.execute(f'UPDATE settings SET defaultAcId={accountId} WHERE ownerId={userId}')
        con.commit()

    
    #: Get the magnet link from the database
    def getMagnet(self, key):
        con = sqlite3.connect(self.mdb)
        cur = con.cursor()
        
        magnetLink = cur.execute(f'SELECT magnetLink FROM data WHERE key="{key}"').fetchone()
        con.commit()

        return magnetLink[0] if magnetLink else None

#: Return query as dictionary
#! https://stackoverflow.com/a/3300514/13987868
def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}