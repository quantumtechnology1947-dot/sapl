# Generated migration for BOM temp table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS tblDG_BOMItem_Temp (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                CompId INTEGER,
                SessionId VARCHAR(50),
                WONo TEXT,
                ItemId INTEGER,
                Qty REAL,
                ChildId INTEGER,
                PartNo TEXT,
                ManfDesc TEXT,
                UOMBasic INTEGER,
                FOREIGN KEY (ItemId) REFERENCES tblDG_Item_Master(Id)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS tblDG_BOMItem_Temp;"
        ),
    ]
