from sqloxide import parse_sql
import unittest
import pytest


sql = """
CREATE PROCEDURE foo (@CustomerName NVARCHAR(50)) AS BEGIN SELECT * FROM DEV END;
CREATE OR ALTER PROCEDURE foo AS BEGIN SELECT 1 END;
CREATE PROCEDURE foo AS BEGIN SELECT 1 END;
CREATE PROCEDURE foo AS BEGIN SELECT [myColumn] FROM [myschema].[mytable] END;
CREATE PROCEDURE foo (@CustomerName NVARCHAR(50)) AS BEGIN SELECT * FROM DEV END;
CREATE PROCEDURE [foo] AS BEGIN UPDATE bar SET col = 'test' END;
CREATE PROCEDURE [foo] AS BEGIN SELECT [foo], CASE WHEN [foo] IS NULL THEN 'empty' ELSE 'notempty' END AS [foo] END;
CREATE PROCEDURE [foo] AS BEGIN UPDATE bar SET col = 'test'; SELECT [foo] FROM BAR WHERE [FOO] > 10 END;
"""


class MSSQLTest(unittest.TestCase):
    def test0(self):
        results = parse_sql(sql=sql, dialect='mssql')
        assert isinstance(results[0], dict)
        assert isinstance(results[0].get('CreateProcedure'), dict)

    def test1(self):
        results = parse_sql(sql=sql, dialect='mssql')
        self.assertIsNotNone(results[0].get('CreateProcedure'))

    def test2(self):
        results = parse_sql(sql=sql, dialect='mssql')
        self.assertEqual('foo',results[0].get('CreateProcedure')['name'][0]['value'])

    def test3(self):
        sql = """
                CREATE PROCEDURE HumanResources.uspGetEmployeesTest2 (  
                    @LastName nvarchar(50),   
                    @FirstName nvarchar(50)
                    )
                AS
                BEGIN
                    -- SET NOCOUNT ON;  
                    SELECT FirstName, LastName, Department  
                    FROM HumanResources.vEmployeeDepartmentHistory  
                    WHERE FirstName = @FirstName AND LastName = @LastName  
                    AND EndDate IS NULL;
                END
                """
        results = parse_sql(sql=sql, dialect='mssql')
        assert isinstance(results[0], dict)
        assert isinstance(results[0].get('CreateProcedure'), dict)

    @pytest.mark.skip(reason="WHITE() not supported by parser")
    def testWhile(self):
        sql = """
            CREATE PROCEDURE Usp_samplestoredprocedure (@MinPriceCondition MONEY, 
                                                        @MaxPriceCondition MONEY) 
            AS 
            BEGIN 
                WHILE (SELECT Avg(salesamount) FROM   dbo.factinternetsales) < @MinPriceCondition 
                    BEGIN 
                        UPDATE dbo.factinternetsales 
                        SET    salesamount = salesamount * 2 
                        SELECT Max(salesamount) 
                        FROM   dbo.factinternetsales 
                        IF (SELECT Max(salesamount) 
                            FROM   dbo.factinternetsales) > @MaxPriceCondition 
                        BREAK 
                    END 
            END
            """
        results = parse_sql(sql=sql, dialect='mssql')
        assert isinstance(results[0], dict)
        assert isinstance(results[0].get('CreateProcedure'), dict)

    @pytest.mark.skip(reason="IF() not supported by parser")
    def testTempTable(self):
        sql = """
            IF OBJECT_ID('tempdb..#stats_ddl') IS NOT NULL
            BEGIN
                DROP TABLE #stats_ddl
            END;
            CREATE TABLE #temp_table
            (
                [schema_name]           NVARCHAR(128) NOT NULL
            ,    [table_name]            NVARCHAR(128) NOT NULL
            ,    [stats_name]            NVARCHAR(128) NOT NULL
            );"""
        results = parse_sql(sql=sql, dialect='mssql')
        assert isinstance(results[0], dict)
        assert isinstance(results[0].get('CreateTable'), dict)
    
    @pytest.mark.skip(reason="HASH() not supported by parser")
    def testTablePartitionStrategy(self):
        sql = """
            CREATE TABLE #temp_table
            (
                [schema_name]           NVARCHAR(128) NOT NULL
            ,    [table_name]            NVARCHAR(128) NOT NULL
            ,    [stats_name]            NVARCHAR(128) NOT NULL
            )
            WITH
            (
                DISTRIBUTION = HASH([seq_nmbr])
            ,    HEAP
            );"""
        results = parse_sql(sql=sql, dialect='mssql')
        assert isinstance(results[0], dict)
        assert isinstance(results[0].get('CreateTable'), dict)

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([sys.argv[0]]))