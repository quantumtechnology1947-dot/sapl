

from django.db import models



class GroupingEvents(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    subject = models.TextField(db_column='Subject', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    start = models.DateTimeField(db_column='Start', blank=True, null=True)  # Field name made lowercase.
    end = models.DateTimeField(db_column='End', blank=True, null=True)  # Field name made lowercase.
    moduleid = models.IntegerField(db_column='ModuleId', blank=True, null=True)  # Field name made lowercase.
    recurrencerule = models.TextField(db_column='RecurrenceRule', blank=True, null=True)  # Field name made lowercase.
    recurrenceparentid = models.IntegerField(db_column='RecurrenceParentId', blank=True, null=True)  # Field name made lowercase.
    reminder = models.TextField(db_column='Reminder', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Grouping_Events'


class GroupingRooms(models.Model):
    moduleid = models.AutoField(db_column='ModuleId', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Grouping_Rooms'


class Message(models.Model):
    messageid = models.AutoField(db_column='MessageID', primary_key=True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID')  # Field name made lowercase.
    touserid = models.IntegerField(db_column='ToUserID', blank=True, null=True)  # Field name made lowercase.
    text = models.TextField(db_column='Text')  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='TimeStamp')  # Field name made lowercase.
    color = models.TextField(db_column='Color', blank=True, null=True)  # Field name made lowercase.
    roomid = models.ForeignKey('Room', models.DO_NOTHING, db_column='RoomID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Message'


class Privatemessage(models.Model):
    privatemessageid = models.AutoField(db_column='PrivateMessageID', primary_key=True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID')  # Field name made lowercase.
    touserid = models.IntegerField(db_column='ToUserID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PrivateMessage'


class Room(models.Model):
    roomid = models.AutoField(db_column='RoomID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Room'

